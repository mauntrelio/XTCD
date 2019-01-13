#!/usr/bin/python

import time
from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
import RPi.GPIO as GPIO

# This file implements DC Motor helper classes each one with a different controller.
# Each DC Motor class must implement the following methods:
#   - forward (move the motor forward)
#   - back (move the motor backward)
#   - stop (stop the motor)
#   - speedup (speed up the motor of a speed step)
#   - slowdown (slow down the motor of a speed step)
#

# DCMotor_ESC:
# Implements a brush motor controlled via an ESC connected to a PCA9685 PWM signal generator
# Expects the following parameters in init:
#   config: a configuration dictionary for the motor with the following parameters:
#     ID:               a string identifying the motor
#     CHANNEL:          channel of the PWM controller where the ESC is connected
#     DIRECTION:        adjust direction according to the polarity of motor cabling 
#                       (1 or -1, to control that what you mean "forward" is what you expect)
#     SPEED_STOP:       PWM value for speed 0 
#     SPEED_STEP:       Increment amount to PWM value for a single speed increment (speed range depends on ESC)
#     F.SPEED_MAX:      Forward direction PWM value for maximum speed 
#     F.SPEED_MIN:      Forward direction PWM value for minimum speed
#     F.SPEED_START:    Forward direction PWM value for starting speed
#     B.SPEED_MAX:      Backward direction PWM value for maximum speed 
#     B.SPEED_MIN:      Backward direction PWM value for minimum speed 
#     B.SPEED_START:    Backward direction PWM value for starting speed 
#     CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
#                       from forward to backward or viceversa
#     STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
#                       (when starting) before going at minimum speed   
#     SERVO.CHANNEL:    Motor can be optionally associated to a servo which 
#                       should change position according to the direction we are moving. 
#                       This value represents the channel of the PWM controller where 
#                       the Servo is connected
#     SERVO.POS_N:      PWM value controlling the position of the servo when DC is stopped   
#     SERVO.POS_B:      PWM value controlling the position of the servo when DC is moving backward
#     SERVO.POS_F:      PWM value controlling the position of the servo when DC is moving forward
#
#   controller: an object which control the PCA9485 PWM signal generator 
#               (it must implement the set_pwm method, accepting channel and PWM value as arguments,
#                and the log method, accepting a string as argument)
#
# DCMotor_HAT:
# Implements a brush motor controlled via the Raspberry Stepper Motor HAT
# Expects the following parameters in init:
#   config: a configuration dictionary for the motor with the following parameters:
#     ID:               a string identifying the motor
#     CHANNEL:          channel of the PWM Stepper Motor HAT where the motor is connected
#     DIRECTION:        adjust direction according to the polarity of motor cabling 
#                       (1 or -1, to control that what you mean "forward" is what you expect)
#     SPEED_STEP:       Increment amount for a single speed increment (speed is in range 0-255)
#     F.SPEED_MAX:      Forward direction maximum speed 
#     F.SPEED_MIN:      Forward direction minimum speed
#     F.SPEED_START:    Forward direction starting speed
#     B.SPEED_MAX:      Backward direction maximum speed 
#     B.SPEED_MIN:      Backward direction minimum speed 
#     B.SPEED_START:    Backward direction starting speed 
#     CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
#                       from forward to backward or viceversa
#     STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
#                       (when starting) before going at minimum speed   
#
#   controller: the object which use the driver  
#               (at the moment it must only implement the log method, accepting a string as argument)
#
# DCMotor_L298N:
# Implements a brush motor controlled via an L298N connected to a PCA9685 PWM signal generator
# This class has direct access to GPIO!
# Expects the following parameters in init:
#   config: a configuration dictionary for the motor with the following parameters:
#     ID:               a string identifying the motor
#     CHANNEL_PWM:      channel of the PWM controller where the EN channel is connected
#     CHANNEL_IN1:      GPIO pin where the IN1 channel is connected
#     CHANNEL_IN2:      GPIO pin where the IN2 channel is connected
#     DIRECTION:        adjust direction according to the polarity of motor cabling 
#                       (1 or -1, to control that what you mean "forward" is what you expect)
#     SPEED_STEP:       Increment amount for a single speed increment (speed is in range 0-4095)
#     F.SPEED_MAX:      Forward direction PWM value for maximum speed
#     F.SPEED_MIN:      Forward direction PWM value for minimum speed
#     F.SPEED_START:    Forward direction PWM value for starting speed
#     B.SPEED_MAX:      Backward direction PWM value for maximum speed
#     B.SPEED_MIN:      Backward direction PWM value for minimum speed 
#     B.SPEED_START:    Backward direction PWM value for starting speed 
#     CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
#                       from forward to backward or vice versa
#     STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
#                       (when starting) before going at minimum speed   
#
#   controller: an object which control the PCA9485 PWM signal generator and the RPi GPIO 
#               (it must implement the set_pwm method, accepting channel and PWM value as arguments,
#                and the log method, accepting a string as argument) 

