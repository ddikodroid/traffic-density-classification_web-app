from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from flask_mysqldb import MySQL, MySQLdb  # untuk koneksi ke mySQL
import hashlib  # library enkripsi password
from camera import VideoCamera
import os, cv2
from werkzeug.utils import secure_filename

# konfigurasi flask dan mySQL
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'loginflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# variable template matching
linkVideo = ''
linkQuery = ''
filenamevideo = ''
metode = ''
vc = object
count = 0


app.config["IMAGE_UPLOADS"] = "./data"

# route ke home.html
@app.route('/')
def home():
    return render_template("home.html")

# route login.html
@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        # mendapatkan data login
        email = request.form['email']
        password = request.form['password']
        encryptpass = hashlib.md5(password.encode())
        passdb = encryptpass.hexdigest()
        # koneksi mySQL
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # eksekusi query
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        # simpan data ke variabel user
        user = cur.fetchone()
        cur.close()

        # jika nama user ada yang sama, cek password. Jika tidak, user error
        if user is not None:
            if passdb == user["password"]:
                # session user
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
    # clear session browser
    session.clear()
    return render_template("home.html")

# route register dan pendaftaran
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # mendapatkan data register
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        encryptpass = hashlib.md5(password.encode())
        passdb = encryptpass.hexdigest()
        # membuka dan eksekusi ke SQL
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                    (name, email, passdb,))
        mysql.connection.commit()
        # session user
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        # redirect ke home
        return redirect(url_for('home'))

# Route ke upload data template matching
@app.route("/template-matching", methods=["GET", "POST"]) # diganti template-matching
def upload_citra():
    global linkVideo
    global linkQuery
    global metode
    global vc
    global filenamevideo
    if request.method == "POST":
        query = request.files["image"]
        metode = request.form["method"]
        inputvideo = request.form["jenis_file"]

        queryimage = secure_filename(query.filename)
        query.save(os.path.join(app.config["IMAGE_UPLOADS"], queryimage))
        linkQuery = os.path.join(app.config['IMAGE_UPLOADS'], queryimage)
        if inputvideo == 'Video':
            video = request.files["video"]
            print("Isi video :", video)
            filenamevideo = secure_filename(video.filename)
            video.save(os.path.join(app.config["IMAGE_UPLOADS"], filenamevideo)) 
            linkVideo = os.path.join(app.config['IMAGE_UPLOADS'], filenamevideo)
            # print("Linkvideo Function : ", linkVideo)
        elif inputvideo == 'Link' :
            alamatVideo = request.form["videolink"] 
            if alamatVideo == "0":
                filenamevideo = "0"
                linkVideo = int(alamatVideo)
            else:
                filenamevideo = alamatVideo
                linkVideo = alamatVideo

        vc = VideoCamera(metode, linkVideo, linkQuery)           
        vc.cleanfile()   
        return render_template("templatematching.html", filename=filenamevideo)         
        # return redirect(url_for('inputvideo')) # function in main.py
    else:
        return render_template("templatematching.html")
    
def gen(camera):
    # global count
    hitung = 0
    while True:
        success, frame = camera.get_frame()
        if success:
            # cv2.putText(frame,"Video has been stopped",(0,0),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            if hitung == 1:
                break
            hitung += 1
            # break

@app.route('/video_feed')
def video_feed():
    return Response(gen(vc), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # screet keamanan enkripsi
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(host='127.0.0.1', debug=True)
