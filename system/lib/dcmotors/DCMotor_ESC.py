#!/usr/bin/python

import time

class DCMotor_ESC:
  """
  DCMotor_ESC:
  Implements a brush motor controlled via an ESC connected to a PCA9685 PWM 
  signal generator
  Expects the following parameters in init:
    config: a configuration dictionary for the motor with the following 
            parameters:
      ID:               a string identifying the motor
      CHANNEL:          channel of the PWM controller where the ESC is 
                        connected
      DIRECTION:        adjust direction according to the polarity of motor 
                        cabling (1 or -1, to control that what you mean 
                        "forward" is what you expect)
      SPEED_STOP:       PWM value for speed 0 
      SPEED_STEP:       Increment amount to PWM value for a single speed 
                        increment (speed range depends on ESC)
      F.SPEED_MAX:      Forward direction PWM value for maximum speed 
      F.SPEED_MIN:      Forward direction PWM value for minimum speed
      F.SPEED_START:    Forward direction PWM value for starting speed
      B.SPEED_MAX:      Backward direction PWM value for maximum speed 
      B.SPEED_MIN:      Backward direction PWM value for minimum speed 
      B.SPEED_START:    Backward direction PWM value for starting speed 
      CHANGE_DIR_PAUSE: (optional) seconds to wait when switching direction 
                        from forward to backward or viceversa
      STARTUP_PULSE:    (optional) seconds to keep the motor in start position 
                        (when starting) before going at minimum speed   
      SERVO.CHANNEL:    Motor can be optionally associated to a servo which 
                        should change position according to the direction we 
                        are moving. 
                        This value represents the channel of the PWM 
                        controller where the Servo is connected
      SERVO.POS_N:      PWM value controlling the position of the servo when 
                        DC is stopped   
      SERVO.POS_B:      PWM value controlling the position of the servo when 
                        DC is moving backward
      SERVO.POS_F:      PWM value controlling the position of the servo when 
                        DC is moving forward

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

  def get_step(self, direction):
  # get the step of increments depending on motor cabling and current direction
    step_dir = 1 
    motor_dir = "F"
    if self.config["DIRECTION"] == 1:
      motor_dir = direction
    elif direction != "B":
      motor_dir = "B"

    if motor_dir == "B": step_dir = -1

    return motor_dir, step_dir

  def set_speed(self, speed):
  # Set the speed of the motor      
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
