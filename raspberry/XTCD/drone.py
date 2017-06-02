#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_PCA9685.PCA9685 as pca9685
import time

class Drone:

  def __init__(self, config):

    self.config = config

    # instantiate and initialise pwm controller
    self.pwm = pca9685(address=int(config["I2C_ADDR"],16))
    self.pwm.set_pwm_freq(config["FREQUENCY"])

    # put motors to stop position
    for motor in config["MOTORS"]:
      self.pwm.set_pwm(motor["CHANNEL"], 0, config["ESC_SPEED_STOP"])

    # put direction switches to neutral position
    for switch in config["SERVO_SWITCHES"]:
      self.pwm.set_pwm(switch["ADDRESS"], 0, switch["N"])

    # center camera
    self.pwm.set_pwm(config["AZIMUTH"]["CHANNEL"], 0, config["AZIMUTH"]["NEUTRAL"])
    self.pwm.set_pwm(config["ALTITUDE"]["CHANNEL"], 0, config["ALTITUDE"]["NEUTRAL"])

    # TODO: status should be read directly interfacing to hardware
    self.status = {
      "AZIMUTH": config["AZIMUTH"]["NEUTRAL"],
      "ALTITUDE": config["ALTITUDE"]["NEUTRAL"],
      "SPEED": config["ESC_SPEED_STOP"],
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
    self.pwm.set_pwm(self.config["AZIMUTH"]["CHANNEL"], 0, self.config["AZIMUTH"]["NEUTRAL"])
    self.pwm.set_pwm(self.config["ALTITUDE"]["CHANNEL"], 0, self.config["ALTITUDE"]["NEUTRAL"])
    self.status["ALTITUDE"] = self.config["ALTITUDE"]["NEUTRAL"]
    self.status["AZIMUTH"] = self.config["AZIMUTH"]["NEUTRAL"]

  # move the camera of one step in the desired direction and coordinate
  def step(self, coord, direction):
    step_dir = self.config[coord]["ORIENTATION"]
    channel = self.config[coord]["CHANNEL"]
    pwm_value = self.status[coord] + direction * step_dir * self.config["MIN_STEP_POS"]
    if pwm_value <= self.config[coord]["MAX"] and pwm_value >= self.config[coord]["MIN"]:
      self.pwm.set_pwm(channel, 0, pwm_value)
      self.status[coord] = pwm_value

  # start moving forward
  def forward(self):
    self.set_direction(self.config["FORWARD_DIRECTION"])

  # start moving backward
  def back(self):
    self.set_direction(self.config["BACK_DIRECTION"])

  # Stop
  def stop(self):
    self.set_speed(self.config["ESC_SPEED_STOP"])
    self.set_direction("N")

  # Speed up
  def speedup(self):
    # brush motor: increment depend on direction
    if self.config["MOTOR_TYPE"] == "B":
      if self.status["DIRECTION"] == self.config["FORWARD_DIRECTION"]:
        pwm_value = self.status["SPEED"] + self.config["MIN_STEP_SPEED"]
        if pwm_value <= self.config["ESC_SPEED_MAX"]:
          self.set_speed(pwm_value)
      else:
        pwm_value = self.status["SPEED"] - self.config["MIN_STEP_SPEED"]
        if pwm_value >= self.config["ESC_SPEED_STOP"]:
          self.set_speed(pwm_value)
    # brushless motor
    else:
      pwm_value = self.status["SPEED"] + self.config["MIN_STEP_SPEED"]
      if pwm_value <= self.config["ESC_SPEED_MAX"]:
        self.set_speed(pwm_value)

  # Slow down
  def slowdown(self):
    # brush motor: increment depend on direction
    if self.config["MOTOR_TYPE"] == "B":
      if self.status["DIRECTION"] == self.config["FORWARD_DIRECTION"]:
        pwm_value = self.status["SPEED"] - self.config["MIN_STEP_SPEED"]
        if pwm_value >= self.config["ESC_SPEED_STOP"]:
          self.set_speed(pwm_value)
      else:
        pwm_value = self.status["SPEED"] + self.config["MIN_STEP_SPEED"]
        if pwm_value >= self.config["ESC_SPEED_STOP"]:
          self.set_speed(pwm_value)
    # brushless motor
    else:
      pwm_value = self.status["SPEED"] - self.config["MIN_STEP_SPEED"]
      if pwm_value >= self.config["ESC_SPEED_MIN"]:
        self.set_speed(pwm_value)

  def set_speed(self, speed):
    for motor in self.config["MOTORS"]:
      self.pwm.set_pwm(motor["CHANNEL"], 0, speed)
    self.status["SPEED"] = speed

  def set_direction(self, direction):
    if self.status["DIRECTION"] != direction:
      # stop the motor
      self.set_speed(self.config["ESC_SPEED_STOP"])
      # if brushless or neutral position requested: set direction switches in neutral position
      if self.config["MOTOR_TYPE"] != "B" or direction == "N":
        for switch in self.config["SERVO_SWITCHES"]:
          self.pwm.set_pwm(switch["ADDRESS"], 0, switch["N"])
        self.status["DIRECTION"] = "N"
      
      # only move when direction is back or forward
      if direction != "N":
        # wait before inverting direction
        time.sleep(self.config["CHANGE_DIR_PAUSE"])
        # if brushless set direction switches in desired position
        if self.config["MOTOR_TYPE"] != "B":
          for switch in self.config["SERVO_SWITCHES"]:
            self.pwm.set_pwm(switch["ADDRESS"], 0, switch[direction])

        self.status["DIRECTION"] = direction

        # set start and minimum speed
        speed_start = self.config["ESC_SPEED_STOP"] + self.config["STEP_SPEED_START"]
        speed_min = self.config["ESC_SPEED_STOP"] + self.config["MIN_STEP_SPEED"]

        # brush motor in reverse direction needs backwards speed
        if self.config["MOTOR_TYPE"] == "B" and self.status["DIRECTION"] == "B":
          speed_start = self.config["ESC_SPEED_STOP"] - self.config["STEP_SPEED_START"]
          speed_min = self.config["ESC_SPEED_STOP"] - self.config["MIN_STEP_SPEED"]

        # start the motor and keep speed higher than minimum for some seconds
        self.set_speed(speed_start)
        time.sleep(self.config["STARTUP_PULSE"])
        # put the motor to minimum speed
        self.set_speed(speed_min)
