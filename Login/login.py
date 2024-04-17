from flask import Flask, render_template, request, redirect, session, jsonify, Response
import requests
from flask_pymongo import PyMongo
import bcrypt
from bson import json_util
from bson.objectid import ObjectId
import requests
import jwt
import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/loginDB'
app.secret_key = 'mysecretkey'

mongo = PyMongo(app)

IP_SERVER = '192.168.1.54'
# IP_SERVER = '10.253.5.198'
PORT = 5555
SERVER_URL = 'http://'+IP_SERVER+':'+str(PORT)
headers = {
    'Authorization': '<token>',
    'Content-Type': 'application/json'
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/login', methods=['GET'])
def login_form():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_validation():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})
    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')):
            session['username'] = request.form['username']
            token = jwt.encode({'username': login_user['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            headers['Authorization'] = headers['Authorization'].replace('<token>', token)
            return redirect('/dashboard')
    return 'Invalid username or password'

@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        headers['Authorization'] = '<token>'
        return 'Logged Out! See you, ' + session.pop('username')
    else:
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        # return 'You are logged in as ' + session['username']
        return redirect('dashboard/show')
    return redirect('/')

@app.route('/dashboard/add', methods=['POST'])
def add():
    content = request.form['content']
    data = {'content': content}

    if data:
        response = requests.post(SERVER_URL+'/add', headers=headers, json=data)
        return render_template('dashboard.html', status=response.json())
    else:
        response = jsonify({'error': 'the message was empty'})
        return render_template('dashboard.html', status=response)

@app.route('/dashboard/remove/<_id>', methods=['DELETE'])
def remove(_id):
    response = requests.delete(SERVER_URL+f'/remove/{_id}', headers=headers)
    return response.json()

@app.route('/dashboard/show', methods=['GET'])
def show():
    response = requests.get(SERVER_URL+'/show')
    return render_template('dashboard.html', books=response.json())

@app.route('/dashboard/show/<_id>', methods=['GET'])
def show_from_id(_id):
    response = requests.get(SERVER_URL+f'/show/{_id}', headers=headers)
    return response.json()

@app.route('/dashboard/update/<_id>', methods=['PUT'])
def update(_id):
    content = request.json['content']
    data = {'content': content}

    response = requests.put(SERVER_URL+f'/update/{_id}', headers=headers, json=data)
    return response.json()

if __name__ == '__main__':
    # HOST = '10.253.5.199'
    # HOST = '192.168.1.56'
    HOST = '127.0.0.1'
    app.run(debug=True, host=HOST, port=PORT)