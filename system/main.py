#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPiHTTPServer import RPiHTTPServer
from drone import Drone
from sensors import Sensors
from web import WebHandler
from collections import OrderedDict
import threading
import time
import os
import sys
import json
import traceback
import atexit
import signal
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

# class coordinating the components:
# - web server
# - drone controller
# - sensors controller

class XTCD:

  def __init__(self, basedir):
    web_config_file = os.path.join(basedir,"config","web.json")
    drone_config_file = os.path.join(basedir,"config","drone.json")
    sensors_config_file = os.path.join(basedir,"config","sensors.json")

    # be sure to give exception immediately if web config is missing or malformed
    self.web_config = json.load(open(web_config_file,'r'), object_pairs_hook=OrderedDict)
    # instantiate http server
    self.web = RPiHTTPServer(web_config_file, WebHandler)
    
    # setup logging
    self.setup_logger(basedir)

    # parse drone config file and instantiate drone controller
    self.drone_config = {}
    if os.path.isfile(drone_config_file):
      try:
        self.drone_config = json.load(open(drone_config_file,'r'), object_pairs_hook=OrderedDict)
        self.log("Instantiating drone controller", severity = 20)
        self.drone = Drone(self.drone_config, controller = self)
      except Exception as e:
        self.log("Error in drone configuration", severity = 40)
        self.log(traceback.format_exc(), severity = 40)

    # parse sensors config file and instantiate sensors controller
    self.sensors_config = {}
    if os.path.isfile(sensors_config_file):
      try:
        self.sensors_config = json.load(open(sensors_config_file,'r'), object_pairs_hook=OrderedDict)
        self.log("Instantiating sensors controller", severity = 20)
        self.sensors = Sensors(self.sensors_config, controller = self) 
      except Exception as e:
        self.log("Error in sensors configuration", severity = 40)
        self.log(traceback.format_exc(), severity = 40)

    # pass data to web server
    self.web.server.controller = self
    self.web.server.root_folder = basedir
    self.web.server.web_config_file = web_config_file
    self.web.server.drone_config_file = drone_config_file  
    self.web.server.sensors_config_file = sensors_config_file

  # setup the logger
  def setup_logger(self, basedir):
    # configure logging
    log_file = os.path.join(basedir,"logs","xtcd.log")
    if "LOG_LEVEL" in self.web_config:
      log_level = self.web_config["LOG_LEVEL"]
    else:
      log_level = 40
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_format = logging.Formatter('[%(asctime)s] - %(name)s/%(threadName)s - %(levelname)s - %(message)s')

    log_ch = logging.StreamHandler(sys.stdout)
    log_ch.setFormatter(log_format)
    logger.addHandler(log_ch)

    log_fh = handlers.RotatingFileHandler(log_file, maxBytes=(1048576*5), backupCount=7)
    log_fh.setFormatter(log_format)
    logger.addHandler(log_fh)

  # start xtcd
  def start(self):
    # start the keep alive thread if needed
    if "KEEP_ALIVE" in self.drone_config:
      self.log("Starting keep alive thread", severity = 20)
      self.drone.keep_alive(self.drone_config["KEEP_ALIVE"]["MIN"])
    self.log("Starting web server on http://%s:%s" % (self.web_config["SERVER_ADDRESS"],self.web_config["SERVER_PORT"]), severity = 20)
    self.web.serve_forever()

  # stop xtcd 
  def stop(self):
    # stop the drone
    self.log("Exiting: stopping drone", severity = 30)
    self.drone.shutdown()
    # stop the web server
    self.log("Exiting: stopping web server", severity = 30)
    self.web.server.server_close()

  # logger
  def log(self, message, severity = 10):
    logging.log(severity, message)

if __name__ == '__main__':

  basedir = os.path.dirname(os.path.abspath(__file__))
  xtcd = XTCD(basedir)

  # exit properly stopping motors, web server, etc..
  def handle_exit(*args):
    try:
      xtcd.stop()
    except:
      pass
      
  # register exit function
  atexit.register(handle_exit)
  signal.signal(signal.SIGTERM, handle_exit)
  signal.signal(signal.SIGINT, handle_exit)

  try:
    xtcd.start()
  except KeyboardInterrupt:
    xtcd.stop()
