from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['SECRET_KEY'] = '9b2a6b0f5906a4cd4a3a5b28b1e76c5f7a84c47a3c9ed10e3297cfdf9a5b2758'

# MongoDB Configuration
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask_app'
app.config['MONGO_URI'] = 'mongodb+srv://aditikhule:KzumuTJSPXnGCO9p@cluster0.emitdqk.mongodb.net/flask_app'
mongo = PyMongo(app)
users_collection = mongo.db.users
attacks_collection = mongo.db.attacks
socketio = SocketIO(app)
login_manager = LoginManager(app)
counter_collection = mongo.db.counter
traffic_collection = mongo.db.traffic_collection


