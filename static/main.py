import os
import time
import requests
from base64 import b64encode

from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


app = Flask(__name__)
app.config['SECRET_KEY'] = 'deepcognition API test'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/' # you'll need to create a folder named uploads

API_URL = 'http://127.0.0.1:22001/models/traffic-density/v1/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image Only!'), FileRequired('Choose a file!')])
    submit = SubmitField('Upload')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    resp = {}
    img_file = open(app.config['UPLOADED_PHOTOS_DEST'] + "placeholder.png",  'rb') 
    image = b64encode(img_file.read()).decode("utf-8")
    
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('photo'):
            name = str(time.time())
            photos.save(filename)
            
            saved_file = open( app.config['UPLOADED_PHOTOS_DEST'] + filename.filename, 'rb')
            image = b64encode(saved_file.read()).decode("utf-8")
            
            files = {'Image': saved_file}
            values = {'key': 'Image'}

            r = requests.post(API_URL, files=files, data=values)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                success = True
            else :
                success = False
                resp = {'status' : 'BAD'}
    else:
        success = False
        resp = {'status' : 'BAD'}
    return render_template('index.html', 
                           form=form, 
                           success=success, 
                           response=resp, 
                           img=image)


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
    app.run()