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
from video_streaming import *
from video_streaming_processed import *


app = Flask(__name__)
base_path = os.path.dirname(__file__)
app.config['SECRET_KEY'] = 'ahmadsyarifuddinrandiko'
app.config['UPLOAD_PATH'] = os.path.join(base_path, 'uploads')


model_path = 'model/lbp-model.h5'
model = load_model(model_path)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        file_path = os.path.join(base_path, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        preds = model_predict(file_path, model)
        pred_class = decode_predictions(preds, top=1)
        result = str(pred_class[0][0][1])
        return result
    return None

@app.route('/manage')
def manage():
    files_list = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
def open(filename):
    # file_url = photos.url(filename)
    file_path = os.path.join(base_path, 'uploads', secure_filename(filename))
    return render_template('browser.html', file_url=file_path)


@app.route('/delete/<filename>')
def delete(filename):
    # file_path = photos.path(filename)
    file_path = os.path.join(base_path, 'uploads', secure_filename(filename))
    os.remove(file_path)
    return redirect(url_for('manage'))

@app.route('/image', methods=['GET'])
def image_predict():
    return render_template('image.html')

@app.route('/video_streaming')
def video_streaming():
    return render_template('video_stream.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_processed')
def video_feed_processed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames_processed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')  

@app.route('/video')
def video_predict():
    return render_template('video.html')

if __name__ == '__main__':
    app.run(debug=True)