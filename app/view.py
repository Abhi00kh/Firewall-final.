import sys
from flask import render_template, request, redirect, url_for, flash, g
from flask import stream_with_context, Response
from app import app, socketio, login_manager
from flask_login import login_user, login_required
from flask_login import UserMixin
from flask_login import LoginManager
from flask_socketio import emit, disconnect
import json
from tensorflow.keras.models import load_model
import numpy as np
import time
from flask import abort
from datetime import datetime, timedelta
import pymongo
from . import users_collection
from . import attacks_collection
from . import counter_collection 
import smtplib
import ssl
from flask import jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message



from bson import ObjectId
# Load models

xss_model = load_model('app/model/xss_model.h5')
sql_injection_model = load_model('app/model/sql_injection_model.h5')
file_inclusion_model = load_model('app/model/file_inclusion.h5')
command_injection_model = load_model('app/model/command injection.h5')
ddos_model = load_model('app/model/DDOS2.h5')
traffic_data = {}

# Attack counters
ddos_attacks = 0
xss_attacks = 0
sql_injection_attacks = 0
file_inclusion_attacks = 0
command_injection_attacks = 0

# Simplified preprocessing function for XSS, SQL Injection, File Inclusion, and Command Injection models
def preprocess_input(text):
    alphabet = " abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}"
    result = [] 
    for ch in text:
        if ch not in alphabet:
            continue
        result.append(alphabet.index(ch))
    
    # Padding to the desired max_len
    padded_sequence = result[:1000] + [0] * max(0, 1000 - len(result))
    
    return np.array(padded_sequence)

# Simplified preprocessing function for DDoS model
def preprocess_ddos_input(data):
    # Pad the sequence to the desired length (Adjust the length based on your model)
    padded_sequence = np.pad(data, ((0, 0), (0, 51 - data.shape[1]), (0, 0)), mode='constant', constant_values=0)
    return padded_sequence

# DDoS detection logic
def detect_ddos(request_data):
    global ddos_attacks
    
    if request.path == '/pages-login.html' and 'next' in request.args:
        return
    if '/static/assets/vendor/bootstrap-icons/fonts/' in request.path:
        return
    # Check if the request is a POST
    if request_data.method == 'POST':
        # Get the data from the request
        data = request_data.form

        for field, value in data.items():
            # Preprocess input for DDoS detection
            processed_input = preprocess_ddos_input(value)

            # Model inference for DDoS detection
            ddos_prediction = ddos_model.predict(np.array([processed_input]))

            # Define a threshold based on your needs
            threshold = 0.5

            # Make decision based on model prediction
            is_ddos_attack = ddos_prediction > threshold

            # If DDoS attack detected, log and block the request
            if is_ddos_attack.any():
                # Increment the counter
                ddos_attacks += int(is_ddos_attack.any())

                # Log the incident
                app.logger.warning(f"DDOS Attack detected in field '{field}' of request: {request_data.form}")

                # Store attack data in the database
                attacks_collection.insert_one({
                    "type": "ddos",
                    "field": field,
                    "request_data": request_data.form,
                    "timestamp": time.time()  # Add a timestamp for tracking
                })

                # Update the database with the latest counter values
                update_counters()

                # Emit the 'update_charts' event to update the client-side charts
                socketio.emit('update_charts', {'ddos_attacks': int(ddos_attacks)})

                # Block the request and return a 403 Forbidden response
                return error_404()

def error_404():
    return render_template('NiceAdmin/NiceAdmin/pages-error-404.html')

# Second intercept_requests function from the original code
@app.before_request
def intercept_requests():
    global xss_attacks, sql_injection_attacks, file_inclusion_attacks, command_injection_attacks

    if request.path == '/pages-login.html' and 'next' in request.args:
        return
    if '/static/assets/vendor/bootstrap-icons/fonts/' in request.path:
        return

    # Get the data from the request
    if request.method == 'POST':
        data = request.form
    elif request.method == 'GET':
        data = request.args
    else:
        data = request.data.decode('utf-8')  # For other types of requests

    attack_types = ['xss', 'sql_injection', 'file_inclusion', 'command_injection']

    for field, value in data.items():
        # Data preprocessing
        processed_input = preprocess_input(value)

        # Initialize dictionary to store model predictions for each attack type
        attack_type_predictions = {}

        for attack_type in attack_types:
            # Model inference for each attack type
            model = globals()[f"{attack_type}_model"]
            prediction = model.predict(np.array([processed_input]))

            # Store the model prediction for the current attack type
            attack_type_predictions[attack_type] = prediction

        # Print model predictions for debugging
        print(f"Predictions for field '{field}': {attack_type_predictions}")

        # Determine the attack type with maximum confidence for this field
        max_confidence_attack_type = max(attack_type_predictions, key=lambda k: np.max(attack_type_predictions[k]))

        # Get the maximum confidence for the chosen attack type
        max_confidence = np.max(attack_type_predictions[max_confidence_attack_type])

        # Print debug information
        print(f"Max confidence attack type: {max_confidence_attack_type}")
        print(f"Max confidence: {max_confidence}")

        # Check if the maximum confidence exceeds the threshold
        if max_confidence > 0.9:  # Adjust the threshold as needed
            # Increment the corresponding attack counter
            globals()[f"{max_confidence_attack_type}_attacks"] += 1

            # Log the incident
            app.logger.warning(f"{max_confidence_attack_type.capitalize()} Attack detected in field '{field}' of request: {request.form}")

            # Store attack data in the database
            attacks_collection.insert_one({
                "type": max_confidence_attack_type,
                "field": field,
                "request_data": request.form,
                "timestamp": time.time()  # Add a timestamp for tracking
            })

            # Update the database with the latest counter values
            update_counters()

            # Emit the 'update_charts' event to update the client-side charts
            socketio.emit('update_charts', {
                'xss_attacks': int(xss_attacks),
                'sql_injection_attacks': int(sql_injection_attacks),
                'file_inclusion_attacks': int(file_inclusion_attacks),
                'command_injection_attacks': int(command_injection_attacks),
                'ddos_attacks': int(ddos_attacks)
            })

            # Block the request and return a 403 Forbidden response
            return error_404()

