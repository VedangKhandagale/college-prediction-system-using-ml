from flask import Flask, render_template, request, redirect, session, url_for
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import pickle
from pymongo import MongoClient
import hashlib
import os

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['college_prediction_2']
users_collection = db['users']

# Define a style guide
STYLE_GUIDE = {
    'typography': TYPOGRAPHY,
    'color_palette': COLOR_PALETTE
}

# Use the style guide to render the UI
@app.route('/')
def home():
    return render_template('home.html', style_guide=STYLE_GUIDE)

@app.route('/form')
def form():
    if 'username' in session:
        branch = sorted(college["branch"].unique())
        seat_type = sorted(college["seat_type"].unique())
        return render_template('form.html', branch=branch, seat_type=seat_type, style_guide=STYLE_GUIDE)
    else:
        return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' in session:
        min_rank = int(request.form.get('min_rank'))
        min_score = float(request.form.get('min_score'))
        branch = request.form.get('branch')
        seat_type = request.form.get('seat_type')

        sample_input = {
            "Min Rank": min_rank,
            "min": min_score,
            "seat_type": seat_type,
            "branch": branch,
        }
        predicted_college = predict_college(model2, sample_input)
        return str(predicted_college)
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if users_collection.find_one({'$or': [{'username': username}, {'email': email}, {'phone': phone}]}):
            return 'Username, email, or phone number already exists!'

        users_collection.insert_one({'name': name, 'email': email, 'phone': phone, 'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('signup.html', style_guide=STYLE_GUIDE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request
