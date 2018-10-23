import time
import Adafruit_PCA9685.PCA9685 as pca

pwm = pca (address = 0x41)
pwm.set_pwm_freq(60)

pwm.set_pwm(2,0,445)
pwm.set_pwm(2,0,530)
pwm.set_pwm(8,0,370)
time.sleep(2)
pwm.set_pwm(8,0,390)
time.sleep(2)
pwm.set_pwm(8,0,395)
time.sleep(2)
pwm.set_pwm(8,0,370)


