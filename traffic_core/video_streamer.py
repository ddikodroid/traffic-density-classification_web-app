import cv2
from traffic_core.preprocessor import *
from traffic_core.model_loader import *

counter = 0
predict_every = 1
preds = ''

def gen_frames(video):
    camera = cv2.VideoCapture(video)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def traffic_video_streamer(video):
    global counter
    camera = cv2.VideoCapture(video)
    while True:
        success, frame = camera.read()
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

            preds = model.predict(preds)
            preds = decode_predictions(preds, top=1)
            preds = str(preds[0][0][0])
            counter = 0

            frame = cv2.putText(frame_raw, 'Kelas Kepadatan: ' + preds, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                    2, cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')