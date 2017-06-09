#!/usr/bin/python

import Adafruit_PCA9685
import time
pwm = Adafruit_PCA9685.PCA9685(address=0x40)


counter = 1
while True:
  if counter == 10:
    pwm.set_pwm(0,0,410)
    pwm.set_pwm(1,0,470)
    counter = 1
  pwm.set_pwm(7,0,4095)
  time.sleep(5)
  pwm.set_pwm(7,0,0)
  time.sleep(5)
  counter = counter + 1
  
