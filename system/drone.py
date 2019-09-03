#!/usr/bin/python
# -*- coding: utf-8 -*-

import Adafruit_PCA9685.PCA9685 as pca9685
from lib.dcmotors import DCMotor_ESC, DCMotor_HAT, DCMotor_L298N
import time
import threading
import RPi.GPIO as GPIO

class Drone:

  def __init__(self, config, controller=None):

    self.config = config
    # TODO: status should be read directly interfacing to hardware
    self.status = {
      "RELAYS": {}, 
      "PWM": [None,None,None,None,
              None,None,None,None,
              None,None,None,None,
              None,None,None,None],
      "GPIO_OUT": {},
      "GPIO_IN": {}              
      }

    self.MOTORS = {}
    self.RELAYS = config["RELAYS"] if "RELAYS" in config else []
    self.KEEP_ALIVE = config["KEEP_ALIVE"] if "KEEP_ALIVE" in config else False
    
    # self.GPIO = GPIO # we set this to give access to the GPIO from
    self.GPIO_IN = {}
    self.GPIO_OUT = {}

    self.controller = controller

    # instantiate and initialize pwm controller
    self.pwm = pca9685(address=int(config["I2C_ADDR"],16))
    self.pwm.set_pwm_freq(config["FREQUENCY"])

    # start up GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # instantiate motors controllers
    for motor in config["MOTORS"]:
      if motor["TYPE"] == "ESC":
        self.MOTORS[motor["ID"]] = DCMotor_ESC(motor, self)
      elif motor["TYPE"] == "HAT":
        self.MOTORS[motor["ID"]] = DCMotor_HAT(motor, self)
      elif motor["TYPE"] == "L298N":
         self.MOTORS[motor["ID"]] = DCMotor_L298N(motor, self)
      else:
        self.log("Motor id %s: unknown type (%s)" % (motor["ID"], motor["TYPE"]), severity = 40)

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
  # possible corresponding azimuth/altitude statuses
  def set_pwm(self,**kwargs):
    channel = kwargs["channel"]
    value = kwargs["value"]
    self.log("Setting PWM on channel %s to %s" % (channel, value))
    self.pwm.set_pwm(channel, 0, value)
    self.status["PWM"][channel] = value

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
    self.log("Setting GPIO output %s to 0" % pin)
    GPIO.output(pin, 0)
    self.status["GPIO_OUT"][pin] = 0

  # set a gpio switch off
  def switch_off(self, pin):
    self.log("Setting GPIO output %s to 1" % pin)
    GPIO.output(pin, 1)
    self.status["GPIO_OUT"][pin] = 1
  
  # toggle a gpio switch
  def switch(self, pin):
    if self.status["GPIO_OUT"][pin] == 1: 
      self.switch_on(pin)
    else:
      self.switch_off(pin)

  # start moving one or more motors forward
  def forward(self, *motor_ids):
    # forward operation may require some delay: manage operation in one single thread per motor
    for motor_id in motor_ids:
      threading.Thread(target=self.MOTORS[motor_id].forward).start()

  # start moving one or more motors backward
  def back(self, *motor_ids):
    # backward operation may require some delay: manage operation in one single thread per motor
    for motor_id in motor_ids:
      threading.Thread(target=self.MOTORS[motor_id].back).start()

  # Stop one or more motors
  def stop(self, *motor_ids):
    # put motors to stop position
    for motor_id in motor_ids:
      threading.Thread(target=self.MOTORS[motor_id].stop).start()
    
  # Speed up
  def speedup(self, *motor_ids):
    for motor_id in motor_ids:
      threading.Thread(target=self.MOTORS[motor_id].speedup).start()

  # Slow down
  def slowdown(self, *motor_ids):
    for motor_id in motor_ids:
      threading.Thread(target=self.MOTORS[motor_id].slowdown).start()

  # stop ALL motors
  def stop_all(self):
    for motor_id in self.MOTORS:
      self.MOTORS[motor_id].stop()

  # move a servo to keep pwm board alive (prevent powebank poweroff)
  def keep_alive(self, position):

    if self.KEEP_ALIVE:
      if position >= self.KEEP_ALIVE["MAX"]:
        self.set_pwm(channel = self.KEEP_ALIVE["CHANNEL"], value = self.KEEP_ALIVE["MIN"])
        position = self.KEEP_ALIVE["MIN"]
        
      position = position + 40
      self.set_pwm(channel = self.KEEP_ALIVE["CHANNEL"], value = position)  

      threading.Timer(self.KEEP_ALIVE["INTERVAL"], self.keep_alive, [position]).start()  

  def shutdown(self):
  # to be called at exit
    self.stop_all()
    time.sleep(1)
    GPIO.cleanup()

  # example callback to GPIO event
  def button_press(self, pin):
    # determine if button was pressed
    value = GPIO.input(pin)
    if value == GPIO.LOW:
      self.log("GPIO input %s was set to LOW" % pin)
      # stop all motors, center camera, switch off light
      self.center()
      self.stop_all()
      self.switch_off(19)


  def stop_motor_lock(self, reading, expected, motor, direction):
    if reading == expected and self.MOTORS[motor].direction == direction:
      self.log("STOPPING %s" % motor)
      self.MOTORS[motor].stop()

  def stop_motor_locking_1(self, pin):
    value = GPIO.input(pin)
    self.log("GPIO input %s was set to %s" % (pin, value))
    self.stop_motor_lock(value, GPIO.LOW, "MOTOR_LOCK_1", "F")

  def stop_motor_unlocking_1(self, pin):
    value = GPIO.input(pin)
    self.log("GPIO input %s was set to %s" % (pin, value))
    self.stop_motor_lock(value, GPIO.LOW, "MOTOR_LOCK_1", "B")

  def stop_motor_locking_2(self, pin):
    value = GPIO.input(pin)
    self.log("GPIO input %s was set to %s" % (pin, value))
    self.stop_motor_lock(value, GPIO.LOW, "MOTOR_LOCK_2", "F")

  def stop_motor_unlocking_2(self, pin):
    value = GPIO.input(pin)
    self.log("GPIO input %s was set to %s" % (pin,value)
    self.stop_motor_lock(value, GPIO.LOW, "MOTOR_LOCK_2", "B")

  def log(self, message, severity = 20):
    self.controller.log(message, severity)
