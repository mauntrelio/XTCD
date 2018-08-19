#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_PCA9685.PCA9685 as pca9685
import time
import threading
import RPi.GPIO as GPIO

class Drone:

  def __init__(self, config):

    self.config = config
    # TODO: status should be read directly interfacing to hardware
    self.status = {
      "SPEEDS": {}, 
      "RELAYS": {}, 
      "PWM": [None,None,None,None,
              None,None,None,None,
              None,None,None,None,
              None,None,None,None],
      "GPIO_OUT": {},
      "GPIO_IN": {}              
      }

    self.MOTORS = config["MOTORS"] if "MOTORS" in config else []
    self.RELAYS = config["RELAYS"] if "RELAYS" in config else []
    self.KEEP_ALIVE = config["KEEP_ALIVE"] if "KEEP_ALIVE" in config else False
    self.GPIO_IN = {}
    self.GPIO_OUT = {}

    # instantiate and initialise pwm controller
    self.pwm = pca9685(address=int(config["I2C_ADDR"],16))
    self.pwm.set_pwm_freq(config["FREQUENCY"])

    # put motors to stop position
    for motor in self.MOTORS:
      self.set_pwm(channel = motor["CHANNEL"], value = motor["SPEED_STOP"])
      self.status["SPEEDS"][motor["CHANNEL"]] = motor["SPEED_STOP"]
      # put direction switches to neutral position
      if motor["SERVO"]:
        self.set_pwm(channel = motor["SERVO"]["CHANNEL"], value = motor["SERVO"]["POS_N"])
    
    self.status["DIRECTION"] = "N"

    # start up GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # set pwm relays OFF
    for i in xrange(len(self.RELAYS)):
      relay = self.RELAYS[i]
      self.set_pwm(channel = relay["CHANNEL"], value = relay["OFF"])
      self.status["RELAYS"][i] = 0

    # set GPIO outputs to initial status
    if "GPIO_OUT" in config:
      for i in xrange(len(config["GPIO_OUT"])):
        gpio = config["GPIO_OUT"][i]
        self.GPIO_OUT[gpio["PIN"]] = gpio
        GPIO.setup(gpio["PIN"],GPIO.OUT)
        GPIO.output(gpio["PIN"], gpio["STARTUP"])
        self.status["GPIO_OUT"][gpio["PIN"]] = gpio["STARTUP"]

    # set GPIO inputs callbacks
    if "GPIO_IN" in config:
      for i in xrange(len(config["GPIO_IN"])):
        gpio = config["GPIO_IN"][i]
        self.GPIO_IN[gpio["PIN"]] = gpio
        if gpio["PULL"] == "UP":
          GPIO.setup(gpio["PIN"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        elif gpio["PULL"] == "DOWN":
          GPIO.setup(gpio["PIN"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        else:
          GPIO.setup(gpio["PIN"], GPIO.IN)
          
        if hasattr(self, gpio["CALLBACK"]):
        # the same callback is added as falling and raising. 
          # Callback itself should determine which one is the case
          GPIO.add_event_detect(gpio["PIN"], GPIO.BOTH, callback=getattr(self, gpio["CALLBACK"]), bouncetime=gpio["BOUNCE"])


    # center camera
    self.set_pwm(channel = config["AZIMUTH"]["CHANNEL"], value = config["AZIMUTH"]["NEUTRAL"])
    self.set_pwm(channel = config["ALTITUDE"]["CHANNEL"], value = config["ALTITUDE"]["NEUTRAL"])
    self.status["AZIMUTH"] = config["AZIMUTH"]["NEUTRAL"]
    self.status["ALTITUDE"] = config["ALTITUDE"]["NEUTRAL"]

  # generic set pwm method 
  # please note that this method completely bypass any check
  # and it does not update the 
  # possible corresponding azimuth/altitude/motors statuses
  def set_pwm(self,**kwargs):
    self.pwm.set_pwm(kwargs["channel"], 0, kwargs["value"])
    self.status["PWM"][kwargs["channel"]] = kwargs["value"]    

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
    self.set_pwm(channel = self.config["AZIMUTH"]["CHANNEL"], value = self.config["AZIMUTH"]["NEUTRAL"])
    self.set_pwm(channel = self.config["ALTITUDE"]["CHANNEL"], value = self.config["ALTITUDE"]["NEUTRAL"])
    self.status["ALTITUDE"] = self.config["ALTITUDE"]["NEUTRAL"]
    self.status["AZIMUTH"] = self.config["AZIMUTH"]["NEUTRAL"]

  # move the camera of one step in the desired direction and coordinate
  def step(self, coord, direction):
    step_dir = self.config[coord]["ORIENTATION"]
    channel = self.config[coord]["CHANNEL"]
    pwm_value = self.status["PWM"][channel] + direction * step_dir * self.config["MIN_STEP_POS"]
    if pwm_value <= self.config[coord]["MAX"] and pwm_value >= self.config[coord]["MIN"]:
      self.set_pwm(channel = channel, value = pwm_value)
      self.status[coord] = pwm_value

  # switch on a pwm controlled relay
  def pwm_on(self, relay):
    RELAY = self.RELAYS[relay]
    self.set_pwm(channel = RELAY["CHANNEL"], value = RELAY["ON"])
    self.status["RELAYS"][relay] = 1

  # switch off a pwm controlled relay
  def pwm_off(self, relay):
    RELAY = self.RELAYS[relay]
    self.set_pwm(channel = RELAY["CHANNEL"], value = RELAY["OFF"])
    self.status["RELAYS"][relay] = 0

  # toggle a pwm controlled relay
  def pwm_toggle(self, relay):
    if self.status["RELAYS"][relay] == 0: 
      self.pwm_on(relay)
    else:
      self.pwm_off(relay)  

  # set a gpio switch on
  def switch_on(self, pin):
    GPIO.output(pin, 1)
    self.status["GPIO_OUT"][pin] = 1

  # set a gpio switch off
  def switch_off(self, pin):
    GPIO.output(pin, 0)
    self.status["GPIO_OUT"][pin] = 0
  
  # toggle a gpio switch
  def switch(self, pin):
    if self.status["GPIO_OUT"][pin] == 0: 
      self.switch_on(pin)
    else:
      self.switch_off(pin)

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
      self.set_pwm(channel = motor["CHANNEL"], value = motor["SPEED_STOP"])
      self.status["SPEEDS"][motor["CHANNEL"]] = motor["SPEED_STOP"]
    
    self.set_direction("N")

  # Speed up
  def speedup(self):

    if self.status["DIRECTION"] == "N":
      return

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

    if self.status["DIRECTION"] == "N":
      return
      
    for motor in self.MOTORS:
      step_dir = 1 # slow down is decrease speed by default
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
    self.set_pwm(channel = motor, value = speed)
    self.status["SPEEDS"][motor] = speed

  # move forward / backward / neutral
  def set_direction(self, direction):
    if self.status["DIRECTION"] != direction:
      # stop the motors
      for motor in self.MOTORS:
        self.set_speed(motor["CHANNEL"], motor["SPEED_STOP"])
        # if brushless or neutral position requested: set direction switches in neutral position
        if motor["TYPE"] == "L" or direction == "N":
          if motor["SERVO"]:
            self.set_pwm(channel = motor["SERVO"]["CHANNEL"], value = motor["SERVO"]["POS_N"])
          self.status["DIRECTION"] = "N"
      
      # only start moving when requested direction is back or forward
      if direction != "N":
        for motor in self.MOTORS:
          if motor["SERVO"]:
            motor_dir = "F"
            if motor["DIRECTION"] == -1:
              motor_dir = "F" if direction == "B" else "B"
            # brushless: wait before switching
            if motor["TYPE"] == "L":
              time.sleep(self.config["CHANGE_DIR_PAUSE"])
            position =  motor["SERVO"]["POS_%s" % motor_dir]   
            self.set_pwm(channel = motor["SERVO"]["CHANNEL"], value = position)            
            # brush: wait after switching
            if motor["TYPE"] == "B":
              time.sleep(self.config["CHANGE_DIR_PAUSE"])

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

  # move a servo to keep pwm board alive (prevent powebank poweroff)
  def keep_alive(self, position):

    if self.KEEP_ALIVE:
      if position >= self.KEEP_ALIVE["MAX"]:
        self.set_pwm(channel = self.KEEP_ALIVE["CHANNEL"], value = self.KEEP_ALIVE["MIN"])
        position = self.KEEP_ALIVE["MIN"]
        
      position = position + 40
      self.set_pwm(channel = self.KEEP_ALIVE["CHANNEL"], value = position)  

      threading.Timer(self.KEEP_ALIVE["INTERVAL"], self.keep_alive, [position]).start()  

