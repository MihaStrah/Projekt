from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
import os
import logging
from izbaze import getSQLFlightStatus, getSQLFlightStats

server = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="letAPI_logs_out/letAPIPythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)

def readAPIKey():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/APIKey.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    key = lines[0]
    f.close()
    return key


path = os.path.abspath(os.path.dirname(__file__))
fullpath = 'sqlite:///' + os.path.join(path, 'apiusers/APIusersDB.db')
print(fullpath)

app.config['SECRET_KEY'] = readAPIKey()
app.config['SQLALCHEMY_DATABASE_URI'] = (fullpath)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)


class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    book = db.Column(db.String(20), unique=True, nullable=False)
    country = db.Column(db.String(50), nullable=False)
    booker_prize = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

db.create_all()
print('db created')


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route('/login', methods=['POST'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': exp},
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8'), 'expires': exp})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


#let
@app.route('/let/<datum>/<stlet>', methods=['GET'])
@token_required
def get_let(current_user,datum,stlet):
    print(datum)
    print(stlet)
    letinfo = getSQLFlightStatus(stlet,datum)
    print(letinfo)
    return (letinfo)

#letstat7day
@app.route('/stat7/<stlet>', methods=['GET'])
@token_required
def get_letstat7day(current_user,stlet):
    print(stlet)
    letstat7dayinfo = getSQLFlightStats(stlet,7)
    print(letstat7dayinfo)
    return (letstat7dayinfo)

#letstat7day
@app.route('/stat30/<stlet>', methods=['GET'])
@token_required
def get_letstat30day(current_user,stlet):
    print(stlet)
    letstat30dayinfo = getSQLFlightStats(stlet,30)
    print(letstat30dayinfo)
    return (letstat30dayinfo)


#if __name__ == '__main__':
#    app.run(debug=True)


