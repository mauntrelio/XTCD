import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address = 0x41)
pwm.set_pwm_freq(60)

pwm.set_pwm(0,0,350)
pwm.set_pwm(0,0,352)
pwm.set_pwm(0,0,354)
pwm.set_pwm(0,0,356)
pwm.set_pwm(0,0,358)
