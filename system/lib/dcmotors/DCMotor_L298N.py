#!/usr/bin/python

import time
import RPi.GPIO as GPIO

class DCMotor_L298N:
  """
  DCMotor_L298N:
  Implements a brush motor controlled via an L298N connected to a PCA9685 PWM 
  signal generator
  This class has direct access to GPIO!
  Expects the following parameters in init:
    config: a configuration dictionary for the motor with the following 
            parameters:
      ID:               a string identifying the motor
      CHANNEL_PWM:      channel of the PWM controller where the EN channel is 
                        connected
      CHANNEL_IN1:      GPIO pin where the IN1 channel is connected
      CHANNEL_IN2:      GPIO pin where the IN2 channel is connected
      DIRECTION:        adjust direction according to the polarity of motor 
                        cabling (1 or -1, to control that what you mean 
                        "forward" is what you expect)
      SPEED_STEP:       Increment amount for a single speed increment 
                        (speed is in range 0-4095)
      F.SPEED_MAX:      Forward direction PWM value for maximum speed
      F.SPEED_MIN:      Forward direction PWM value for minimum speed
      F.SPEED_START:    Forward direction PWM value for starting speed
      B.SPEED_MAX:      Backward direction PWM value for maximum speed
      B.SPEED_MIN:      Backward direction PWM value for minimum speed 
      B.SPEED_START:    Backward direction PWM value for starting speed 
      CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
                        from forward to backward or vice versa
      STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
                        (when starting) before going at minimum speed   

    controller: an object which control the PCA9485 PWM signal generator 
                (it must implement the set_pwm method, accepting channel and 
                PWM value as arguments, and the log method, accepting a string
                as argument)
	"""

  def __init__(self, config, controller):
    self.id = config["ID"]
    self.config = config
    self.controller = controller
    self.direction = "X"
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.config["CHANNEL_IN1"], GPIO.OUT)
    GPIO.setup(self.config["CHANNEL_IN2"], GPIO.OUT)
    self.stop()    

  def get_motor_dir(self, direction):
   # access to speed parameter x direction depending on cabling polarity:
    motor_dir = direction # by default we access the parameters of the provided direction
    if self.config["DIRECTION"] == -1: 
      # if the motor is cabled reversed we access the parameters of the opposite direction
      motor_dir = "F" if direction == "B" else "B"
    return motor_dir     

  def set_speed(self, speed):
    self.speed = speed
    self.controller.set_pwm(channel = self.config["CHANNEL_PWM"], value = self.speed)

  def go(self, direction):
    # return immediately if no change in direction
    if self.direction == direction:
      return

    # save current direction
    current_direction = self.direction

    # access config shorter
    config = self.config

    # access to speed parameter x direction depending on cabling polarity:
    motor_dir = self.get_motor_dir(direction)

    # As a first step, we stop the motor
    self.stop()
    
    if direction != "N":
      # if we are switching direction (from B to F or vice versa)
      if current_direction != "N":
        # wait after switching
        if "CHANGE_DIR_PAUSE" in config:
          time.sleep(config["CHANGE_DIR_PAUSE"])

      # set the new current direction
      self.direction = direction

      # Set the GPIO HIGH
      channel = "CHANNEL_IN1" if motor_dir == "F" else "CHANNEL_IN2"
      GPIO.output(self.config[channel], GPIO.HIGH)

      # put the motor to START speed
      self.set_speed(config[motor_dir + ".SPEED_START"])

      # let the motor start to win initial inertia
      if "STARTUP_PULSE" in config:
        time.sleep(config["STARTUP_PULSE"])

      # put the motor to the minimum speed
      self.set_speed(config[motor_dir + ".SPEED_MIN"])
    
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
    GPIO.output(self.config["CHANNEL_IN1"], GPIO.LOW)
    GPIO.output(self.config["CHANNEL_IN2"], GPIO.LOW)
    self.controller.set_pwm(channel = self.config["CHANNEL_PWM"], value = self.speed)
  
  def speedup(self):
    if self.direction == "N":
      return
    new_speed = self.speed + self.config["SPEED_STEP"]
    if (new_speed <= self.config[self.get_motor_dir(self.direction) + ".SPEED_MAX"]):
      self.set_speed(new_speed)      

  def slowdown(self):
    if self.direction == "N":
      return
    new_speed = self.speed - self.config["SPEED_STEP"]
    if (new_speed >= self.config[self.get_motor_dir(self.direction) + ".SPEED_MIN"]):
      self.set_speed(new_speed)