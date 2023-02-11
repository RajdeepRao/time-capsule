import pyrebase
from firebase_config import config

def auth():
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()

    email = 'test@1234.com'
    password = 'password'

    user = auth.create_user_with_email_and_password(email, password)
    print(user)