from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
import os
import logging
from flask_caching import Cache
from izbaze import getSQLFlightStatus, getSQLFlightStats, getSQLFlightCodeshares, getSQLFlightPastStats
from aircraftImage import getAircraftImageURL
from liveLufthansa import getFlightStatusLufthansa, getAircraftModelLufthansa, getAirlineNameLufthansa, getAirportNameLufthansa, getCodesharesLufthansa
from notificationUsers import setDatabase, registerFlight, unregisterFlight

server = Flask(__name__)

#cache for API https://pythonhosted.org/Flask-Caching/
cache = Cache(server, config={'CACHE_TYPE': 'simple'})

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="letAPI_logs_out/letAPIPythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)


#set notificationUsers database
setDatabase()


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
            return jsonify({'info': 'a valid token is missing'})

        try:
            data = jwt.decode(token, server.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'info': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator



@server.route('/login', methods=['POST'])
def login_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': exp},
            server.config['SECRET_KEY'])
        #for json in iso
        return jsonify({'token': token.decode('UTF-8'), 'expires': exp.isoformat()})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


#let
@server.route('/flight/<date>/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=432000) #cache requests for 1 day 864000s (this is historical data and should not change)
def get_flight(current_user,date,flightnumber):
    #print(date)
    #print(flightnumber)
    flightInfo = getSQLFlightStatus(flightnumber,date)
    #print(flightInfo)
    return (flightInfo)

#letstat7day
@server.route('/stat7/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=3600) #cache requests for 1 hour 3600s
def get_flightStat7day(current_user,flightnumber):
    #print(flightnumber)
    letstat7dayinfo = getSQLFlightStats(flightnumber,7)
    #print(letstat7dayinfo)
    return (letstat7dayinfo)

#letstat7day
@server.route('/stat30/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=3600) #cache requests for 1 hour 3600s
def get_flightStat30day(current_user,flightnumber):
    #print(flightnumber)
    letstat30dayinfo = getSQLFlightStats(flightnumber,30)
    #print(letstat30dayinfo)
    return (letstat30dayinfo)


#flightCodeshares
@server.route('/codeshares/<date>/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=864000) #cache requests for 1 day 864000s (this is historical data and should not change)
def get_flightCodeshares(current_user,date,flightnumber):
    #print(date)
    #print(flightnumber)
    flightCodeshares = getSQLFlightCodeshares(flightnumber,date)
    #print(flightCodeshares)
    return (flightCodeshares)

#AirplaneImageURL
@server.route('/aircraftimage/<aircraftreg>', methods=['GET'])
@token_required
@cache.cached(timeout=432000) #cache requests for 5 days 432000s
def get_aircraftImage(current_user,aircraftreg):
    #print("test")
    aircraftImageURL = getAircraftImageURL(aircraftreg)
    #print(aircraftImageURL)
    return (aircraftImageURL)

@server.route('/live/flight/<date>/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=60) #cache requests for 1 minute 60s
def get_flightstatusLive(flightnumber, date):
    #print("test")
    flightstatusLive = getFlightStatusLufthansa(flightnumber, date)
    #print(flightstatusLive)
    return (flightstatusLive)

@server.route('/info/aircraftname/<aircraftmodelcode>', methods=['GET'])
@token_required
@cache.cached(timeout=432000) #cache requests for 5 days 432000s
def get_aircraftmodelName(current_user,aircraftmodelcode):
    #print("test")
    aircraftmodelname = getAircraftModelLufthansa(aircraftmodelcode)
    #print(aircraftmodelname)
    return (aircraftmodelname)

@server.route('/info/airlinename/<airlinecode>', methods=['GET'])
@token_required
@cache.cached(timeout=432000) #cache requests for 5 days 432000s
def get_airlineName(current_user,airlinecode):
    #print("test")
    airlinename = getAirlineNameLufthansa(airlinecode)
    #print(airlinename)
    return (airlinename)

@server.route('/info/airportname/<airportcode>', methods=['GET'])
@token_required
@cache.cached(timeout=432000) #cache requests for 5 days 432000s
def get_airportName(current_user,airportcode):
    #print("test")
    airportname = getAirportNameLufthansa(airportcode)
    #print(airportname)
    return (airportname)

@server.route('/live/codeshares/<date>/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=60) #cache requests for 1 minute 60s
def get_flightCodesharesLive(current_user,date,flightnumber):
    #print(date)
    #print(flightnumber)
    flightCodeshares = getCodesharesLufthansa(flightnumber,date)
    #print(flightCodeshares)
    return (flightCodeshares)


@server.route('/statday/<flightnumber>', methods=['GET'])
@token_required
@cache.cached(timeout=60) #cache requests for 1 minute 60s
def get_flightStatDay(current_user,flightnumber):
    #print(date)
    #print(flightnumber)
    flightStatDay = getSQLFlightPastStats(flightnumber)
    #print(flightCodeshares)
    return (flightStatDay)


@server.route('/notifications/register', methods=['POST'])
@token_required
def notificationsRegister(current_user):
    if request.method == 'POST':
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        info = registerFlight(token, airline, flightnumber, date)
        return info
    return (jsonify({'info': 'REQUEST ERROR'}))

@server.route('/notifications/unregister', methods=['POST'])
@token_required
def notificationsUnregister(current_user):
    if request.method == 'POST':
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        info = unregisterFlight(token, airline, flightnumber, date)
        return info
    return (jsonify({'info': 'REQUEST ERROR'}))







#testno
#flightCodesharesOPEN!!!
#@server.route('/open/codeshares/<date>/<flightnumber>', methods=['GET'])
#def get_flightCodesharesOpen(date,flightnumber):
#    #print(date)
#    #print(flightnumber)
#    flightCodeshares = getSQLFlightCodeshares(flightnumber,date)
#    #print(flightCodeshares)
#    return (flightCodeshares)



#if __name__ == '__main__':
#   server.run(debug=True)


