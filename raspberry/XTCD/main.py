#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from RPiHTTPServer import RPiHTTPServer, RPiHTTPRequestHandler
import Adafruit_PCA9685.PCA9685 as pca9685
import pystache
import os
import socket
import time
import json

class XTCDHandler(RPiHTTPRequestHandler):

  # GET /
  def default_response(self):
    tpl_vars = self.server.status
    camera_url = "http://%s:8080/stream/video.mjpeg" % socket.gethostbyname(socket.gethostname())
    tpl_vars["CAMERA_URL"] = camera_url
    self.render_template(tpl_vars=tpl_vars)

  # POST /up
  def up(self):
    channel = self.config.ALTITUDE
    pwm = self.server.status["ALTITUDE"] + self.config.MIN_STEP_POS
    if pwm <= self.config.SERVO_MAX:
      self.server.pwm.set_pwm(channel, 0, pwm)
      self.server.status["ALTITUDE"] = pwm
    self.render_template()

  # POST /down
  def down(self):
    channel = self.config.ALTITUDE
    pwm = self.server.status["ALTITUDE"] - self.config.MIN_STEP_POS
    if pwm >= self.config.SERVO_MIN:
      self.server.pwm.set_pwm(channel, 0, pwm)
      self.server.status["ALTITUDE"] = pwm
    self.render_template()

  # POST /left
  def left(self):
    channel = self.config.AZIMUTH
    pwm = self.server.status["AZIMUTH"] - self.config.MIN_STEP_POS
    if pwm >= self.config.SERVO_MIN:
      self.server.pwm.set_pwm(channel, 0, pwm)
      self.server.status["AZIMUTH"] = pwm
    self.render_template()

  # POST /right
  def right(self):
    channel = self.config.AZIMUTH
    pwm = self.server.status["AZIMUTH"] + self.config.MIN_STEP_POS
    if pwm <= self.config.SERVO_MAX:
      self.server.pwm.set_pwm(channel, 0, pwm)
      self.server.status["AZIMUTH"] = pwm
    self.render_template()

  # POST /center
  def center(self):
    servos_center = int((self.config.SERVO_MAX + self.config.SERVO_MIN)/2)
    self.server.pwm.set_pwm(self.config.AZIMUTH, 0, servos_center)
    self.server.pwm.set_pwm(self.config.ALTITUDE, 0, servos_center)
    self.server.status["ALTITUDE"] = servos_center
    self.server.status["AZIMUTH"] = servos_center
    self.render_template()

  # POST /forward
  def forward(self):
    self.set_direction("F")
    self.render_template()

  # POST /back
  def back(self):
    self.set_direction("B")
    self.render_template()

  # POST /start
  def start(self):
    self.set_speed(self.config.ESC_SPEED_MIN)
    self.set_direction("F")
    self.render_template()

  # POST /stop
  def stop(self):
    self.set_speed(self.config.ESC_SPEED_STOP)
    self.set_direction("N")
    self.render_template()

  # POST /speedup
  def speedup(self):
    pwm = self.server.status["MOTOR"] + self.config.MIN_STEP_SPEED
    if pwm <= self.config.ESC_SPEED_MAX:
      self.set_speed(pwm)
    self.render_template()

  # POST /slowdown
  def slowdown(self):
    pwm = self.server.status["MOTOR"] - self.config.MIN_STEP_SPEED
    if pwm >= self.config.ESC_SPEED_MIN:
      self.set_speed(pwm)
    self.render_template()

  def set_speed(self,speed):
    self.server.pwm.set_pwm(self.config.MOTOR_1, 0, speed)
    #self.server.pwm.set_pwm(self.config.MOTOR_2, 0, speed)
    self.server.status["MOTOR"] = speed

  def set_direction(self,direction):
    if self.server.status["DIRECTION"] != direction:
      DIRS = self.config.DIRECTIONS
      self.server.pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0]["N"])
      self.server.pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1]["N"])
      self.set_speed(self.config.ESC_SPEED_STOP)
      time.sleep(self.config.CHANGE_DIR_PAUSE)
      self.server.pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0][direction])
      self.server.pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1][direction])
      self.server.status["DIRECTION"] = direction
      self.set_speed(self.config.ESC_SPEED_MIN+10)
      time.sleep(2)
      self.set_speed(self.config.ESC_SPEED_MIN)

  # POST /picture
  def take_picture(self):
    self.render_template()

  def render_template(self, template="home.html", tpl_vars={}):
    if not tpl_vars:
      tpl_vars = self.server.status

    if self.request_xhr:
      self.content_type = "application/json"
      self.content = json.dumps(tpl_vars)
    else:
      tpl = os.path.join(self.config.TEMPLATE_FOLDER, template)
      if os.path.isfile(tpl):
        tpl_content = open(tpl,"r").read()
        self.content = pystache.render(tpl_content, tpl_vars)
      else:
        self.give_404("Template %s missing" % template)


def main():

  # read configuration from json
  basedir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(basedir,"config.json")

  # instantiate http server
  WebServer = RPiHTTPServer(config_file, XTCDHandler)

  # quick access to config params
  config = WebServer.server.config

  # instantiate and initialise pwm controller
  pwm = pca9685(address=int(config.I2C_ADDR,16))
  pwm.set_pwm_freq(config.FREQUENCY)

  # put motors to stop position
  pwm.set_pwm(config.MOTOR_1, 0, config.ESC_SPEED_STOP)
  #pwm.set_pwm(config.MOTOR_2, 0, config.ESC_SPEED_STOP)
  DIRS = config.DIRECTIONS
  pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0]["N"])
  pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1]["N"])

  # center camera
  servos_center = int((config.SERVO_MAX + config.SERVO_MIN)/2)
  pwm.set_pwm(config.AZIMUTH, 0, servos_center)
  pwm.set_pwm(config.ALTITUDE, 0, servos_center)

  # assign variables to server
  WebServer.server.pwm = pwm
  WebServer.server.root_folder = basedir

  # TODO: status should be read directly interfacing to i2c
  WebServer.server.status = {
    "AZIMUTH": servos_center,
    "ALTITUDE": servos_center,
    "MOTOR": 0,
    "DIRECTION": 0
  }


  # start the web server
  try:
    print "Server listening on http://%s:%s" % (config.SERVER_ADDRESS,config.SERVER_PORT)
    WebServer.serve_forever()
  except KeyboardInterrupt:
    pass
    # TODO: cleanup pwm status
    WebServer.server.server_close()


if __name__ == '__main__':

  main()
