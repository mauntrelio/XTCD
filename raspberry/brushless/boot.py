#!/usr/bin/python

import Adafruit_PCA9685
import time, curses

i2c = 0x41
freq = 60
channel = 8

pwm = Adafruit_PCA9685.PCA9685(address=i2c)

# here the values are the secs of duration
# of the pulse... does it work for any ESC?

# max and min for the setup
pulse_max = int(0.00225 * 4096 * freq)
pulse_min = int(0.00133 * 4096 * freq)

# max and min speed found by tests
# need more current / tests / hw to probe RPM
vmax = int(0.00215 * 4096 * freq)
vmin = int(0.001367 * 4096 * freq)
vmed = int((vmax + vmin) / 2)

# step of increments during the setup phase
# with a total of 30 increments, every signal
# lasting 0.1 secs
inc = (pulse_max - pulse_min) / 30

pwm.set_pwm_freq(freq)

def bootup():
  boot = pulse_min
  while boot < pulse_max:
    print "setting pwm to %s" % boot
    pwm.set_pwm(channel,0,boot)
    boot += inc
    time.sleep(0.1)
  print "sleeping 2 seconds..."
  time.sleep(2)
  while boot > pulse_min:
    boot -= inc
    print "setting pwm to %s" % boot
    pwm.set_pwm(channel,0,boot)
    time.sleep(0.1)


if __name__ == "__main__":

  print "arming the ESC"
  bootup()

  print "Should be ready, wait 3 secs..."
  time.sleep(3)

  print "setting max speed: pwm to %s" % vmax
  pwm.set_pwm(channel,0,vmax)

  time.sleep(5)

  print "setting medium speed: pwm to %s" % vmed
  pwm.set_pwm(channel,0,vmed)

  time.sleep(5)

  print "setting minimum speed: pwm to %s" % vmin
  pwm.set_pwm(channel,0,vmin)

  time.sleep(5)

  print "stopping motor: pwm to %s" % pulse_min
  pwm.set_pwm(channel,0,pulse_min)
