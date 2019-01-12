#!/usr/bin/python

import time

# This file implements DC Motor helper classes each one with a different controller.
# Each DC Motor class must implement the following methods:
#   - forward (move the motor forward)
#   - back (move the motor backward)
#   - stop (stop the motor)
#   - speedup (speed up the motor of a speed step)
#   - slowdown (slow down the motor of a speed step)
#

# DCMotor_ESC:
# Implements a brush motor controlled via an ESC connected to a PWM signal generator
# Expects the following parameters:
#   config: a configuration dictionary for the motor with the following parameters:
#     CHANNEL:          channel of the PWM controller where the ESC is connected
#     DIRECTION:        adjust direction according to the polarity of motor cabling 
#                       (1 or -1, to control that what you mean "forward" is correct)
#     SPEED_STOP:       PWM value for speed 0 
#     SPEED_STEP:       Increment amount to PWM value for a single speed increment
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
#   controller: an object which control the PWM signal generator 
#               (it must implement the set_pwm method, accepting channel and PWM value as arguments)
#
#
# DCMotor_HAT:
# Implements a brush motor controlled the Raspberry Stepper Motor HAT

# DCMotor_L298N:
# Implements a brush motor controlled via an L298N connected to a PWM signal generator

class DCMotor_ESC:

  def __init__(self, config, controller):
    self.controller = controller
    self.config = config
    self.direction = "X"
    self.stop()

  def forward(self):
    self.set_direction("F")

  def back(self):
    self.set_direction("B")

  def stop(self):
    self.controller.set_pwm(channel = self.config["CHANNEL"], value = self.config["SPEED_STOP"])
    self.set_direction("N")

  def speedup(self):
    if self.direction == "N":
      return
    # increment depends on direction
    motor_dir, step_dir = self.get_step() 

    pwm_value = self.speed + step_dir * self.config["SPEED_STEP"]

    if pwm_value * step_dir <= self.config[motor_dir + ".SPEED_MAX"] * step_dir:
      self.set_speed(pwm_value)

  def slowdown(self):
    if self.direction == "N":
      return

    # decrement depends on direction
    motor_dir, step_dir = self.get_step()

    pwm_value = self.speed - step_dir * self.config["SPEED_STEP"]

    if pwm_value * step_dir >= self.config[motor_dir + ".SPEED_MIN"] * step_dir:
      self.set_speed(pwm_value)

  # get the step of increments depending on motor cabling and current direction
  def get_step(self):
    step_dir = 1 
    motor_dir = "F"
    if self.config["DIRECTION"] == 1:
      motor_dir = self.direction
    elif self.direction != "B":
      motor_dir = "B"

    if motor_dir == "B": step_dir = -1

    return motor_dir, step_dir

  # Set the speed of the motor      
  def set_speed(self, speed):
    self.controller.set_pwm(channel = self.config["CHANNEL"], value = speed)
    self.speed = speed

  def set_direction(self, direction):
    # return immediately if no change in direction
    if self.direction == direction:
      return

    # access config shorter
    config = self.config  

    # access to speed parameter x direction depending on cabling polarity:
    motor_dir = direction # by default we access the parameters of the provided direction
    if config["DIRECTION"] == -1: 
      # if the motor is cabled reversed we access the parameters of the opposite direction
      motor_dir = "F" if direction == "B" else "B"

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
        
      # if we are switching direction (from B to F or viceversa)
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
      pass

    def forward(self):
      pass

    def back(self):
      pass

    def stop(self):
      pass

    def speed_up(self):
      pass
    
    def slow_down(self):
      pass
    

class DCMotor_L298N:

    def __init__(self, config, controller):
      pass
    
    def forward(self):
      pass
    
    def back(self):
      pass

    def stop(self):
      pass
    
    def speed_up(self):
      pass

    def slow_down(self):
      pass
