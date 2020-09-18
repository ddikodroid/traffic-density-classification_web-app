import sys
import re
import os
import time
import hashlib
import json
from base64 import b64encode
from flask import Flask, render_template, redirect, url_for, request, Response

from werkzeug.utils import secure_filename
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
import tensorflow as tf
import numpy as np
from model_loader import *
from video_streamer import *
from video_player import VideoPlayer

app = Flask(__name__)
base_path = os.path.dirname(__file__)
app.config['SECRET_KEY'] = 'ahmadsyarifuddinrandiko'
app.config['UPLOAD_PATH'] = os.path.join(base_path, 'uploads')

vf = object
counter = 0

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        file_path = os.path.join(base_path, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        preds = model_predict(file_path)
        pred_class = decode_predictions(preds, top=1)
        result = str(pred_class[0][0][1])
        return result
    return None

@app.route('/predict_video', methods=['GET', 'POST'])
def upload_video():
    global vf
    if request.method == 'POST':
        v = request.files['video']
        video_name = secure_filename(v.filename)
        video_path = os.path.join(base_path, 'uploads', video_name)
        v.save(video_path)
        vf = VideoPlayer(video_path)
        vf.clean_file()
        return render_template("video.html")

def gen(camera):
    global counter
    while True:
        success, frame = camera.get_frame()
        frame_raw = frame
        if not success:
            break_img_filepath = "./templates/endVideo.jpg"
            break_img = cv2.imread(break_img_filepath)
            _, jpeg_break = cv2.imencode('.jpg', break_img)
            return success, jpeg_break.tobytes()
        counter += 1
        frame = lbp(frame)
        if counter == predict_every:
            preds = np.zeros((287, 304, 3))
            for _ in range(3):
                preds[:, :, _] = frame[236:540, 280:567].T
            preds = np.expand_dims(preds, axis=0)

            preds = model.predict(preds)
            preds = decode_predictions(preds, top=1)
            preds = str(preds[0][0][1])
            counter = 0

            frame = cv2.putText(frame_raw, 'Kelas Kepadatan: ' + preds, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                    2, cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            del camera
            break


@app.route('/manage')
def manage():
    files_list = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
def open(filename):
    file_path = os.path.join(base_path, 'uploads', secure_filename(filename))
    return render_template('browser.html', file_url=file_path)


@app.route('/delete/<filename>')
def delete(filename):
    file_path = os.path.join(base_path, 'uploads', secure_filename(filename))
    os.remove(file_path)
    return redirect(url_for('manage'))

@app.route('/image', methods=['GET'])
def image_predict():
    return render_template('image.html')

@app.route('/video', methods=['GET'])
def video_predict():
    return render_template('video.html')

@app.route('/video_streaming')
def video_streaming():
    return render_template('video_stream.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_processed')
def video_feed_processed():
    return Response(gen_frames_processed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')  

@app.route('/video_file_feed')
def video_file_feed():
    return Response(gen(vf),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)