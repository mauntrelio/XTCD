#!/usr/bin/python
# -*- coding: utf-8 -*-
from RPiHTTPServer import RPiHTTPServer, RPiHTTPRequestHandler
import Adafruit_PCA9685
import os
import time
import re

class ServoHandler(RPiHTTPRequestHandler):

  # GET /
  def default_response(self):
    tpl_vars = {
      '{{message}}': '',
      '{{selected000}}': '',
      '{{selected090}}': '',
      '{{selected180}}': ''
    }

    """Control servo according to QS param"""
    if 'pos' in self.qs:
      pos = self.qs['pos'][0]
      # only if param is one of the possible values
      if pos in self.server.positions.keys():
        # send data to pwm controller
        pwm_set = self.server.positions[pos]
        self.server.pwm.set_pwm(self.server.config.SERVO_CHANNEL, 0, pwm_set)
        self.server.pwm.set_pwm(self.server.config.SERVO_CHANNEL+1, 0, pwm_set)
        self.server.pwm.set_pwm(self.server.config.SERVO_CHANNEL+2, 0, pwm_set)
        # self.server.pwm.set_all_pwm(0, pwm_set)
        # set template vars for GUI
        tpl_vars['{{message}}'] = "Setting PWM to %s" % pwm_set
        tpl_vars["{{selected%s}}" % pos] = "selected"

    print tpl_vars['{{message}}']

    # render templates
    self.render_template(tpl_vars)

  def render_template(self, tpl_vars):
    tpl = os.path.join(self.server.root_folder, 'home.html')
    tpl_content = open(tpl,"r").read()
    pattern = re.compile('|'.join(tpl_vars.keys()))
    self.content = pattern.sub(lambda x: tpl_vars[x.group()], tpl_content)


def main():

  # read configuration from json
  basedir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(basedir,"config.json")

  # instantiate http server
  SwitchServer = RPiHTTPServer(config_file, ServoHandler)

  # quick access to config params
  config = SwitchServer.server.config

  # instantiate and initialise pwm controller
  pwm = Adafruit_PCA9685.PCA9685(address=int(config.I2C_ADDR,16))
  pwm.set_pwm_freq(config.SERVO_FREQ)
  positions = {
    "000": config.SERVO_MIN,
    "090": (config.SERVO_MAX + config.SERVO_MIN)/2,
    "180": config.SERVO_MAX
  }


  # assign variables to server
  SwitchServer.server.pwm = pwm
  SwitchServer.server.positions = positions
  SwitchServer.server.root_folder = basedir

  try:
    print "Server listening on http://%s:%s" % (config.SERVER_ADDRESS,config.SERVER_PORT)
    SwitchServer.serve_forever()
  except KeyboardInterrupt:
    pass
    SwitchServer.server.server_close()


if __name__ == '__main__':

  main()
