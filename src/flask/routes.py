from flask import Flask, render_template, request
import os
from views.signup import auth

app = Flask(__name__)

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

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print('In the get')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(request)
        print(username + ' - ' + password)
    return render_template('signup.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)