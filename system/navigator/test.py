#!/usr/bin/python

from navigator import Navigator
import time
import logging
import sys

logging.basicConfig(
  stream=sys.stdout, level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

class DroneMock:
  def __init__(self):
    pass
  
  def forward(self):
    logger.info("Drone: Forward - started")
    time.sleep(3)
    logger.info("Drone: Forward - finished")

  def back(self):
    logger.info("Drone: Back - started")
    time.sleep(3)
    logger.info("Drone: Back - finished")

  def stop(self):
    logger.info("Drone: Stop - started")
    time.sleep(3)
    logger.info("Drone: Stop - finished")

  def speedup(self):
    logger.info("Drone: SpeedUp - started")
    time.sleep(3)
    logger.info("Drone: SpeedUp - finished")

  def slowdown(self):
    logger.info("Drone: SlowDown - started")
    time.sleep(3)
    logger.info("Drone: SlowDown - finished")


def main():
  drone_mock = DroneMock()
  nav = Navigator(drone_mock)
  nav.start()

if __name__ == "__main__":
  main()