class DCMotor_ESC:

  def __init__(self, config, controller):
    self.id = config["ID"]
    self.config = config
    self.controller = controller
    self.direction = "X"
    self.stop()

  def forward(self):
    self.controller.log("%s: moving forward" % self.id)
    self.go("F")

  def back(self):
    self.controller.log("%s: moving backward" % self.id)
    self.go("B")

  def stop(self):
    self.controller.log("%s: stopping!" % self.id)
    self.go("N")

  def speedup(self):
    if self.direction == "N":
      return
    # increment depends on direction
    motor_dir, step_dir = self.get_step(self.direction) 

    pwm_value = self.speed + step_dir * self.config["SPEED_STEP"]

    if pwm_value * step_dir <= self.config[motor_dir + ".SPEED_MAX"] * step_dir:
      self.set_speed(pwm_value)

  def slowdown(self):
    if self.direction == "N":
      return
    # decrement depends on direction
    motor_dir, step_dir = self.get_step(self.direction)

    pwm_value = self.speed - step_dir * self.config["SPEED_STEP"]

    if pwm_value * step_dir >= self.config[motor_dir + ".SPEED_MIN"] * step_dir:
      self.set_speed(pwm_value)

  # get the step of increments depending on motor cabling and current direction
  def get_step(self, direction):
    step_dir = 1 
    motor_dir = "F"
    if self.config["DIRECTION"] == 1:
      motor_dir = direction
    elif direction != "B":
      motor_dir = "B"

    if motor_dir == "B": step_dir = -1

    return motor_dir, step_dir

  # Set the speed of the motor      
  def set_speed(self, speed):
    self.speed = speed
    self.controller.set_pwm(channel = self.config["CHANNEL"], value = speed)

  def go(self, direction):
    # return immediately if no change in direction
    if self.direction == direction:
      return

    # access config shorter
    config = self.config  

    # access to speed parameter x direction depending on cabling polarity:
    motor_dir, step_dir = self.get_step(direction)

    # As a first step, we stop the motor
    self.set_speed(config["SPEED_STOP"])
    
    if direction == "N":
      # do we have a servo controlling a switch?
      if "SERVO.CHANNEL" in config:
        self.controller.set_pwm(channel = config["SERVO.CHANNEL"], value = config["SERVO.POS_N"])
      self.direction = "N"
      
    # only start moving when requested direction is back or forward
    else:
      # do we have a servo controlling a power switch?
      if "SERVO.CHANNEL" in config:
        servo_position = config["SERVO.POS_%s" % motor_dir]
        self.controller.set_pwm(channel = config["SERVO.CHANNEL"], value = servo_position)
        
      # if we are switching direction (from B to F or vice versa)
      if self.direction != "N":
        # wait after switching
        if "CHANGE_DIR_PAUSE" in config:
          time.sleep(config["CHANGE_DIR_PAUSE"])

      # set the new current direction
      self.direction = direction

      # put the motor to START speed
      self.set_speed(config[motor_dir + ".SPEED_START"])

      # let the motor start to win initial inertia
      if "STARTUP_PULSE" in config:
        time.sleep(config["STARTUP_PULSE"])

      # put the motor to the minimum speed
      self.set_speed(config[motor_dir + ".SPEED_MIN"])

class DCMotor_HAT:

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
      motor_dir = direction # by default we access the parameters of the provided direction
      if self.config["DIRECTION"] == -1: 
        # if the motor is cabled reversed we access the parameters of the opposite direction
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
    
class DCMotor_L298N:

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
