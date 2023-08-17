import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import UserNotFoundError

'''
This is a Firebase Obj that we create that wraps all our firebase_admin related use cases
Create User
Get User
'''
class TimeCapsuleFirebaseAdminObj:
    def __init__(self):
        cred = credentials.Certificate("firebaseAdminConfig.json")
        self.firebase = firebase_admin.initialize_app(cred)
    
    def create_user(self, email, password):
        user = auth.create_user(email=email, password=password)
        return user
    
    def get_user(self, email):
        try:
            user = auth.get_user_by_email(email=email)
        except UserNotFoundError:
            user = None
        return user
