import time
import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address=0x41)


#NAV camera
pwm.set_pwm(0,0,530)
pwm.set_pwm(1,0,210)

#light

pwm.set_pwm(6,0,0)
pwm.set_pwm(7,0,0)
pwm.set_pwm(8,0,4095)
pwm.set_pwm(9,0,0)
pwm.set_pwm(10,0,0)
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
pwm.set_pwm(4,0,390)
time.sleep(1)
pwm.set_pwm(4,0,391)
time.sleep(1)
pwm.set_pwm(4,0,392)
time.sleep(1)
pwm.set_pwm(4,0,393)
time.sleep(1)
pwm.set_pwm(4,0,394)
time.sleep(1)
pwm.set_pwm(4,0,395)
time.sleep(1)
pwm.set_pwm(4,0,396)
time.sleep(1)
pwm.set_pwm(4,0,397)
time.sleep(1)
pwm.set_pwm(4,0,398)
time.sleep(1)
pwm.set_pwm(4,0,399)
time.sleep(1)

#travel
pwm.set_pwm(4,0,405)
time.sleep(300)

#slow down

pwm.set_pwm(4,0,399)
time.sleep(1)
pwm.set_pwm(4,0,398)
time.sleep(1)
pwm.set_pwm(4,0,397)
time.sleep(1)
pwm.set_pwm(4,0,396)
time.sleep(1)
pwm.set_pwm(4,0,395)
time.sleep(1)
pwm.set_pwm(4,0,394)
time.sleep(1)
pwm.set_pwm(4,0,393)
time.sleep(1)
pwm.set_pwm(4,0,392)
time.sleep(1)
pwm.set_pwm(4,0,391)
time.sleep(1)
pwm.set_pwm(4,0,390)
time.sleep(1)

#stop
pwm.set_pwm(4,0,370)
time.sleep(3)
pwm.set_pwm(3,0,445)

# start 3105
# finish 