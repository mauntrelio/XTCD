import Adafruit_PCA9685
import time
pwm = Adafruit_PCA9685.PCA9685(address=0x41)
pwm.set_pwm_freq(50)

channel=5

max = 3000
min = 1000

for i in xrange(0,31):
  v = min + i*100
  print "setting  speed: pwm to %s" % v
  pwm.set_pwm(channel,0,v)
  time.sleep(3)


print "stopping motor: pwm to %s" % 0
pwm.set_pwm(channel,0,0)
