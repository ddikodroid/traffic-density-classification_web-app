from skimage.feature import local_binary_pattern
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2

R = 3
P = 8 * R
def lbp(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = local_binary_pattern(frame, P, R, method='default')
    return frame