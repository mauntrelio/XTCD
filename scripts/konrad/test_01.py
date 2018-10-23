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

#go bckward

pwm.set_pwm(4,0,350)
time.sleep(15)
pwm.set_pwm(4,0,345)
time.sleep(30)
pwm.set_pwm(4,0,350)
time.sleep(15)

#stop
pwm.set_pwm(4,0,370)
time.sleep(10)
pwm.set_pwm(3,0,445)
time.sleep(30)

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
pwm.set_pwm(4,0,394)
time.sleep(35)
pwm.set_pwm(4,0,395)
time.sleep(15)

#stop
pwm.set_pwm(4,0,370)
time.sleep(10)
pwm.set_pwm(3,0,445)
time.sleep(30)

#prepare ESC
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)

#go bckward

pwm.set_pwm(4,0,350)
time.sleep(15)
pwm.set_pwm(4,0,345)
time.sleep(30)
pwm.set_pwm(4,0,350)
time.sleep(15)

#stop
pwm.set_pwm(4,0,370)
time.sleep(10)
pwm.set_pwm(3,0,445)
time.sleep(30)

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
pwm.set_pwm(4,0,394)
time.sleep(30)
pwm.set_pwm(4,0,395)
time.sleep(15)

#stop
pwm.set_pwm(4,0,370)
time.sleep(10)
pwm.set_pwm(3,0,445)
time.sleep(30)

#prepare ESC
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)

#go bckward

pwm.set_pwm(4,0,350)
time.sleep(15)
pwm.set_pwm(4,0,345)
time.sleep(30)
pwm.set_pwm(4,0,350)
time.sleep(15)

#stop
pwm.set_pwm(4,0,370)
time.sleep(30)
pwm.set_pwm(3,0,445)
time.sleep(30)

#prepare ESC
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)

#go forward

pwm.set_pwm(4,0,395)
time.sleep(120)
pwm.set_pwm(4,0,394)
time.sleep(60)
pwm.set_pwm(4,0,395)
time.sleep(180)

#stop
pwm.set_pwm(4,0,370)
time.sleep(30)
pwm.set_pwm(3,0,445)

# registered position
# start about 3330
# finish ?