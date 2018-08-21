#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_ADS1x15
import time
import RPi.GPIO as GPIO
import subprocess

class Sensors:
  def __init__(self, config):

    self.config = config

    self.status = {}
    for key in self.config.keys():
      self.status[key] = {
        "last_value": None,
        "last_reading": None,
        "unit": self.config[key]["unit"]
      }

    # ADC (TODO: put gain in the configuration, either global, or per sensor)
    self.adc = Adafruit_ADS1x15.ADS1115()
    self.adc_GAIN = 2/3
    self.adc_MAX = 4.096*3/2


  # TODO:
  #   - implement periodic readings (interval)
  #   - implement Data Logger
  #   - implement get_value and read_value (for periodic readings)

  def get_value(self, sensor_id):

    value = None

    if not sensor_id in self.config:
      return None

    sensor = self.config[sensor_id]
    
    if sensor["source"] == "commandline":
      value = subprocess.check_output(sensor["cmd"], shell=True)

    elif sensor["source"] == "ADS1":
      reading = self.adc.read_adc(sensor["channel"], gain=self.adc_GAIN)
      value = round((reading / 32768.0) * self.adc_MAX,2)

    return value
