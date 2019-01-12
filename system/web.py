#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPiHTTPServer import RPiHTTPRequestHandler
from shutil import copyfile
import netifaces as ni
import socket
import time
import os
import json
import pystache

# class handling web requests
class WebHandler(RPiHTTPRequestHandler):

  # init template vars as first thing
  def pre_handle_request(self):
    self.tpl_vars = {}
    if "APP_NAME" in self.server.config:
      self.tpl_vars["TITLE"] = self.server.config["APP_NAME"]
    else:  
      self.tpl_vars["TITLE"] = "RPi Camera control"

  # get current ip address of the machine on the first available configured interface
  def my_ip(self):
    ip = None

    ifaces = self.server.config["NETWORK_INTERFACE"]
    for iface in ifaces:
      try:
        ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
      except:
        pass
      if ip:
        break

    # call gethostbyname if not able to get IP from interfaces
    if not ip:
      ip = socket.gethostname()

    return ip

  # GET /
  def default_response(self):
    # replace ip in webcam url if required
    if "%s" in self.server.config["CAMERA_URL"]:
      camera_url = self.server.config["CAMERA_URL"] % self.my_ip()
    else:
      camera_url = self.server.config["CAMERA_URL"]

    self.tpl_vars["CAMERA_URL"] = camera_url
    self.render_template()

  # GET /config
  def show_config(self):
    self.tpl_vars["WEB_CONFIG"] = json.dumps(self.config, indent = 4)
    self.tpl_vars["DRONE_CONFIG"] = json.dumps(self.server.drone.config, indent = 4)
    self.tpl_vars["SENSORS_CONFIG"] = json.dumps(self.server.sensors.config, indent = 4)
    self.render_template(template="config.html")

  # GET /sensor?id=sensor_id
  def get_sensor(self):
    sensor_id = self.qs["id"][0]
    if sensor_id in self.server.controller.sensors.config: 
      sensor = self.server.controller.sensors.get_sensor(sensor_id)
    else:
      sensor = {
        "id": sensor_id,
        "value": None,
        "reading": None,
        "unit": ""
      }
    self.content_type = "application/json"
    self.content = json.dumps(sensor)

  # POST /save_config
  def save_config(self):

    configs = [
      {
        "config": self.form["web-config"].value,
        "valid": None,
        "file": self.server.web_config_file
      },
      {
        "config": self.form["drone-config"].value,
        "valid": None,
        "file": self.server.drone_config_file
      },
      {
        "config": self.form["sensors-config"].value,
        "valid": None,
        "file": self.server.sensors_config_file
      }
    ]

    restart = False

    for config in configs:
      try:
        json.loads(config["config"])
        config["valid"] = True
      except ValueError:
        config["valid"] = False

      if config["valid"]:
        # make a backup of the old config file
        backup_file = os.path.join(os.path.dirname(config["file"]),"backup",os.path.basename(config["file"]) + "." + time.strftime("%Y-%m-%d_%H-%M-%S"))
        copyfile(config["file"], backup_file)
        # write new config
        f = open(config["file"],"w")
        f.write(config["config"])
        f.close()
        restart = True
    
    self.render_template(template="saveconfig.html")

    if restart:
      def post_serve_response():
        os.execl("/usr/sbin/service","xtcd","xtcd","restart")
      
      setattr(self,"post_serve_response",post_serve_response)

  # POST /switch
  def switch(self):
    index = int(self.form["pin"].value)
    self.server.controller.drone.switch(index)
    self.render_template()

  # POST /pwm_toggle
  def pwm_toggle(self):
    index = int(self.form["index"].value)
    self.server.controller.drone.pwm_toggle(index)
    self.render_template()

  # POST /up
  def up(self):
    self.server.controller.drone.up()
    self.render_template()

  # POST /down
  def down(self):
    self.server.controller.drone.down()
    self.render_template()

  # POST /left
  def left(self):
    self.server.controller.drone.left()
    self.render_template()

  # POST /right
  def right(self):
    self.server.controller.drone.right()
    self.render_template()

  # POST /center
  def center(self):
    self.server.controller.drone.center()
    self.render_template()

  # POST /forward
  def forward(self):
    self.server.controller.drone.forward("MOTOR_1")
    self.render_template()

  # POST /back
  def back(self):
    self.server.controller.drone.back("MOTOR_1")
    self.render_template()

  # POST /stop
  def stop(self):
    self.server.controller.drone.stop("MOTOR_1")
    self.render_template()

  # POST /speedup
  def speedup(self):
    self.server.controller.drone.speedup("MOTOR_1")
    self.render_template()

  # POST /slowdown
  def slowdown(self):
    self.server.controller.drone.slowdown("MOTOR_1")
    self.render_template()

  # POST /set_pwm
  def set_pwm(self):
    channel = int(self.form["channel"].value)
    value = int(self.form["value"].value)
    self.server.controller.drone.set_pwm(channel = channel, value = value)  
    self.render_template()

  # POST /switch_pwm
  def switch_pwm(self):
    channel = int(self.form["channel"].value)
    value_on = int(self.form["valueOn"].value)
    value_off = int(self.form["valueOff"].value)
    status = self.server.drone.status["PWM"][channel]

    if (status == None or status == value_off):
      self.server.controller.drone.set_pwm(channel = channel, value = value_on)
    else:
      self.server.controller.drone.set_pwm(channel = channel, value = value_off)

    self.render_template()

  # POST /sequence_pwm
  def sequence_pwm(self):
    params = self.form["params"].value
    sequence = params.split("|")
    for command in sequence:
      (channel,value,delay) = command.split(",") 
      self.server.controller.drone.set_pwm(channel = int(channel), value = int(value))
      time.sleep(int(delay)/1000.0)  
    self.render_template()

  def render_template(self, template="home.html"):

    self.tpl_vars.update(self.server.controller.drone.status)
    # self.tpl_vars.update(self.server.sensors.status)
    pwm = self.tpl_vars["PWM"]
    self.tpl_vars["PWM"] = dict([str(i),pwm[i]] for i in range(0,len(pwm)) if pwm[i] != None)
    
    self.tpl_vars["USER"] = self.user

    self.tpl_vars["IS_ADMIN"] = False
    self.tpl_vars["IS_OPERATOR"] = False

    if self.user == "admin":
      self.tpl_vars["IS_ADMIN"] = True
      self.tpl_vars["IS_OPERATOR"] = True

    if self.user == "operator":
      self.tpl_vars["IS_OPERATOR"] = True

    if self.request_xhr:
      self.content_type = "application/json"
      self.content = json.dumps(self.tpl_vars)
    else:
      tpl = os.path.join(self.config["TEMPLATE_FOLDER"], template)
      if os.path.isfile(tpl):
        tpl_content = open(tpl,"r").read()
        self.content = pystache.render(tpl_content, self.tpl_vars)
      else:
        self.give_404("Template file %s/%s missing" % (self.config["TEMPLATE_FOLDER"],template))

  # override default logging
  def log_message(self, format, *args):
    self.server.controller.log("%s %s" % (self.address_string(),format%args))        
