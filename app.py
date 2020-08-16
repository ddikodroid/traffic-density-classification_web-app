import sys
import re
import os
import time
import hashlib
import json
from base64 import b64encode
from flask import Flask, render_template, redirect, url_for, request
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ahmadsyarifuddinrandiko'
# app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads

# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)
# patch_request_class(app)  # set maximum file size, default is 16MB

base_path = os.path.dirname(__file__)
model_path = 'model/lbp-model.h5'
model = load_model(model_path)
# model._make_predict_function()

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(287,304))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    return preds

def decode_predictions(preds, top=4, class_list_path='model/class.json'):
  if len(preds.shape) != 2 or preds.shape[1] != 6:
    raise ValueError('`decode_predictions` expects '
                     'a batch of predictions '
                     '(i.e. a 2D array of shape (samples, 6)). '
                     'Found array with shape: ' + str(preds.shape))
  index_list = json.load(open(class_list_path))
  results = []
  for pred in preds:
    top_indices = pred.argsort()[-top:][::-1]
    result = [tuple(index_list[str(i)]) + (pred[i],) for i in top_indices]
    result.sort(key=lambda x: x[2], reverse=True)
    results.append(result)
  return results


# class UploadForm(FlaskForm):
#     photo = FileField(validators=[FileAllowed(photos, 'Image Only!'), FileRequired('Choose a file!')])
#     submit = SubmitField('Upload')
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
        pred_class = decode_predictions(preds, top=2)
        result = str(pred_class[0][1][1])
        return result
    return None
# def upload_file():
#     resp = {}
#     img_file = open(app.config['UPLOADED_PHOTOS_DEST'] + "\\" + "placeholder.png", 'rb')
#     image = b64encode(img_file.read()).decode("utf-8")
    
#     form = UploadForm()
#     if form.validate_on_submit():
#         for filename in request.files.getlist('photo'):
#             name = str(time.time())
#             photos.save(filename)
            
#             saved_file = open( app.config['UPLOADED_PHOTOS_DEST'] + "\\" + filename.filename, 'rb')
#             image = b64encode(saved_file.read()).decode("utf-8")
            
#             files = {'Image': saved_file}
#             values = {'key': 'Image'}

#             r = requests.post("http://127.0.0.1:22001/models/traffic-density-1/v1/predict", files=files, data=values)
#             if r.status_code == requests.codes.ok:
#                 resp = r.json()
#                 success = True
#             else :
#                 success = False
#                 resp = {'status' : 'BAD'}
#     else:
#         success = False
#         resp = {'status' : 'BAD'}
#     return render_template('index.html', 
#                            form=form, 
#                            success=success, 
#                            response=resp, 
#                            img=image)


@app.route('/manage')
def manage_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
def open_file(filename):
    file_url = photos.url(filename)
    return render_template('browser.html', file_url=file_url)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = photos.path(filename)
    os.remove(file_path)
    return redirect(url_for('manage_file'))


if __name__ == '__main__':
    app.run(debug=True)