def error_404():
    return render_template('NiceAdmin/NiceAdmin/pages-error-404.html')

# Initialize counters in the database
def initialize_counters():
    if counter_collection.count_documents({}) == 0:
        counter_collection.insert_one({
            'xss_attacks': 0,
            'sql_injection_attacks': 0,
            'file_inclusion_attacks': 0,
            'command_injection_attacks': 0,
            'ddos_attacks': 0
        })

# Update counters in the database
def update_counters():
    counter_collection.update_one({}, {'$set': {
        'xss_attacks': xss_attacks,
        'sql_injection_attacks': sql_injection_attacks,
        'file_inclusion_attacks': file_inclusion_attacks,
        'command_injection_attacks': command_injection_attacks,
        'ddos_attacks': ddos_attacks
    }}, upsert=True)

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            # Send the data to the client
            yield f'''data: {json.dumps({
                'xss_attacks': int(xss_attacks),
                'sql_injection_attacks': int(sql_injection_attacks),
                'file_inclusion_attacks': int(file_inclusion_attacks),
                'command_injection_attacks': int(command_injection_attacks),
                'ddos_attacks': int(ddos_attacks)
            })}\n\n'''
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")

login_manager = LoginManager()
login_manager.init_app(app) # app is the Flask instance
login_manager.login_view = '/pages-login.html'

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/pages-register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate form inputs (you can add more validations as needed)
        if not (name and email and username and password):
            flash("Please fill in all required fields.")
            return redirect(url_for('register'))

        # Check if the username already exists in the database
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('register'))

        # Hash the password before storing it in the database (You should use a secure hashing algorithm)
        # For demonstration purposes, we'll store the password as plain text here
        user_data = {
            "name": name,
            "email": email,
            "username": username,
            "password": password
        }

        # Insert the user data into the MongoDB collection
        result = users_collection.insert_one(user_data)

        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template('NiceAdmin/NiceAdmin/pages-register.html')

# User Login
@app.route('/pages-login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve the user from the database based on the username
        user = users_collection.find_one({"username": username})

        # Check if the user exists and the password matches
        if user and user['password'] == password:
            user_obj = User(username)
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('NiceAdmin/NiceAdmin/pages-login.html')


@app.route('/get_latest_attacks_data', methods=['GET'])
def get_latest_attacks_data():
    # Retrieve the latest 10 attack records from MongoDB, sorted by timestamp in descending order
    latest_attacks = attacks_collection.find().sort("timestamp", -1).limit(10)

    # Convert ObjectId to string for each document
    serialized_latest_attacks = []
    for attack in latest_attacks:
        attack['_id'] = str(attack['_id'])  # Convert ObjectId to string
        serialized_latest_attacks.append(attack)

    # Return the JSON response containing the latest 10 attack records
    return jsonify(serialized_latest_attacks)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
 # Fetch graph data from the database
 
 # Pass the graph data to the template rendering function
 return render_template('NiceAdmin/NiceAdmin/index.html')
@app.route('/index.html', methods=['GET', 'POST'])
@login_required
def index_html():
    # Fetch graph data from the database

    # Pass the graph data to the template rendering function
    return render_template('NiceAdmin/NiceAdmin/index.html')
@app.route('/pages-error-404.html', methods=['GET', 'POST'])
def error_404():
    return render_template('NiceAdmin/NiceAdmin/pages-error-404.html')
@app.route('/pages-faq.html', methods=['GET', 'POST'])
def faq():
    return render_template('NiceAdmin/NiceAdmin/pages-faq.html')




@app.route('/pages-contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Send email
        send_email(name, email, subject, message)

        flash('Your message has been sent. Thank you!')
        return redirect(url_for('contact'))

    return render_template('NiceAdmin/NiceAdmin/pages-contact.html')

def send_email(name, user_email, subject, message):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "samstark9990@gmail.com"
    password = "ytfs jwot ykie aesi"
    receiver_email = "samstark9990@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = f"From: {name} <{user_email}>\n\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    text = msg.as_string()

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 
