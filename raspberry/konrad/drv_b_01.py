import time
import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address=0x41)

pwm.set_pwm(4,0,370)
pwm.set_pwm(3,0,530)
time.sleep(2)
pwm.set_pwm(4,0,370)
time.sleep(0.5)
pwm.set_pwm(4,0,340)
time.sleep(5)
pwm.set_pwm(4,0,345)
time.sleep(30)
pwm.set_pwm(4,0,340)
time.sleep(60)
pwm.set_pwm(4,0,345)
time.sleep(15)
pwm.set_pwm(4,0,350)
time.sleep(15)
pwm.set_pwm(4,0,370)
pwm.set_pwm(3,0,445)



