import time
import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address=0x41)

#light off

pwm.set_pwm(6,0,4095)
pwm.set_pwm(7,0,0)
pwm.set_pwm(8,0,4095)
pwm.set_pwm(9,0,4095)
pwm.set_pwm(10,0,4095)
pwm.set_pwm(11,0,0)

#prepare ESC
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)

#go forward

pwm.set_pwm(4,0,395)
time.sleep(15)
pwm.set_pwm(4,0,400)
time.sleep(180)
pwm.set_pwm(4,0,395)
time.sleep(240)

#stop
pwm.set_pwm(4,0,370)
time.sleep(30)
pwm.set_pwm(3,0,445)

# start about 2790
# finish 3249