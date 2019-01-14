#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPiHTTPServer import RPiHTTPServer
from drone import Drone
from sensors import Sensors
from web import WebHandler
import threading
import time
import os
import json
import traceback
import atexit
import signal

# class coordinating the components:
# - web server
# - drone controller
# - sensors controller

class XTCD:

  def __init__(self, basedir):
    web_config_file = os.path.join(basedir,"config","web.json")
    drone_config_file = os.path.join(basedir,"config","drone.json")
    sensors_config_file = os.path.join(basedir,"config","sensors.json")

    # be sure to give exception if main config is missing or malformed
    web_config = json.load(open(web_config_file,'r'))
    # instantiate http server
    self.web = RPiHTTPServer(web_config_file, WebHandler)

    # quick access to config params
    self.config = self.web.server.config

    # parse drone config file
    self.drone_config = {}
    
    if os.path.isfile(drone_config_file):
      try:
        self.drone_config = json.load(open(drone_config_file,'r'))
        # instantiate drone controller
        self.drone = Drone(self.drone_config, controller = self)
      except Exception as e:
        self.log("Error parsing drone configuration file")
        self.log(traceback.format_exc())

    # parse drone config file
    self.sensors_config = {}
    
    if os.path.isfile(sensors_config_file):
      try:
        self.sensors_config = json.load(open(sensors_config_file,'r'))
        # instantiate sensors controller
        self.sensors = Sensors(self.sensors_config, controller = self) 
      except Exception as e:
        self.log("Error parsing sensors configuration file")
        self.log(traceback.format_exc())

    # pass data to web server
    self.web.server.controller = self
    self.web.server.root_folder = basedir
    self.web.server.web_config_file = web_config_file
    self.web.server.drone_config_file = drone_config_file  
    self.web.server.sensors_config_file = sensors_config_file

  # start the web server
  def start(self):
    self.log("Server listening on http://%s:%s" % (self.config["SERVER_ADDRESS"],self.config["SERVER_PORT"]))
    # start the keep alive thread if needed
    if "KEEP_ALIVE" in self.drone_config:
      self.drone.keep_alive(self.drone_config["KEEP_ALIVE"]["MIN"])
    self.web.serve_forever()

  # stop everything 
  def stop(self):
    # stop the drone
    self.drone.shutdown()
    # stop the web server
    self.web.server.server_close()

  # logger
  def log(self, message):
    print "[%s] - %s" % (time.strftime("%d/%b/%Y %H:%M:%S"), message)


if __name__ == '__main__':

  basedir = os.path.dirname(os.path.abspath(__file__))
  xtcd = XTCD(basedir)

  def handle_exit(*args):
    xtcd.stop()

  atexit.register(handle_exit)
  signal.signal(signal.SIGTERM, handle_exit)
  signal.signal(signal.SIGINT, handle_exit)

  try:
    xtcd.start()
  except KeyboardInterrupt:
    xtcd.stop()
