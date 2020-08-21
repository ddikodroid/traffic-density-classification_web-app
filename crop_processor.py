import cv2

def crop_process(frame):
    frame = frame[236:540, 280:567]
    return frame