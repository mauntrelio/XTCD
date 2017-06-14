#!/usr/bin/python

import Adafruit_PCA9685
import time
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

channel = 4
start = 160
position = start

while True:
  time.sleep(5)
  if position >= 500:
    pwm.set_pwm(channel,0,start)
    time.sleep(5)
    position = start
  
  position = position + 40
  pwm.set_pwm(channel,0,position)
  
  
