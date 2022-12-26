import pyrebase

config = {
  "apiKey": "AIzaSyDzJaFxs8pg_r7-3AEf-JH6CuBv1Y83vGk",
  "authDomain": "time-capsule-66dc4.firebaseapp.com",
  "projectId": "time-capsule-66dc4",
  "storageBucket": "time-capsule-66dc4.appspot.com",
  "messagingSenderId": "519401308847",
  "appId": "1:519401308847:web:7a5a580d5396d59780ca5a",
  "measurementId": "G-52M0T7G4HN",
  "databaseURL": ""
}

def auth():
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    email = 'test@123.com'
    password = 'password'

    user = auth.create_user_with_email_and_password(email, password)
    print(user)