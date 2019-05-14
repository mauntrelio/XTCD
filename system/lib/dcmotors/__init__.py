"""
This package implements DC Motor helper classes each one with a different controller.
Each DC Motor class must implement the following methods:
  - forward (move the motor forward)
  - back (move the motor backward)
  - stop (stop the motor)
  - speedup (speed up the motor of a speed step)
  - slowdown (slow down the motor of a speed step)
"""

from DCMotor_ESC import DCMotor_ESC
from DCMotor_HAT import DCMotor_HAT
from DCMotor_L298N import DCMotor_L298N
