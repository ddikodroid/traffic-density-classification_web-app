import cv2
from traffic_utils.preprocessor import *
from traffic_utils.model_loader import *

counter = 0
predict_every = 5

class VideoPlayer:
    def __init__(self, file_video):
        self.file_video = file_video
        self.video = cv2.VideoCapture(self.file_video)

    def stop(self):
        self.video.release()

    def clean_file(self):
        global counter
        counter = 0

    def get_frame(self):
        global counter
        success, frame = self.video.read()
        if not success:
            break_img_filepath = "./templates/endVideo.jpg"
            break_img = cv2.imread(break_img_filepath)
            _, jpeg_break = cv2.imencode('.jpg', break_img)
            return success, jpeg_break.tobytes()
        counter+=1
        ret, jpeg = cv2.imencode('.jpg', frame)
        return success, jpeg.tobytes() 