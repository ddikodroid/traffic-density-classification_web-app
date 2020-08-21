import cv2
import numpy as np

pts1 = np.array([[0,0],[680,0],[278,540],[0,540]])
pts2 = np.array([[720,0],[575,0],[560,540],[720,540]])
pts3 = np.array([[400,100],[600,100],[600,235],[400,235]])

def frame_masking(frame):
    cv2.fillPoly(frame,[pts1],(0,0,0))
    cv2.fillPoly(frame,[pts2],(0,0,0))
    cv2.fillPoly(frame,[pts3],(0,0,0))
    return frame