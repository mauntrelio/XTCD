import time
import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address=0x41)

pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(3,0,530)
time.sleep(3)
pwm.set_pwm(4,0,370)
time.sleep(1)
pwm.set_pwm(4,0,395)
time.sleep(1)
pwm.set_pwm(4,0,370)
pwm.set_pwm(3,0,445)



