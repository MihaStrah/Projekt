from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
import os
import logging
from izbaze import getSQLFlightStatus, getSQLFlightStats, getSQLFlightCodeshares

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
#print(fullpath)

server.config['SECRET_KEY'] = readAPIKey()
server.config['SQLALCHEMY_DATABASE_URI'] = (fullpath)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(server)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)


db.create_all()
#print('db created or opened')


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, server.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@server.route('/login', methods=['POST'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        exp = (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).isoformat()
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': exp},
            server.config['SECRET_KEY'])
        print(exp)
        return jsonify({'token': token.decode('UTF-8'), 'expires': exp})


    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


#let
@server.route('/let/<datum>/<stlet>', methods=['GET'])
@token_required
def get_let(current_user,datum,stlet):
    #print(datum)
    #print(stlet)
    letinfo = getSQLFlightStatus(stlet,datum)
    #print(letinfo)
    return (letinfo)

#letstat7day
@server.route('/stat7/<stlet>', methods=['GET'])
@token_required
def get_letstat7day(current_user,stlet):
    #print(stlet)
    letstat7dayinfo = getSQLFlightStats(stlet,7)
    #print(letstat7dayinfo)
    return (letstat7dayinfo)

#letstat7day
@server.route('/stat30/<stlet>', methods=['GET'])
@token_required
def get_letstat30day(current_user,stlet):
    #print(stlet)
    letstat30dayinfo = getSQLFlightStats(stlet,30)
    #print(letstat30dayinfo)
    return (letstat30dayinfo)


#letcodeshares
@server.route('/codeshares/<datum>/<stlet>', methods=['GET'])
@token_required
def get_letcodeshares(current_user,datum,stlet):
    #print(datum)
    #print(stlet)
    letcodeshares = getSQLFlightCodeshares(stlet,datum)
    print(letcodeshares)
    return (letcodeshares)




#testno
#letcodesharesOPEN!!!
@server.route('/open/codeshares/<datum>/<stlet>', methods=['GET'])
def get_letcodesharesopen(datum,stlet):
    #print(datum)
    #print(stlet)
    letcodeshares = getSQLFlightCodeshares(stlet,datum)
    #print(letcodeshares)
    return (letcodeshares)



#if __name__ == '__main__':
#   server.run()

