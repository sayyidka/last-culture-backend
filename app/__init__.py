from app.helpers import *
import pymysql
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Init app, config DB & cors
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b62e924f512fdb:f8ffe693@us-cdbr-iron-east-05.cleardb.net/heroku_5b91fdc12b747b8'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()
CORS(app)


# DB Model
class Cache(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

@app.route('/', methods=['GET'])
def getHome():
    response = 'test'
    return response

# run function parameter (integer) refers to type field in cache table
@app.route('/books', methods=['GET'])
def getBooks():
    response = run(1)
    return response


@app.route('/movies', methods=['GET'])
def getMovies():
    response = run(2)
    return response


@app.route('/series', methods=['GET'])
def getSeries():
    response = run(3)
    return response


@app.route('/games', methods=['GET'])
def getGames():
    response = run(4)
    return response
