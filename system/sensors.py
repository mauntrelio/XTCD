#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_ADS1x15
import time
import subprocess
import traceback

class Sensors:
  def __init__(self, config, controller=None):

    self.config = config

    self.status = {}
    for key in self.config.keys():
      self.status[key] = {
        "id": key,
        "value": None,
        "reading": None,
        "unit": self.config[key]["unit"]
      }

    # ADC (TODO: put gain in the configuration, either global, or per sensor)
    self.adc = Adafruit_ADS1x15.ADS1115()
    self.adc_GAIN = 2/3
    self.adc_MAX_VAL = 4.096*3/2
    self.adc_MAX = 32768.0

    self.controller = controller

  # TODO:
  #   - implement periodic readings (interval)
  #   - implement Data Logger
  #   - implement different methods get_value (to get the last read value for periodic readings) 
  #     and read_value (to read a value immediately)

  def get_sensor(self, sensor_id):
    if not sensor_id in self.status:
      self.controller.log("Sensor %s not found" % sensor_id)
      return {
        "id": sensor_id,
        "value": None,
        "reading": None,
        "unit": ""
      }

    sensor = self.status[sensor_id]  

    # read the sensor if we do not have a value
    if not sensor["value"]:
      self.controller.log("Reading sensor %s because value is missing" % sensor_id)
      self.read_sensor(sensor_id)

    # read the sensor if last reading is older then it should be
    if time.time() - sensor["reading"] > self.config[sensor_id]["frequency"]:
      self.controller.log("Reading sensor %s because cached value is expired" % sensor_id)
      self.read_sensor(sensor_id)

    # return the sensor
    return self.status[sensor_id] 


  def read_sensor(self, sensor_id):

    value = None

    if not sensor_id in self.config:
      return {
        "id": sensor_id,
        "value": None,
        "reading": None,
        "unit": ""
      }

    sensor = self.config[sensor_id]
    source = sensor["source"]
    params = sensor["source_params"]

    try:
      # command line sensor
      if source == "commandline":
        value = subprocess.check_output(params["cmd"], shell=True)

      # ADS1 sensor
      elif sensor["source"] == "ADS1":
        reading = self.adc.read_adc(params["channel"], gain=self.adc_GAIN)
        value = (reading / self.adc_MAX) * self.adc_MAX_VAL

      # DHT sensor
      elif sensor["source"] == "DHT":
        types = {'11': Adafruit_DHT.DHT11,
                  '22': Adafruit_DHT.DHT22,
                  '2302': Adafruit_DHT.AM2302 }
        
        if params["type"] in types:
          sensor_type = types[params["type"]]
          h, t = Adafruit_DHT.read_retry(sensor_type, params["pin"])
          if params["index"] == 0:
            value = h
          else:
            value = t
        
      # BMP sensor
      elif sensor["source"] == "BMP":
        if hasattr(self.bmp, params["method"]):
          value = getattr(self.bmp, params["method"])()
          value *= params["multiplier"]

    except Exception as e:
      self.controller.log("Error reading sensor %s" % sensor_id)
      self.controller.log(traceback.format_exc())
      value = None  

    if sensor["type"] == "float":
      if value:
        value = float(value)
        value = round(value,2)

    self.status[sensor_id]["value"] = value
    # update time of last reading
    self.status[sensor_id]["reading"] = time.time()
