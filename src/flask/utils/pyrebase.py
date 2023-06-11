# This is all pseudo code
import pyrebase
from firebase_config import config
import ipdb
'''
This is a Pyrebase Obj that we create that wraps all our firebase related use cases
Sign user in
Sign user out
'''
class TimeCapsulePyrebaseObj:
    def __init__(self):
        self.pyrebase = pyrebase.initialize_app(config)
        self.auth = self.pyrebase.auth()
    
    def sign_user_in(self, email, password):
        response = self.auth.sign_in_with_email_and_password(email,password)
        return response
    
    def sign_user_out(self):
        # This is bad, but there's no Sign out functionality in pyrebase yet
        self.auth.current_user = None
        return
