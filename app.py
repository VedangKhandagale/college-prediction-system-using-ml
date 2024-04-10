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

# Load the trained model and college data
label_encoder = LabelEncoder()
model2 = pickle.load(open("trained_model_clg.pkl", "rb"))
college = pd.read_csv("MHTCET_RANK_last_dance_3 - MHTCET_RANK_last_dance_3.csv")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form')
def form():
    if 'username' in session:
        branch = sorted(college["branch"].unique())
        seat_type = sorted(college["seat_type"].unique())
        return render_template('form.html', branch=branch, seat_type=seat_type)
        
    else:
        return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' in session:
        min_rank = int(request.form.get('min_rank'))
        min_score = float(request.form.get('min_score'))
        branch = request.form.get('branch')
        seat_type = request.form.get('seat_type')

        def predict_college(model, sample_input):
            transformed_input = sample_input.copy()
            if isinstance(sample_input['seat_type'], str):
                if sample_input['seat_type'] == 'OPEN':
                    transformed_input['seat_type'] = 3
                elif sample_input['seat_type'] == 'OBC':
                    transformed_input['seat_type'] = 2
                elif sample_input['seat_type'] == 'SC':
                    transformed_input['seat_type'] = 4
                elif sample_input['seat_type'] == 'ST':
                    transformed_input['seat_type'] = 5
                elif sample_input['seat_type'] == 'MI':
                    transformed_input['seat_type'] = 0
                elif sample_input['seat_type'] == 'MI-MH':
                    transformed_input['seat_type'] = 1

            if isinstance(sample_input['branch'], str):
                if sample_input['branch'] == 'Computer Engineering':
                    transformed_input['branch'] = 0
                elif sample_input['branch'] == 'Information Technology':
                    transformed_input['branch'] = 3
                elif sample_input['branch'] == 'Electronics and Telecommunication Engg':
                    transformed_input['branch'] = 2
                elif sample_input['branch'] == 'Electrical Engineering':
                    transformed_input['branch'] = 1

            sample_df = pd.DataFrame(transformed_input, index=[0])
            predicted_college = model.predict(sample_df)
            return predicted_college[0]

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

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = users_collection.find_one({'username': username, 'password': hashed_password})
        if user:
            session['username'] = username
            return redirect(url_for('form'))

        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
