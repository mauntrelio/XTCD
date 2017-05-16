#!/usr/bin/python
# -*- coding: utf-8 -*-

# import Adafruit_PCA9685.PCA9685 as pca9685
from pca9685 import pca9685 as pca9685
import time

class Drone:

  def __init__(self, config):

    self.config = config

    # instantiate and initialise pwm controller
    self.pwm = pca9685(address=int(config.I2C_ADDR,16))
    self.pwm.set_pwm_freq(config.FREQUENCY)

    # put motors to stop position
    for motor in config.MOTORS:
      self.pwm.set_pwm(motor["CHANNEL"], 0, config.ESC_SPEED_STOP)

    # put direction switches to neutral position
    DIRS = config.DIRECTIONS
    self.pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0]["N"])
    self.pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1]["N"])

    # center camera
    self.servos_center = int((config.SERVO_MAX + config.SERVO_MIN)/2)
    self.pwm.set_pwm(config.AZIMUTH["CHANNEL"], 0, self.servos_center)
    self.pwm.set_pwm(config.ALTITUDE["CHANNEL"], 0, self.servos_center)

    # TODO: status should be read directly interfacing to hardware
    self.status = {
      "AZIMUTH": self.servos_center,
      "ALTITUDE": self.servos_center,
      "SPEED": 0,
      "DIRECTION": "N"
    }


  # move camera up
  def up(self):
    self.step("ALTITUDE", 1)

  # move camera down
  def down(self):
    self.step("ALTITUDE", -1)

  # move camera left
  def left(self):
    self.step("AZIMUTH", 1)

  # move camera right
  def right(self):
    self.step("AZIMUTH", -1)

  # move back camera to center position
  def center(self):
    self.pwm.set_pwm(self.config.AZIMUTH["CHANNEL"], 0, self.servos_center)
    self.pwm.set_pwm(self.config.ALTITUDE["CHANNEL"], 0, self.servos_center)
    self.status["ALTITUDE"] = self.servos_center
    self.status["AZIMUTH"] = self.servos_center

  def step(self, param, direction):
    coord = getattr(self.config, param)
    step_dir = coord["ORIENTATION"]
    channel = coord["CHANNEL"]
    pwm_value = self.status[param] + direction * step_dir * self.config.MIN_STEP_POS
    if pwm_value <= self.config.SERVO_MAX and pwm_value >= self.config.SERVO_MIN:
      self.pwm.set_pwm(channel, 0, pwm_value)
      self.status[param] = pwm_value

  # start moving forward
  def forward(self):
    self.set_direction(self.config.FORWARD_DIRECTION)

  # start moving back
  def back(self):
    self.set_direction(self.config.BACK_DIRECTION)

  # Stop
  def stop(self):
    self.set_speed(self.config.ESC_SPEED_STOP)
    self.set_direction("N")

  # Speed up
  def speedup(self):
    pwm_value = self.status["SPEED"] + self.config.MIN_STEP_SPEED
    if pwm_value <= self.config.ESC_SPEED_SAFEMAX:
      self.set_speed(pwm_value)

  # Slow down
  def slowdown(self):
    pwm_value = self.status["SPEED"] - self.config.MIN_STEP_SPEED
    if pwm_value >= self.config.ESC_SPEED_MIN:
      self.set_speed(pwm_value)

  def set_speed(self, speed):
    for motor in self.config.MOTORS:
      self.pwm.set_pwm(motor["CHANNEL"], 0, speed)
    self.status["SPEED"] = speed

  def set_direction(self,direction):
    if self.status["DIRECTION"] != direction:
      DIRS = self.config.DIRECTIONS
      # stop the motor
      self.set_speed(self.config.ESC_SPEED_STOP)
      # set direction switches in neutral position
      self.pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0]["N"])
      self.pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1]["N"])
      self.status["DIRECTION"] = "N"
      
      # only move when direction is back or forward
      if direction != "N":
        # wait
        time.sleep(self.config.CHANGE_DIR_PAUSE)
        # set direction switches in desired position
        self.pwm.set_pwm(DIRS[0]["ADDRESS"], 0, DIRS[0][direction])
        self.pwm.set_pwm(DIRS[1]["ADDRESS"], 0, DIRS[1][direction])
        self.status["DIRECTION"] = direction
        # start the motor and keep speed higher than minimum for some seconds
        self.set_speed(self.config.ESC_SPEED_START)
        time.sleep(self.config.STARTUP_PULSE)
        # put the motor to minumum speed
        self.set_speed(self.config.ESC_SPEED_MIN)   
