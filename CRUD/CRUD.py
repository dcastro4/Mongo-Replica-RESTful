from flask import Flask, render_template, request, redirect, session, jsonify, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
import bcrypt
from bson import json_util
from bson.objectid import ObjectId
import jwt
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], 'HS256')
        except:
            return jsonify({'error': 'token is invalid'}), 403

        return f(*args, **kwargs)

    return decorated

app = Flask(__name__)

# app.config['MONGO_URI'] = 'mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=myReplicaSet'
# client = MongoClient(app.config['MONGO_URI'])
# mongo = client.CRUDDB

app.config['MONGO_URI'] = 'mongodb://localhost:27017/CRUDDB'
mongo = PyMongo(app)
mongo = mongo.db

app.secret_key = 'mysecretkey'

@app.route('/')
def home():
    return redirect('/show')

@app.route('/add', methods=['POST'])
@token_required
def add():
    data = request.get_json()

    if data:
        mongo.data.insert_one(data)
        return {'message': 'successfuly saved'}
    else:
        return {'error': 'the message was empty'}

@app.route('/remove/<_id>', methods=['DELETE'])
@token_required
def remove(_id):
    data = {'_id': ObjectId(_id)}
    mongo.data.delete_one(data)
    response = jsonify({'message': 'data deleted successfuly'})
    return response

@app.route('/show', methods=['GET'])
def show():
    data = mongo.data.find()
    data = json_util.dumps(data)
    return Response(data, mimetype='application/json')

@app.route('/show/<_id>', methods=['GET'])
def show_from_id(_id):
    data = mongo.data.find_one({'_id': ObjectId(_id)})
    response = json_util.dumps(data)
    return Response(response, mimetype='application/json')

@app.route('/update/<_id>', methods=['PUT'])
@token_required
def update(_id):
    data = request.get_json()

    if data:
        mongo.data.update_one({'_id': ObjectId(_id)}, {'$set' : data})
        return jsonify({'message': 'successfuly update'})
    else:
        return jsonify({'error': 'the message was empty'})

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({'error': 'resource not found', 'status': 404})
    response.status_code = 404
    return response

if __name__ == '__main__':
    HOST = '192.168.1.54'
    # HOST = '10.253.5.198'
    PORT = 5555
    app.run(debug=True, host=HOST, port=PORT)