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
from sqldata import getSQLFlightStatus, getSQLFlightStats, getSQLFlightCodeshares, getSQLFlightPastStats
from aircraftImage import getAircraftImageURL
from liveLufthansa import getFlightStatusLufthansa, getAircraftModelLufthansa, getAirlineNameLufthansa, getAirportNameLufthansa, getCodesharesLufthansa
from notificationUsers import setDatabase, registerFlight, unregisterFlight
from opensky import getAircraftLocation

#konfiguracija aplikacije
server = Flask(__name__)
api = Api(server)

#konfiguracija predpomnjenja
cache = Cache(server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp'})
cache.clear()

#konfiguracija dnevnika
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="letAPI_logs_out/letAPIPythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)

#nastavitev baze uporabnikov obvestil
setDatabase()

#branje API ključa
def readAPIKey():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/APIKey.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    key = lines[0]
    f.close()
    return key

#konfiguracija baze API uporabnikov
path = os.path.abspath(os.path.dirname(__file__))
fullpath = 'sqlite:///' + os.path.join(path, 'apiusers/APIusersDB.db')

server.config['SECRET_KEY'] = readAPIKey()
server.config['SQLALCHEMY_DATABASE_URI'] = (fullpath)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(server)

#model uporabnika za bazo uporabnikov
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)

#baza uporabnikov
db.create_all()

#preverjanje prisotnosti in veljavnosti žetona
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

#možna končna točka za registracijo API uporabnikov (onemogočeno, razen za ustvarjanje dodatnih uporabnikov)
# @server.route('/register', methods=['POST'])
# def signup_user():
#     data = request.get_json()
#
#     hashed_password = generate_password_hash(data['password'], method='sha256')
#
#     new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
#     db.session.add(new_user)
#     db.session.commit()
#
#     return jsonify({'message': 'registered successfully'})

#prijava: preverjanje uporabniških podatkov in generacija žetona
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

#končna točka za prijavo in pridobitev žetona
api.add_resource(Login, '/login', endpoint='login')

#pridobitev podatkov za stare lete iz lastne podatkovne baze
class OldFlight(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, flightnumber, date):
        return getSQLFlightStatus(flightnumber, date)

#končna točka za stare lete
api.add_resource(OldFlight, '/flight/<string:date>/<string:flightnumber>', endpoint='flight')

#pridobitev podatkov o skupnih oznakah letov
class OldCodeshares(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, flightnumber, date):
        return getSQLFlightCodeshares(flightnumber, date)

#končna točka za skupne oznake starih letov
api.add_resource(OldCodeshares, '/codeshares/<string:date>/<string:flightnumber>', endpoint='codeshares')

#pridobitev podatkov za 7 dnevno statistiko iz lastne podatkovne baze
class Stat7Day(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightStats(flightnumber,7)

#končna točka za 7 dnevno statistiko
api.add_resource(Stat7Day, '/stat7/<string:flightnumber>', endpoint='stat7')

#pridobitev podatkov za 30 dnevno statistiko iz lastne podatkovne baze
class Stat30Day(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightStats(flightnumber,30)

#končna točka za 30 dnevno statistiko
api.add_resource(Stat30Day, '/stat30/<string:flightnumber>', endpoint='stat30')

#pridobitev podatkov za 90 dnevne informacije o statusu iz lastne podatkovne baze
class StatDay(Resource):
    @token_required
    @cache.cached(timeout=3600)
    def get(self, current_user, flightnumber):
        return getSQLFlightPastStats(flightnumber)

#končna točka za 90 dnevne statuse
api.add_resource(StatDay, '/statday/<string:flightnumber>', endpoint='statday')

#pridobitev aktualnih podatkov za let iz Lufthansa API
class LiveFlight(Resource):
    @token_required
    @cache.cached(timeout=60)
    def get(self, current_user, flightnumber, date):
        return getFlightStatusLufthansa(flightnumber, date)

#končna točka za aktualne podatke o letu
api.add_resource(LiveFlight, '/live/flight/<string:date>/<string:flightnumber>', endpoint='live/flight')

#pridobitev aktualnih podatkov za skupne oznake leta iz Lufthansa API
class LiveCodeshares(Resource):
    @token_required
    @cache.cached(timeout=60)
    def get(self, current_user, flightnumber, date):
        return getCodesharesLufthansa(flightnumber, date)

#končna točka za aktualne skupne oznake leta
api.add_resource(LiveCodeshares, '/live/codeshares/<string:date>/<string:flightnumber>', endpoint='live/codeshares')

#pridobitev URL do slike letala iz airport-data.com API
class AircraftImage(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, aircraftreg):
        return getAircraftImageURL(aircraftreg)

#končna točka za URL slike letala
api.add_resource(AircraftImage, '/aircraftimage/<aircraftreg>', endpoint='aircraftimage')

#pridobitev trenutne lokacije letala iz opensky-network.org API
class AircraftLocation(Resource):
    @token_required
    @cache.cached(timeout=10)
    def get(self, current_user, aircraftreg):
        return getAircraftLocation(aircraftreg)

#končna točka za trenutno lokacijo letala
api.add_resource(AircraftLocation, '/aircraftlocation/<aircraftreg>', endpoint='aircraftlocation')

#pridobitev naziva letala iz Lufthansa API
class AircraftName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, aircraftmodelcode):
        return getAircraftModelLufthansa(aircraftmodelcode)

#končna točka za naziv letala
api.add_resource(AircraftName, '/info/aircraftname/<aircraftmodelcode>', endpoint='info/aircraftname')

#pridobitev naziva letalske družbe iz Lufthansa API
class AirlineName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, airlinecode):
        return getAirlineNameLufthansa(airlinecode)

#končna točka za naziv letalske družbe
api.add_resource(AirlineName, '/info/airlinename/<airlinecode>', endpoint='info/airlinename')

#pridobitev naziva letališča iz Lufthansa API
class AirportName(Resource):
    @token_required
    @cache.cached(timeout=432000)
    def get(self, current_user, airportcode):
        return getAirportNameLufthansa(airportcode)

#končna točka za naziv letališča
api.add_resource(AirportName, '/info/airportname/<airportcode>', endpoint='info/airportname')

#registracija za obvestila o spremembah
class NotificationRegister(Resource):
    @token_required
    def post(self, current_user):
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        return registerFlight(token, airline, flightnumber, date)

#končna točka registracije za obvestila
api.add_resource(NotificationRegister, '/notifications/register', endpoint='/notifications/register')

#izbris registracije za obvestila o spremembah
class NotificationUnRegister(Resource):
    @token_required
    def post(self, current_user):
        token = request.form.get('token')
        airline = request.form.get('airline')
        flightnumber = request.form.get('flightnumber')
        date = request.form.get('date')
        return unregisterFlight(token, airline, flightnumber, date)

#končna točka za izbris registracije za obvestila
api.add_resource(NotificationUnRegister, '/notifications/unregister', endpoint='/notifications/unregister')

#zagon strežnika v načinu razhroščevanja
#if __name__ == '__main__':
#   server.run(debug=True)




