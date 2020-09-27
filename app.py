from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL, MySQLdb
from traffic_core.model_loader import model_predict, decode_predictions
from traffic_core.video_streamer import gen_frames,traffic_video_streamer
from traffic_core.preprocessor import lbp
import numpy as np
import hashlib
import cv2
import os

app = Flask(__name__)
base_path =os.path.dirname(__file__)
app.config['SECRET_KEY']= 'ahmadsyarifuddinr'
app.config['UPLOAD_PATH']= os.path.join(base_path, 'traffic_uploads')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'diko'
app.config['MYSQL_DB'] = 'user'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

traffic_video = ''


@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')


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
        _cur = mysql.connection.cursor()
        _cur.execute("INSERT INTO profile (name, email, password) VALUES (%s,%s,%s)",
                    (name, email, passdb,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('login'))

@app.route('/traffic-file-manager')
def traffic_file_manager():
    files_list = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('traffic-file-manager.html', files_list=files_list)

@app.route('/delete-traffic-file/<filename>')
def delete_traffic_file(filename):
    file_path = os.path.join(base_path, 'traffic_uploads',secure_filename(filename))
    if os.path.exists(file_path): os.remove(file_path)
    print('file_path:' + file_path)
    print('base_path:' + base_path)
    return redirect(url_for('traffic_file_manager'))

@app.route('/predict-image', methods=['GET', 'POST'])
def upload_traffic_image():
    if request.method == 'POST':
        f = request.files['file']
        file_path = os.path.join(base_path, 'traffic_uploads', secure_filename(f.filename))
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
    global traffic_video

    if request.method == "POST":
        video = request.files["video"]
        print("Isi video :", video)
        video_name = secure_filename(video.filename)
        video_path = os.path.join(base_path, 'traffic_uploads', video_name)
        video.save(video_path) 
        traffic_video = os.path.join(app.config['UPLOAD_PATH'], video_name)
 
        return render_template("traffic-video.html", filename=video_name)         
    else:
        return render_template("traffic-video.html")

@app.route('/traffic_video_feed')
def traffic_video_feed():

    return Response(traffic_video_streamer(traffic_video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/traffic-video-streaming', methods=['GET','POST'])
def video_streaming():
    traffic_data = {}
    if request.method == 'POST':
        if request.form['vid_src'] == '1':
            traffic_url = request.form['url']
        elif request.form['vid_src'] == '2':
            traffic_url = request.form['cctv']
        else:
            flash('Pilih sumber video terlebih dahulu')
            return redirect(request.url)
        traffic_data['input_type'] = request.form['vid_src']
        traffic_data['traffic_url'] = traffic_url

    _cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    _cur.execute("SELECT cctvId, cctvName FROM ref_cctv")
    traffic_data['cctv_ids'] = _cur.fetchall()
    _cur.close()
    
    return render_template('traffic-video-streaming.html', traffic_data=traffic_data)

@app.route('/traffic_live_feed/<input_type>/<filename>', methods=["GET", "POST"])
def traffic_live_feed(input_type, filename):
    if int(input_type) == 1:
        # traffic_url = int(filename)
        traffic_url = filename
    elif int(input_type) == 2:
        _cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        _cur.execute("SELECT * FROM ref_cctv WHERE cctvId={}".format(int(filename)))
        cctv_data = _cur.fetchone()
        _cur.close()
        if cctv_data['cctvURL'] == '':
            # rtsp://admin:adminYKQFNH@169.254.108.121
            traffic_url = '{}://{}:{}@{}:{}'.format(
                cctv_data['cctvType'],
                cctv_data['cctvUser'],
                cctv_data['cctvPassword'],
                cctv_data['cctvIp'],
                cctv_data['cctvPort']
            )
        else:
            traffic_url = cctv_data['cctvURL']
            print(traffic_url)
    
    return Response(traffic_video_streamer(traffic_url), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)