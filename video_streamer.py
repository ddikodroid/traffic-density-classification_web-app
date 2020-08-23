import cv2
from preprocessor import *
from model_loader import *
url = 'http://cctv-dishub.sukoharjokab.go.id/zm/cgi-bin/nph-zms?mode=jpeg&monitor=8&scale=150&maxfps=15&buffer=1000&user=user&pass=user'

camera = cv2.VideoCapture(url)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frames_processed():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = frame_masking(frame)
            frame = cropping(frame)
            frame = lbp(frame)
            # print(frame.shape)
            # preds = model.predict(frame)
            # preds = decode_predictions(preds, top=1)
            # preds = str(preds[0,0,1])
            # frame = cv2.putText(frame, 'OpenCV', (50, 50),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0),
            #             2, cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')