from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
from werkzeug.security import check_password_hash
from flask import render_template
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "http://18.143.253.37"}})


class TempCredentials(db.Model):
    __tablename__ = 'temp_credentials'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)  # Store hashed passwords for security

class RoomDemoUtf(db.Model):
    __tablename__ = 'room_demo_utf8'

    CODE = db.Column(db.String, primary_key=True)
    BUILD = db.Column(db.String)
    FLOOR = db.Column(db.String)
    NAME = db.Column(db.String)

    def json(self):
        return {'CODE': self.CODE, 'BUILD': self.BUILD, 'FLOOR': self.FLOOR, 'NAME': self.NAME}


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def json(self):
        return {'id': self.id,'username': self.username, 'email': self.email}

db.create_all()

# Log in without Hash
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = TempCredentials.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            token = user.username + ":" + user.password  # Example token generation
            return make_response(jsonify({'message': 'Login successful', 'token': token}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid username or password'}), 401)
    except Exception as e:
        return make_response(jsonify({'message': f'Error during login: {str(e)}'}), 500)

@app.route('/register', methods=['GET'])
def register():
    token = request.args.get('token')
    if token:
        username, password = token.split(':')
        user = TempCredentials.query.filter_by(username=username, password=password).first()
        if user:
            room_info = RoomDemoUtf.query.filter_by(CODE=user.username).first()
            if room_info:
                return jsonify({'room_info': room_info.json()})
            else:
                return jsonify({'message': 'Room info not found'}), 404
        else:
            return jsonify({'message': 'Invalid token'}), 401
    else:
        return jsonify({'message': 'Token required'}), 400

# Log in with Hash
@app.route('/login_hash', methods=['POST'])
def login_hash():
    try:
        data = request.get_json()
        user = TempCredentials.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            # Assuming successful login, add user to the users table
            new_user = User(username=user.username, email='default@email.com')
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify({'message': 'Login successful, user added to users table'}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid username or password'}), 401)
    except Exception as e:
        return make_response(jsonify({'message': 'Error during login'}), 500)

@app.route('/')
def index():
    return render_template('index.html')

#create a test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)


# create a user
@app.route('/users', methods=['POST'])
def create_user():
  try:
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'message': 'user created'}), 201)
  except e:
    return make_response(jsonify({'message': 'error creating user'}), 500)

# get all users
@app.route('/users', methods=['GET'])
def get_users():
  try:
    users = User.query.all()
    return make_response(jsonify([user.json() for user in users]), 200)
  except e:
    return make_response(jsonify({'message': 'error getting users'}), 500)

# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      return make_response(jsonify({'user': user.json()}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except e:
    return make_response(jsonify({'message': 'error getting user'}), 500)

# update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      data = request.get_json()
      user.username = data['username']
      user.email = data['email']
      db.session.commit()
      return make_response(jsonify({'message': 'user updated'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except e:
    return make_response(jsonify({'message': 'error updating user'}), 500)

# delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      db.session.delete(user)
      db.session.commit()
      return make_response(jsonify({'message': 'user deleted'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except e:
    return make_response(jsonify({'message': 'error deleting user'}), 500)
