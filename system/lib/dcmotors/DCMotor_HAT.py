#!/usr/bin/python

import time
from ..Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor

class DCMotor_HAT:
  """
  DCMotor_HAT:
  Implements a brush motor controlled via the Raspberry Stepper Motor HAT
  Expects the following parameters in init:
    config: a configuration dictionary for the motor with the following 
            parameters:
      ID:               a string identifying the motor
      CHANNEL:          channel of the PWM Stepper Motor HAT where the motor 
                        is connected
      DIRECTION:        adjust direction according to the polarity of motor 
                        cabling (1 or -1, to control that what you mean 
                        "forward" is what you expect)
      SPEED_STEP:       Increment amount for a single speed increment 
                        (speed is in range 0-255)
      F.SPEED_MAX:      Forward direction maximum speed 
      F.SPEED_MIN:      Forward direction minimum speed
      F.SPEED_START:    Forward direction starting speed
      B.SPEED_MAX:      Backward direction maximum speed 
      B.SPEED_MIN:      Backward direction minimum speed 
      B.SPEED_START:    Backward direction starting speed 
      CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
                        from forward to backward or viceversa
      STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
                        (when starting) before going at minimum speed   

    controller: the object which use the driver (at the moment it must only 
                implement the log method, accepting a string as argument)
  """

  def __init__(self, config, controller):
    self.id = config["ID"]
    self.config = config
    self.speed = 0
    self.direction = "X"
    self.controller = controller
    mh = Raspi_MotorHAT(addr=0x6f)
    self.motor = mh.getMotor(config["CHANNEL"])
    self.stop()

  def get_motor_dir(self, direction):
  # access to speed parameter x direction depending on cabling polarity:
    # by default we access the parameters of the provided direction
    motor_dir = direction 
    if self.config["DIRECTION"] == -1: 
      # if the motor is cabled reversed we access the parameters of the 
      # opposite direction
      motor_dir = "F" if direction == "B" else "B"
    return motor_dir     

  def go(self, direction):
    if self.direction != direction:
      if self.direction != "N":
        self.stop()
        if "CHANGE_DIR_PAUSE" in self.config:
          time.sleep(self.config["CHANGE_DIR_PAUSE"])
    else:
      return

    # access to speed parameter x direction depending on cabling polarity:
    motor_dir = self.get_motor_dir(direction)

    self.direction = direction
    if motor_dir == "F":
      self.motor.run(Raspi_MotorHAT.FORWARD)
    else:
      self.motor.run(Raspi_MotorHAT.BACKWARD)

    self.speed = self.config[motor_dir + ".SPEED_START"]
    self.controller.log("%s: setting speed to %s" % (self.id, self.speed))
    self.motor.setSpeed(self.speed)
    
    # let the motor start to win initial inertia
    if "STARTUP_PULSE" in self.config:
      time.sleep(self.config["STARTUP_PULSE"])
    self.speed = self.config[motor_dir + ".SPEED_MIN"]

    self.controller.log("%s: setting speed to %s" % (self.id, self.speed))
    self.motor.setSpeed(self.speed)

  def forward(self):
    self.controller.log("%s: moving forward" % self.id)
    self.go("F")

  def back(self):
    self.controller.log("%s: moving backward" % self.id)
    self.go("B")

  def stop(self):
    self.controller.log("%s: stopping" % self.id)
    self.direction = "N"
    self.speed = 0
    self.motor.setSpeed(self.speed)
    self.motor.run(Raspi_MotorHAT.RELEASE)

  def speedup(self):
    if self.direction == "N":
      return
    new_speed = self.speed + self.config["SPEED_STEP"]
    if (new_speed <= self.config[self.get_motor_dir(self.direction) + ".SPEED_MAX"]):
      self.speed = new_speed
      self.controller.log("Setting HAT speed motor to %s" % self.speed)
      self.motor.setSpeed(self.speed)
  
  def slowdown(self):
    if self.direction == "N":
      return
    new_speed = self.speed - self.config["SPEED_STEP"]
    if (new_speed >= self.config[self.get_motor_dir(self.direction) + ".SPEED_MIN"]):
      self.speed = new_speed
      self.controller.log("Setting HAT speed motor to %s" % self.speed)
      self.motor.setSpeed(self.speed)