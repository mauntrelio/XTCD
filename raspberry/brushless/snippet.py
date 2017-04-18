import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x41)
pwm.set_pwm_freq(50)

channel=5
boot=250
pwm.set_pwm(channel,0,boot)
