from flask import Flask
from flask_mysqldb import MySQL, MySQLdb
import os

app = Flask(__name__)
app.config['SECRET_KEY']= 'ahmadsyarifuddinr'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'diko'
app.config['MYSQL_DB'] = 'user'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

import views

if __name__ == "__main__":
    app.run(debug=True)