import Adafruit_PCA9685.PCA9685 as pca
pwm = pca (address = 0x41)
pwm.set_pwm(6,0,4095)
pwm.set_pwm(7,0,4095)
pwm.set_pwm(8,0,4095)
pwm.set_pwm(9,0,4095)
pwm.set_pwm(10,0,4095)
pwm.set_pwm(11,0,4095)