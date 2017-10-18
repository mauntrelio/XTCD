import time
import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address=0x41)


#NAV camera
pwm.set_pwm(0,0,230)
pwm.set_pwm(1,0,230)

#light

pwm.set_pwm(6,0,0)
pwm.set_pwm(7,0,4095)
pwm.set_pwm(8,0,0)
pwm.set_pwm(9,0,4095)
pwm.set_pwm(10,0,4095)
pwm.set_pwm(11,0,4095)

#prepare ESC
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)

#go backward
#accelerate
pwm.set_pwm(4,0,350)
time.sleep(1)
pwm.set_pwm(4,0,349)
time.sleep(1)
pwm.set_pwm(4,0,348)
time.sleep(1)
pwm.set_pwm(4,0,347)
time.sleep(1)
pwm.set_pwm(4,0,346)
time.sleep(1)
pwm.set_pwm(4,0,345)
time.sleep(1)
pwm.set_pwm(4,0,344)
time.sleep(1)
pwm.set_pwm(4,0,343)
time.sleep(1)
pwm.set_pwm(4,0,342)
time.sleep(1)
pwm.set_pwm(4,0,341)
time.sleep(1)

#travel
pwm.set_pwm(4,0,335)
time.sleep(90)

#slow down
pwm.set_pwm(4,0,341)
time.sleep(1)
pwm.set_pwm(4,0,342)
time.sleep(1)
pwm.set_pwm(4,0,343)
time.sleep(1)
pwm.set_pwm(4,0,344)
time.sleep(1)
pwm.set_pwm(4,0,345)
time.sleep(1)
pwm.set_pwm(4,0,346)
time.sleep(1)
pwm.set_pwm(4,0,347)
time.sleep(1)
pwm.set_pwm(4,0,348)
time.sleep(1)
pwm.set_pwm(4,0,349)
time.sleep(1)
pwm.set_pwm(4,0,350)
time.sleep(1)

#stop
pwm.set_pwm(4,0,370)
time.sleep(3)
pwm.set_pwm(3,0,445)

# start 3105
# finish 