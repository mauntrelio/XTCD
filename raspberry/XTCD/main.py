#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPiHTTPServer import RPiHTTPServer, RPiHTTPRequestHandler
from drone import Drone
import netifaces as ni
import socket
import threading
import time
import pystache
import os
import json

class XTCDHandler(RPiHTTPRequestHandler):
  
  # GET /
  def default_response(self):
    tpl_vars = self.server.drone.status
    ip = None
    ifaces = self.server.config["NETWORK_INTERFACE"]
    for iface in ifaces:
      try:
        ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
      except:
        pass
      if ip:
        break

    if not ip:
      ip = socket.gethostname()    
    
    camera_url = self.server.config["CAMERA_URL"] % ip
    tpl_vars["CAMERA_URL"] = camera_url
    self.render_template(tpl_vars=tpl_vars)

  # GET /config
  def show_config(self):
    tpl_vars["WEB_CONFIG"] = json.dumps(self.config, indent = 4)
    tpl_vars["DRONE_CONFIG"] = json.dumps(self.server.drone.config, indent = 4)
    self.render_template(tpl_vars=tpl_vars)

  # POST /switch
  def switch(self):
    index = int(self.form["index"].value)
    self.server.drone.toggle(index)
    self.render_template()

  # POST /up
  def up(self):
    self.server.drone.up()
    self.render_template()

  # POST /down
  def down(self):
    self.server.drone.down()
    self.render_template()

  # POST /left
  def left(self):
    self.server.drone.left()
    self.render_template()

  # POST /right
  def right(self):
    self.server.drone.right()
    self.render_template()

  # POST /center
  def center(self):
    self.server.drone.center()
    self.render_template()

  # POST /forward
  def forward(self):
    self.server.drone.forward()
    self.render_template()

  # POST /back
  def back(self):
    self.server.drone.back()    
    self.render_template()

  # POST /stop
  def stop(self):
    self.server.drone.stop()    
    self.render_template()

  # POST /speedup
  def speedup(self):
    self.server.drone.speedup()  
    self.render_template()

  # POST /slowdown
  def slowdown(self):
    self.server.drone.slowdown()  
    self.render_template()

  # POST /set_pwm
  def set_pwm(self):
    channel = int(self.form["channel"].value)
    value = int(self.form["value"].value)
    self.server.drone.set_pwm(channel = channel, value = value)  
    self.render_template()

  # POST /switch_pwm
  def switch_pwm(self):
    channel = int(self.form["channel"].value)
    value_on = int(self.form["valueOn"].value)
    value_off = int(self.form["valueOff"].value)
    status = self.server.drone.status["PWM"][channel]

    if (status == None or status == value_off):
      self.server.drone.set_pwm(channel = channel, value = value_on)
    else:
      self.server.drone.set_pwm(channel = channel, value = value_off)

    self.render_template()

  # POST /sequence_pwm
  def sequence_pwm(self):
    params = self.form["params"].value
    sequence = params.split("|")
    for command in sequence:
      (channel,value,delay) = command.split(",") 
      self.server.drone.set_pwm(channel = int(channel), value = int(value))
      time.sleep(int(delay)/1000.0)  
    self.render_template()

  def render_template(self, template="home.html", tpl_vars={}):
    if not tpl_vars:
      tpl_vars = self.server.drone.status

    if self.request_xhr:
      self.content_type = "application/json"
      self.content = json.dumps(tpl_vars)
    else:
      tpl = os.path.join(self.config["TEMPLATE_FOLDER"], template)
      if os.path.isfile(tpl):
        tpl_content = open(tpl,"r").read()
        self.content = pystache.render(tpl_content, tpl_vars)
      else:
        self.give_404("Template %s missing" % template)


def main():

  # read configuration from json
  basedir = os.path.dirname(os.path.abspath(__file__))
  web_config_file = os.path.join(basedir,"config","web.json")
  drone_config_file = os.path.join(basedir,"config","drone.json")
  sensors_config_file = os.path.join(basedir,"config","sensors.json")

  # instantiate http server
  WebServer = RPiHTTPServer(web_config_file, XTCDHandler)

  # parse drone config file
  drone_config = {}
  
  if os.path.isfile(drone_config_file):
    try:
      drone_config = json.load(open(drone_config_file,'r'))
    except:
      print "Error parsing drone configuration file"

  # parse drone config file
  sensors_config = {}
  
  if os.path.isfile(sensors_config_file):
    try:
      sensors_config = json.load(open(sensors_config_file,'r'))
    except:
      print "Error parsing sensors configuration file"

  # quick access to config params
  config = WebServer.server.config

  # assign variables to web server
  WebServer.server.drone = Drone(drone_config) # instantiate drone controller
  WebServer.server.root_folder = basedir

   # start the web server
  try:
    if "KEEP_ALIVE" in drone_config:
      WebServer.server.drone.keep_alive(drone_config["KEEP_ALIVE"]["MIN"])
    print "Server listening on http://%s:%s" % (config["SERVER_ADDRESS"],config["SERVER_PORT"])
    WebServer.serve_forever()
  except KeyboardInterrupt:
    pass
    # TODO: cleanup pwm status on close
    WebServer.server.server_close()


if __name__ == '__main__':

  main()

