#!/usr/bin/python
# -*- coding: utf-8 -*-
from RPiHTTPServer import RPiHTTPServer, RPiHTTPRequestHandler
import serial
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
        # send data to Arduino
        command = self.server.positions[pos]
        self.server.serial.write(command)
        # set template vars for GUI
        tpl_vars['{{message}}'] = "Sending %s to Arduino" % command
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

  positions = {
    "000": "L",
    "090": "U",
    "180": "R"
  }

  # read configuration from json
  basedir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(basedir,"config.json")

  # instantiate http server
  SwitchServer = RPiHTTPServer(config_file, ServoHandler)

  # quick access to config params
  config = SwitchServer.server.config

  # set serial
  ser = serial.Serial(
               port = config.SERIAL_PORT, \
               baudrate = 9600, \
               parity=serial.PARITY_NONE, \
               stopbits=serial.STOPBITS_ONE, \
               bytesize=serial.EIGHTBITS, \
               timeout=1
           )

  # assign variables to server
  SwitchServer.server.serial = ser
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
