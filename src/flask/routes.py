# Std lib
from flask import Flask, render_template, request, flash, redirect, url_for, session
from functools import wraps
import ipdb
import json
import os

# 3rd party
import requests
from requests.exceptions import HTTPError
import boto3
from temp_secrets import aws_secrets # Todo: use param store or something in prod
import datetime

# local
from utils.firebase_admin import TimeCapsuleFirebaseAdminObj
from utils.pyrebase import TimeCapsulePyrebaseObj
from utils.signed_cf_url_helper import generate_signed_urls
from temp_secrets import FLASK_SECRET_KEY

app = Flask(__name__)
# Todo: Come back and env var this
app.secret_key = FLASK_SECRET_KEY
# Init firebase obj
time_capsule_firebase_admin_obj = TimeCapsuleFirebaseAdminObj()
time_capsule_pyrebase_obj = TimeCapsulePyrebaseObj()
s3_client = boto3.client('s3',
                aws_access_key_id=aws_secrets['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=aws_secrets['AWS_SECRET_ACCESS_KEY'],
                region_name='us-east-1')
BUCKET_NAME='time-capsule-media'
VIDEO_FILE_FORMATS = ['mp4']
IMAGE_FILE_FORMATS = ['jpg','jpeg','png','gif','svg']

# To render the base app nav bar based on user session
@app.context_processor
def is_logged_in():
    if 'logged_in' not in session:
        return dict(logged_in=False)
    return dict(logged_in=session['logged_in'], user_email=session['email_id'])

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

def extract_date(date_obj):
    return str(date_obj).split(' ')[0]

def get_user_content(user_id):
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=user_id
    )
    contents = response['Contents']
    content_urls = {
        'images':[],
        'videos':[],
        'text':[]
        }
    for content in contents:
        if content['Size']>0:
            key = content['Key']
            key_lower = key.lower()
            file_format = key_lower.split('.')[-1]
            signed_url = generate_signed_urls(key)
            date_modified = extract_date(content['LastModified'])
            if file_format in VIDEO_FILE_FORMATS:
                content_urls['videos'].append({'url':signed_url, 'title': key.split('/')[-1], 'date_modified':date_modified})
            elif file_format in IMAGE_FILE_FORMATS:
                content_urls['images'].append({'url':signed_url, 'title': key.split('/')[-1], 'date_modified':date_modified})
            else:
                content_urls['text'].append({'url':signed_url, 'title': key.split('/')[-1], 'date_modified':date_modified})
    content_urls['videos'] = sorted(content_urls['videos'], key=lambda c:c['date_modified'], reverse=True)
    content_urls['images'] = sorted(content_urls['images'], key=lambda c:c['date_modified'], reverse=True)
    content_urls['text'] = sorted(content_urls['text'], key=lambda c:c['date_modified'], reverse=True)
    print(content_urls)
    return content_urls

@app.route('/', methods=['GET'])
@login_required
def home():
    print(session)
    content_urls = get_user_content(session['user_id'])
    return render_template('index.html', content_urls=content_urls)

@app.route('/_meta', methods=['GET'])
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
        session['user_id'] = response['localId']
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
            session['logged_in'] = True
            session['email_id'] = email
            firebase_user_id = new_user.uid
            session['user_id'] = firebase_user_id
            s3_client.put_object(Bucket=BUCKET_NAME, Key=(firebase_user_id+'/'))
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
