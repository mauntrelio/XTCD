from multiprocessing import Process
from controller import Controller
import logging

logger = logging.getLogger(__name__)

class Navigator:

  def __init__(self, drone_ref):
    self.drone_ref = drone_ref
    self.current_thread = None
    self.controller = Controller()

  def start(self):
    logger.info("Starting a processing thread ...")
    self.current_thread = Process(target=self.controller.run, args=(self.drone_ref,))
    self.current_thread.start()
    self.current_thread.join()

  def terminate(self):
    pass

  def pause(self):
    pass
