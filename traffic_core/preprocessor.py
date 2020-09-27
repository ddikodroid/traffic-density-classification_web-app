import cv2
import numpy as np
from skimage.feature import local_binary_pattern
from PIL import Image
import matplotlib.pyplot as plt

pts1 = np.array([[0,0],[680,0],[278,540],[0,540]])
pts2 = np.array([[720,0],[575,0],[560,540],[720,540]])
pts3 = np.array([[400,100],[600,100],[600,235],[400,235]])

def frame_masking(frame):
    cv2.fillPoly(frame,[pts1],(0,0,0))
    cv2.fillPoly(frame,[pts2],(0,0,0))
    cv2.fillPoly(frame,[pts3],(0,0,0))
    return frame

def lbp(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = local_binary_pattern(frame, 24, 3, method='default')
    return frame

def cropping(frame):
    frame = frame[236:540, 280:567]
    return frame