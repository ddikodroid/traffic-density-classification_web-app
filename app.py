import sys
import re
import os
import time
import hashlib
import json
from base64 import b64encode
from flask import Flask, render_template, redirect, url_for, request, Response
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

from werkzeug.utils import secure_filename
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
import tensorflow as tf
import numpy as np
from loader import *
from video_streaming import *

app = Flask(__name__)
base_path = os.path.dirname(__file__)
app.config['SECRET_KEY'] = 'ahmadsyarifuddinrandiko'
app.config['UPLOAD_PATH'] = os.path.join(base_path, 'uploads')
# app.config['UPLOAD_PATH'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads

model_path = 'model/lbp-model.h5'
# model = load_model(model_path)

# def model_predict(img_path, model):
#     img = image.load_img(img_path, target_size=(287,304))
#     x = image.img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
#     preds = model.predict(x)
#     return preds

# def decode_predictions(preds, top=4, class_list_path='model/class.json'):
#   if len(preds.shape) != 2 or preds.shape[1] != 6:
#     raise ValueError('`decode_predictions` expects '
#                      'a batch of predictions '
#                      '(i.e. a 2D array of shape (samples, 6)). '
#                      'Found array with shape: ' + str(preds.shape))
#   index_list = json.load(open(class_list_path))
#   results = []
#   for pred in preds:
#     top_indices = pred.argsort()[-top:][::-1]
#     result = [tuple(index_list[str(i)]) + (pred[i],) for i in top_indices]
#     result.sort(key=lambda x: x[2], reverse=True)
#     results.append(result)
#   print(pred)
#   return results

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

@app.route('/video_streaming')
def video_streaming():
    return render_template('video_stream.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')    


if __name__ == '__main__':
    app.run(debug=True)