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

    # def generate_frame(self):
    #     global counter
    #     while True:
    #         success, frame = self.video.read()
    #         frame_raw = frame
    #         if not success:
    #             break_img_filepath = "./templates/endVideo.jpg"
    #             break_img = cv2.imread(break_img_filepath)
    #             _, jpeg_break = cv2.imencode('.jpg', break_img)
    #             return success, jpeg_break.tobytes()
    #     counter += 1
    #     frame = lbp(frame)
    #     if counter == predict_every:
    #         preds = np.zeros((287, 304, 3))
    #         for _ in range(3):
    #             preds[:, :, _] = frame[236:540, 280:567].T
    #         preds = np.expand_dims(preds, axis=0)

    #         preds = model.predict(preds)
    #         preds = decode_predictions(preds, top=1)
    #         preds = str(preds[0][0][1])
    #         counter = 0

    #         frame = cv2.putText(frame_raw, 'Kelas Kepadatan: ' + preds, (50, 100),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
    #                 2, cv2.LINE_AA)
    #         ret, buffer = cv2.imencode('.jpg', frame)
    #         frame = buffer.tobytes()
    #         yield (b'--frame\r\n'
    #                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    
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

    def get_frame_predict(self):
        global counter
        while True:
            success, frame =self.video.read()
            frame_raw = frame
            if not success:
                break

            counter += 1
            frame = lbp(frame)
        
            if counter == predict_every:
                preds = np.zeros((287, 304, 3))
                for _ in range(3):
                    preds[:, :, _] = frame[236:540, 280:567].T
                preds = np.expand_dims(preds, axis=0)

                preds = model_predict(preds)
                preds = decode_predictions(preds, top=1)
                preds = str(preds[0][0][0])
                counter = 0

                frame = cv2.putText(frame_raw, 'Kelas Kepadatan: ' + preds, (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                        2, cv2.LINE_AA)
                ret, buffer = cv2.imencode('.jpg', frame)
                return ret, buffer.tobytes()
            