#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_PCA9685.PCA9685 as pca9685
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import time

class Drone:

  def __init__(self, config):

    self.config = config
    # TODO: status should be read directly interfacing to hardware
    self.status = {"SPEEDS": {}, "RELAYS": {}}

    self.MOTORS = self.config["MOTORS"] if self.config["MOTORS"] else []
    self.RELAYS = self.config["RELAYS"] if self.config["RELAYS"] else []

    # instantiate and initialise pwm controller
    self.pwm = pca9685(address=int(config["I2C_ADDR"],16))
    self.pwm.set_pwm_freq(config["FREQUENCY"])

    # put motors to stop position
    for motor in self.MOTORS:
      self.pwm.set_pwm(motor["CHANNEL"], 0, motor["SPEED_STOP"])
      self.status["SPEEDS"][motor["CHANNEL"]] = motor["SPEED_STOP"]
      # put direction switches to neutral position
      if motor["SERVO"]:
        self.pwm.set_pwm(motor["SERVO"]["CHANNEL"], 0, motor["SERVO"]["POS_N"])
    
    self.status["DIRECTION"] = "N"

    # set relais GPIO as output and set them OFF
    for relay in self.RELAYS:
      GPIO.setup(relay, GPIO.OUT)
      GPIO.setup(relay, GPIO.LOW)
      self.status["RELAYS"][relay] = 0

    # center camera
    self.pwm.set_pwm(config["AZIMUTH"]["CHANNEL"], 0, config["AZIMUTH"]["NEUTRAL"])
    self.pwm.set_pwm(config["ALTITUDE"]["CHANNEL"], 0, config["ALTITUDE"]["NEUTRAL"])
    self.status["AZIMUTH"] = config["AZIMUTH"]["NEUTRAL"]
    self.status["ALTITUDE"] = config["ALTITUDE"]["NEUTRAL"]

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

  # switch on a relay
  def on(self, relay):
    GPIO.setup(relay, GPIO.HIGH)
    self.status["RELAYS"][relay] = 1

  # switch off a relay
  def off(self, relay):
    GPIO.setup(relay, GPIO.LOW)
    self.status["RELAYS"][relay] = 0

  # toggle a relay
  def toggle(self, relay):
    if self.status["RELAYS"][relay] = 0: 
      self.on(relay)
    else:
      self.off(relay)  
    
  # start moving forward
  def forward(self):
    self.set_direction("F")

  # start moving backward
  def back(self):
    self.set_direction("B")

  # Stop
  def stop(self):
    # put motors to stop position
    for motor in self.MOTORS:
      self.pwm.set_pwm(motor["CHANNEL"], 0, motor["SPEED_STOP"])
      self.status["SPEEDS"][motor["CHANNEL"]] = motor["SPEED_STOP"]
    
    self.set_direction("N")

  # Speed up
  def speedup(self):

    for motor in self.MOTORS:
      step_dir = 1 # speed up is increase speed by default
      motor_dir = "F"
      # brush motor: increment depends on direction
      if motor["TYPE"] == "B":
        if motor["DIRECTION"] == 1:
          motor_dir = self.status["DIRECTION"]
        else:
          motor_dir = "F" if self.status["DIRECTION"] == "B" else "B"
        step_dir = 1 if motor_dir == "F" else -1

      pwm_value = self.status["SPEEDS"][motor["CHANNEL"]] + step_dir * motor["SPEED_STEP"]

      if pwm_value * step_dir <= motor[motor_dir]["SPEED_MAX"] * step_dir:
        self.set_speed(motor["CHANNEL"], pwm_value)

  # Slow down
  def slowdown(self):

    for motor in self.MOTORS:
      step_dir = 1 # slow down up is decrease speed by default
      motor_dir = "F"
      # brush motor: increment depends on direction
      if motor["TYPE"] == "B":
        if motor["DIRECTION"] == 1:
          motor_dir = self.status["DIRECTION"]
        else:
          motor_dir = "F" if self.status["DIRECTION"] == "B" else "B"
        step_dir = 1 if motor_dir == "F" else -1

      pwm_value = self.status["SPEEDS"][motor["CHANNEL"]] - step_dir * motor["SPEED_STEP"]

      if pwm_value * step_dir >= motor[motor_dir]["SPEED_MIN"] * step_dir:
        self.set_speed(motor["CHANNEL"], pwm_value)

  # Set the speed of a motor      
  def set_speed(self, motor, speed):
    self.pwm.set_pwm(motor, 0, speed)
    self.status["SPEEDS"][motor] = speed

  # move forward / backward / neutral
  def set_direction(self, direction):
    if self.status["DIRECTION"] != direction:
      # stop the motors
      for motor in self.MOTORS:
        self.set_speed(motor["CHANNEL"], motor["SPEED_STOP"])
        # if brushless or neutral position requested: set direction switches in neutral position
        if motor["TYPE"] == "L":
          if motor["SERVO"]:
            self.pwm.set_pwm(motor["SERVO"]["CHANNEL"], 0, motor["SERVO"]["POS_N"])
          self.status["DIRECTION"] = "N"
      
      # only start moving when requested direction is back or forward
      if direction != "N":
        # wait before inverting direction
        time.sleep(self.config["CHANGE_DIR_PAUSE"])
        # if brushless set direction switches in desired position
        for motor in self.MOTORS:
          if motor["TYPE"] == "L":
            if motor["SERVO"]:
              motor_dir = 1
              if motor["DIRECTION"] == -1:
                motor_dir = "F" if direction == "B" else "B"
              self.pwm.set_pwm(motor["SERVO"]["CHANNEL"], 0, motor["SERVO"]["POS_%s" % motor_dir])

        self.status["DIRECTION"] = direction

        # put the motors to START speed
        for motor in self.MOTORS:
          motor_dir = direction
          if motor["DIRECTION"] == -1:
            motor_dir = "F" if direction == "B" else "B"

          self.set_speed(motor["CHANNEL"], motor[motor_dir]["SPEED_START"])

        time.sleep(self.config["STARTUP_PULSE"])

        # put the motors to minimum speed
        for motor in self.MOTORS:
          motor_dir = direction
          if motor["DIRECTION"] == -1:
            motor_dir = "F" if direction == "B" else "B"
          
          self.set_speed(motor["CHANNEL"], motor[motor_dir]["SPEED_MIN"])

