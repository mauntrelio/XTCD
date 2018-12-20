from detector import Detector
import logging
import time

logger = logging.getLogger(__name__)
MARK_CODE_REDUCTION = 20
MARK_CODE_ENDING_CHECKPOINT = 60
MARK_CODE_CHECKPOINT_MIN = 40
MARK_CODE_CHECKPOINT_MAX = 60

class Controller:
  def __init__(self):
    self.detector = Detector()
    self.drone_ref = None
  
  def run(self, drone_ref):
    self.drone_ref = drone_ref

    ending_mark_not_founded = True

    while ending_mark_not_founded:
      self.drone_ref.forward()
      self.drone_ref.speedup()

      checkpoint_founded = False
      while not checkpoint_founded:
        mark_code = self.mark_searching()

        if self.__is_reduction_mark(mark_code):
          self.drone_ref.slowdown()
          continue
      
        if self.__is_checkpoint_mark(mark_code):
          self.drone_ref.stop()
          self.take_picture()
          checkpoint_founded = True

        if self.__is_ending_checkpoint_mark(mark_code):
          ending_mark_not_founded = False

    logger.info("End of the journey")


  def take_picture(self):
    logger.info("Taking a picture")
    time.sleep(1)
  
  def mark_searching(self):
    mark_founded = False
    while not mark_founded:
      mark_founded, mark_code = self.detector.search()

    logger.info("Mark: {} founded".format(mark_code))
    return mark_code

  def __is_reduction_mark(self, code):
    if code == MARK_CODE_REDUCTION:
      logger.info(" - recognized reduction mark")
      return True
    
    return False

  def __is_checkpoint_mark(self, code):
    if code >= MARK_CODE_CHECKPOINT_MIN and code <= MARK_CODE_CHECKPOINT_MAX:
      logger.info(" - recognized checkpoint mark")
      return True
    
    return False

  def __is_ending_checkpoint_mark(self, code):
    if code == MARK_CODE_ENDING_CHECKPOINT:
      logger.info(" - recognized ending checkpoint mark")
      return True

    return False

  # forward
  # back
  # stop
  # speedup
  # slowdown