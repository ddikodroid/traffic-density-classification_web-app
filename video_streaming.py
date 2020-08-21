import cv2

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