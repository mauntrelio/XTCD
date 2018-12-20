# import the necessary packages
import time
import cv2
import cv2.aruco as aruco

from random import randint

class Detector:
  def __init__(self):
    pass

  def search(self, code=None, timeout=10):
    time.sleep(randint(1, 5))
    return True, [20, 30, 40, 50, 60][randint(0,4)]

# # Constant parameters used in Aruco methods
# ARUCO_PARAMETERS = aruco.DetectorParameters_create()
# ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_6X6_1000)
# 
# # Create vectors we'll be using for rotations and translations for postures
# rvecs, tvecs = None, None
# 
# cam = cv2.VideoCapture(0)
# cam.set(3,400)
# cam.set(4,300)
# 
# while(True):
#     # Capturing each frame of our video stream
#     print "FPS: {}".format(cam.get(5))
#     ret, QueryImg = cam.read()
#     if ret == True:
#         # grayscale image
#         gray = cv2.cvtColor(QueryImg, cv2.COLOR_BGR2GRAY)
#     
#         # Detect Aruco markers
#         corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMETERS)
#         
#         # Make sure all 5 markers were detected before printing them out
#         if ids is not None and len(ids) == 5:
#             # Print corners and ids to the console
#             for i, corner in zip(ids, corners):
#                 print('ID: {}; Corners: {}'.format(i, corner))
# 
#             # Outline all of the markers detected in our image
#             QueryImg = aruco.drawDetectedMarkers(QueryImg, corners, borderColor=(0, 0, 255))
# 
#             # Wait on this frame
#             if cv2.waitKey(0) & 0xFF == ord('q'):
#                 break
# 
#         # Display our image
#         cv2.imshow('QueryImage', QueryImg)
# 
# 
#     # Exit at the end of the video on the 'q' keypress
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# 
# cv2.destroyAllWindows()
# 