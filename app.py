from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL, MySQLdb
from traffic_utils.video_player import VideoPlayer
from traffic_utils.model_loader import model_predict, decode_predictions
from traffic_utils.video_streamer import gen_frames_processed
from traffic_utils.preprocessor import lbp
import numpy as np
import hashlib
import cv2
import os

app = Flask(__name__)
base_path =os.path.dirname(__file__)
app.config['SECRET_KEY']= 'ahmadsyarifuddinr'
app.config['UPLOAD_PATH']= os.path.join(base_path, 'uploads')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'diko'
app.config['MYSQL_DB'] = 'user'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

video_link = ''
video_name = ''
vp = object
# counter = 0
# predict_every = 5
# preds = ''

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        encryptpass = hashlib.md5(password.encode())
        passdb = encryptpass.hexdigest()
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM profile WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()

        if user is not None:
            if passdb == user["password"]:
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("home.html")
            else:
                flash("Error password and email not match", "error")
                return redirect(request.url)
        else:
            flash("Error user not found", "error")
            return redirect(request.url)
    else:
        return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        encryptpass = hashlib.md5(password.encode())
        passdb = encryptpass.hexdigest()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO profile (name, email, password) VALUES (%s,%s,%s)",
                    (name, email, passdb,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('login'))

@app.route('/predict-image', methods=['GET', 'POST'])
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

@app.route('/traffic-image', methods=['GET'])
def traffic_image():
    return render_template('traffic-image.html')

@app.route("/traffic-video", methods=["GET", "POST"])
def upload_traffic_video():
    global video_link
    global video_name
    global vp

    if request.method == "POST":
        input_video = request.form["file_type"]
        if input_video == 'Video':
            video = request.files["video"]
            print("Isi video :", video)
            video_name = secure_filename(video.filename)
            video_path = os.path.join(base_path, 'uploads', video_name)
            video.save(video_path) 
            video_link = os.path.join(app.config['UPLOAD_PATH'], video_name)
        elif input_video == 'Link' :
            video_address = request.form["video_link"] 
            if video_address == "0":
                video_name = "0"
                video_link = int(video_address)
            else:
                video_name = "CCTV Dishub Sukoharjo"
                video_link = video_address

        vp = VideoPlayer(video_link)           
        vp.clean_file()   
        return render_template("traffic-video.html", filename=video_name)         
    else:
        return render_template("traffic-video.html")
    
def gen(camera):
    counter = 0
    while True:
        success, frame = camera.get_frame_predict()
        if success:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            if counter==1:
                break
            counter += 1

@app.route('/video_file_feed')
def video_file_feed():
    return Response(gen(vp), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/traffic-video-streaming')
def video_streaming():
    return render_template('traffic-video-streaming.html')

@app.route('/video_streaming_feed')
def video_streaming_feed():
    return Response(gen_frames_processed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)