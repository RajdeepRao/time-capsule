# Std lib
from flask import Flask, render_template, request, flash, redirect, url_for, session
from functools import wraps
import ipdb
import json
import os

# 3rd party
import requests
from requests.exceptions import HTTPError

# local
from utils.firebase_admin import TimeCapsuleFirebaseAdminObj
from utils.pyrebase import TimeCapsulePyrebaseObj


app = Flask(__name__)
# Todo: Come back and env var this
app.secret_key = "super secret key"
# Init firebase obj
time_capsule_firebase_admin_obj = TimeCapsuleFirebaseAdminObj()
time_capsule_pyrebase_obj = TimeCapsulePyrebaseObj()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if session['logged_in']:
                return f(*args, **kwargs)
        else:
            flash("You need to login first", category='error')
            return redirect(url_for('login'))
    return wrap

users = [{'uid': 1, 'name': 'Noah Schairer'}]
@app.route('/api/userinfo')
@login_required
def userinfo():
    return {'data': users}, 200

@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template('index.html')

@app.route('/auth-test', methods=['GET'])
def authenticate_test():
    return {'status': 'ok'}, 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            response = time_capsule_pyrebase_obj.sign_user_in(email, password)
        except HTTPError as e:
            error_json = e.args[1]
            error_code = json.loads(error_json)['error']['code']
            error_message = json.loads(error_json)['error']['message']
            flash(f'{error_message}', category='error')
            return render_template('login.html')
        #ipdb.set_trace()
        session['logged_in'] = True
        session['email_id'] = email
        return redirect(url_for('home'))
    
    if 'logged_in' in session:
            if session['logged_in']:
                return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # Query firebase to see if user exists
        user = time_capsule_firebase_admin_obj.get_user(email)
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create new user in Firebase
            new_user = time_capsule_firebase_admin_obj.create_user(email, password1)
            flash('Account created!', category='success')
            return redirect(url_for('home'))
    
    if 'logged_in' in session:
            if session['logged_in']:
                return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    time_capsule_pyrebase_obj.sign_user_out()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)
