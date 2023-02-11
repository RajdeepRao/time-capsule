from flask import Flask, render_template, request, flash
import os
from views.signup import auth

app = Flask(__name__)
# Todo: Come back and env var this
app.secret_key = "super secret key"

users = [{'uid': 1, 'name': 'Noah Schairer'}]
@app.route('/api/userinfo')
def userinfo():
    return {'data': users}, 200

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/auth-test', methods=['GET'])
def authenticate_test():
    auth()
    return {'status': 'ok'}, 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
    return render_template('signup.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)