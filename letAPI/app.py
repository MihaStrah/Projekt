from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, abort
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
from opensky import getAircraftLocation

server = Flask(__name__)
api = Api(server)

#cache for API https://pythonhosted.org/Flask-Caching/
#cache = Cache(server, config={'CACHE_TYPE': 'simple'})
cache = Cache(server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp'})
cache.clear()

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
            return abort(401, message="Missing Token")

        try:
            data = jwt.decode(token, server.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return abort(401, message="Invalid Token")

        return f(current_user, *args, **kwargs)

    return decorator



class Login(Resource):
    def post(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

        user = Users.query.filter_by(name=auth.username).first()

        if (user is None):
            return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

        if check_password_hash(user.password, auth.password):
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            token = jwt.encode(
                {'public_id': user.public_id, 'exp': exp},
                server.config['SECRET_KEY'])
            # for json in iso
            return make_response(jsonify({'token': token.decode('UTF-8'), 'expires': exp.isoformat()}), 200)

        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

api.add_resource(Login, '/login', endpoint='login')




class OldFlight(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, flightnumber, date):
        return getSQLFlightStatus(flightnumber, date)

api.add_resource(OldFlight, '/flight/<string:date>/<string:flightnumber>', endpoint='flight')


class OldCodeshares(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, flightnumber, date):
        return getSQLFlightCodeshares(flightnumber, date)

api.add_resource(OldCodeshares, '/codeshares/<string:date>/<string:flightnumber>', endpoint='codeshares')


class Stat7Day(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightStats(flightnumber,7)

api.add_resource(Stat7Day, '/stat7/<string:flightnumber>', endpoint='stat7')


class Stat30Day(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightStats(flightnumber,30)

api.add_resource(Stat30Day, '/stat30/<string:flightnumber>', endpoint='stat30')


class StatDay(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightPastStats(flightnumber)

api.add_resource(StatDay, '/statday/<string:flightnumber>', endpoint='statday')


class LiveFlight(Resource):
    @token_required
    @cache.cached(timeout=60)
    def get(self, current_user, flightnumber, date):
        return getFlightStatusLufthansa(flightnumber, date)

api.add_resource(LiveFlight, '/live/flight/<string:date>/<string:flightnumber>', endpoint='live/flight')


class LiveCodeshares(Resource):
    @token_required
    @cache.cached(timeout=60)
    def get(self, current_user, flightnumber, date):
        return getCodesharesLufthansa(flightnumber, date)

api.add_resource(LiveCodeshares, '/live/codeshares/<string:date>/<string:flightnumber>', endpoint='live/codeshares')


class AircraftImage(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, aircraftreg):
        return getAircraftImageURL(aircraftreg)

api.add_resource(AircraftImage, '/aircraftimage/<aircraftreg>', endpoint='aircraftimage')


class AircraftLocation(Resource):
    @token_required
    @cache.cached(timeout=10)
    def get(self, current_user, aircraftreg):
        return getAircraftLocation(aircraftreg)

api.add_resource(AircraftLocation, '/aircraftlocation/<aircraftreg>', endpoint='aircraftlocation')


class AircraftName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, aircraftmodelcode):
        return getAircraftModelLufthansa(aircraftmodelcode)

api.add_resource(AircraftName, '/info/aircraftname/<aircraftmodelcode>', endpoint='info/aircraftname')


class AirlineName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, airlinecode):
        return getAirlineNameLufthansa(airlinecode)

api.add_resource(AirlineName, '/info/airlinename/<airlinecode>', endpoint='info/airlinename')


class AirportName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, airportcode):
        return getAirportNameLufthansa(airportcode)

api.add_resource(AirportName, '/info/airportname/<airportcode>', endpoint='info/airportname')


class NotificationRegister(Resource):
    @token_required
    def post(self, current_user):
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        return registerFlight(token, airline, flightnumber, date)

api.add_resource(NotificationRegister, '/notifications/register', endpoint='/notifications/register')


class NotificationUnRegister(Resource):
    @token_required
    def post(self, current_user):
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        return unregisterFlight(token, airline, flightnumber, date)

api.add_resource(NotificationUnRegister, '/notifications/unregister', endpoint='/notifications/unregister')


class AppleGet(Resource):
    def get(self):
        return {"appclips": {"apps": ["7YNLV7443U.com.MihaStrah.FlightTracker.Clip"]}}, 200

api.add_resource(AppleGet, '/apple-app-site-association', endpoint='/apple-app-site-association')



#if __name__ == '__main__':
#   server.run(debug=True)




