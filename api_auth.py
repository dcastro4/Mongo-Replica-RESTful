from flask import Flask, jsonify, request, make_response
import jwt
import datetime
from functools import wraps

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.args.get('token')
		if not token:
			return jsonify({'error': 'token is missing'}), 403

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], 'HS256')
		except:
			return jsonify({'error': 'token is invalid'}), 403

		return f(*args, **kwargs)

	return decorated

app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/unprotected')
def unprotected():
	token = request.args.get('token')
	return jsonify({'message': 'anyone can view this'})

@app.route('/protected')
@token_required
def protected():
	return jsonify({'message': 'this is only available for people with the token'})

@app.route('/login')
def login():
	auth = request.authorization

	if auth and auth.password == 'secret':
		token = jwt.encode({'username': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
		return jsonify({'token': token})

	return make_response("Could not verify!", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

if __name__ == '__main__':
	HOST = '192.168.1.66'
	PORT = 5000

	app.run(debug=True, host=HOST, port=PORT)