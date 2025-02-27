from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['SECRET_KEY'] = ''

# MongoDB Configuration
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask_app'
app.config['MONGO_URI'] = ''
mongo = PyMongo(app)
users_collection = mongo.db.users
attacks_collection = mongo.db.attacks
socketio = SocketIO(app)
login_manager = LoginManager(app)
counter_collection = mongo.db.counter
traffic_collection = mongo.db.traffic_collection


