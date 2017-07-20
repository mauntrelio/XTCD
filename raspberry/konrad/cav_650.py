import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address = 0x41)
pwm.set_pwm_freq(60)

pwm.set_pwm(1,0,650)


