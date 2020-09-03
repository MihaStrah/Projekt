import requests, json
import datetime
import time
import oauth2 as oauth
import re
import logging
from flask import jsonify, request
from flask_restful import Resource, Api, abort
import requests_cache

#za zunanje povezave na Lufthansa API uporabimo predpomnjenje 60 sekund
requests_cache.install_cache(cache_name='lufthansa_cache', backend='sqlite', expire_after=60)

logger = logging.getLogger(__name__)

#pridobivanje žetona za Lufthansa API pred zahtevami
def getFlightStatusObjectLufthansa(flight, date):
    try:
        token = getToken()
    except:
        return
    return getFlightObject(token, flight, date)

def getFlightStatusLufthansa(flight, date):
    try:
        token = getToken()
    except:
        return abort(500, message="API Error")
    return getFlight(token, flight, date)

def getCodesharesLufthansa(flight, date):
    try:
        token = getToken()
    except:
        return abort(500, message="API Error")
    return getCodeshares(token, flight, date)

def getAircraftModelLufthansa(aircraftcode):
    try:
        token = getToken()
    except:
        return abort(500, message="API Error")
    return getAircraft(token, aircraftcode)

def getAirlineNameLufthansa(airlineid):
    try:
        token = getToken()
    except:
        return abort(500, message="API Error")
    return getAirline(token, airlineid)

def getAirportNameLufthansa(airportid):
    try:
        token = getToken()
    except:
        return abort(500, message="API Error")
    return getAirport(token, airportid)

#pridobitev aktualnih podatkov o letu iz Lufthansa API
def getFlight(token, flight, date):
    try:
        date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
        flight = re.search("^[A-z]{1,2}[0-9]{1,6}$", flight).group()
    except:
        return abort(400, message="Invalid Request")

    url = (f"https://api.lufthansa.com/v1/operations/flightstatus/{flight}/{date}")
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<5:
        try:
            request = requests.get(url = url, headers = headers)
            data = request.json()
            i = 5
            logger.info("(Used cache: %s) LH API response: %s", str(request.from_cache), data)
        except:
            time.sleep(2)
            i = i + 1
            logger.info("LH API error, retry")
            if (i==5):
                logger.error("LH API error, ABORT")
                return abort(500, message="API Error")
            else:
                logger.info("LH API error, retry")
            pass

    try:
        depairport = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['AirportCode']
    except:
        depairport = ""
    try:
        depscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeLocal']['DateTime']
    except:
        depscheduled = ""
    try:
        depscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeUTC']['DateTime']
    except:
        depscheduledUTC = ""
    try:
        depestimated = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['EstimatedTimeLocal']['DateTime']
    except:
        depestimated = ""
    try:
        depestimatedUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['EstimatedTimeUTC']['DateTime']
    except:
        depestimatedUTC = ""
    try:
        depactual = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeLocal']['DateTime']
    except:
        depactual = ""
    try:
        depactualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeUTC']['DateTime']
    except:
        depactualUTC = ""
    try:
        depterminal = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['Terminal']['Name']
    except:
        depterminal = ""
    try:
        depgate = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['Terminal']['Gate']
    except:
        depgate = ""
    try:
        deptimestatus = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['TimeStatus']['Code']
    except:
        deptimestatus = ""
    try:
        arrairport = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['AirportCode']
    except:
        arrairport = ""
    try:
        arrscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeLocal']['DateTime']
    except:
        arrscheduled = ""
    try:
        arrscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeUTC']['DateTime']
    except:
        arrscheduledUTC = ""
    try:
        arrestimated = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['EstimatedTimeLocal']['DateTime']
    except:
        arrestimated = ""
    try:
        arrestimatedUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['EstimatedTimeUTC']['DateTime']
    except:
        arrestimatedUTC = ""
    try:
        arractual = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ActualTimeLocal']['DateTime']
    except:
        arractual = ""
    try:
        arractualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ActualTimeUTC']['DateTime']
    except:
        arractualUTC = ""
    try:
        arrterminal = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['Terminal']['Name']
    except:
        arrterminal = ""
    try:
        arrgate = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['Terminal']['Gate']
    except:
        arrgate = ""
    try:
        arrtimestatus = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['TimeStatus']['Code']
    except:
        arrtimestatus = ""
    try:
        aircraftcode = data['FlightStatusResource']['Flights']['Flight'][0]['Equipment']['AircraftCode']
    except:
        aircraftcode = ""
    try:
        aircraftreg = data['FlightStatusResource']['Flights']['Flight'][0]['Equipment']['AircraftRegistration']
    except:
        aircraftreg = ""
    try:
        airlineid = data['FlightStatusResource']['Flights']['Flight'][0]['OperatingCarrier']['AirlineID']
    except:
        airlineid = ""
    try:
        flightnumber = data['FlightStatusResource']['Flights']['Flight'][0]['OperatingCarrier']['FlightNumber']
    except:
        flightnumber = ""
    try:
        flightstatus = data['FlightStatusResource']['Flights']['Flight'][0]['FlightStatus']['Code']
    except:
        flightstatus = ""

    newstatus = flight_status(depairport, depscheduled, depscheduledUTC, depestimated, depestimatedUTC, depactual, depactualUTC, depterminal, depgate,
                              deptimestatus, arrairport, arrscheduled, arrscheduledUTC, arrestimated, arrestimatedUTC, arractual,
                              arractualUTC, arrterminal, arrgate, arrtimestatus, aircraftcode,
                              aircraftreg, airlineid, flightnumber, flightstatus)

    operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
    if (operating != flight.upper() and operating != ""):
        getFlight(token, operating, date)

    if newstatus.depscheduledUTC == "":
        return abort(404, message="Flight Not Found")
    else:
        return newstatus.toJson(), 200

#pridobitev naziva letala iz Lufthansa API
def getAircraft(token, aircraftcode):
    try:
        aircraftcode = re.search("[A-z0-9]{1,10}", aircraftcode).group()
    except:
        return abort(400, message="Invalid Request")

    url = (f"https://api.lufthansa.com/v1/mds-references/aircraft/{aircraftcode}")
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            data = request.json()
            i = 3
            logger.info("LH API response: %s", data)
        except:
            time.sleep(2)
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
                return abort(500, message="API Error")
            else:
                logger.info("LH API error, retry")
            pass

    try:
        aircraftmodel = data['AircraftResource']['AircraftSummaries']['AircraftSummary']['Names']['Name']['$']
        aircraftinfo = AircraftInfo(aircraftmodel)
    except:
        return abort(404, message="Aircraft Not Found")

    return aircraftinfo.toJson(), 200

#pridobitev naziva letalske družbe iz Lufthansa API
def getAirline(token, airlinecode):
    try:
        airlinecode = re.search("[A-z]{1,5}", airlinecode).group()
    except:
        return abort(400, message="Invalid Request")

    url = (f"https://api.lufthansa.com/v1/mds-references/airlines/{airlinecode}")
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            data = request.json()
            i = 3
            logger.info("LH API response: %s", data)

        except:
            time.sleep(2)
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
                return abort(500, message="API Error")
            else:
                logger.info("LH API error, retry")
            pass

    try:
        airlinename = (data['AirlineResource']['Airlines']['Airline']['Names']['Name']['$'])
        airlineinfo = AirlineInfo(airlinename)
    except:
        return abort(404, message="Airline Not Found")

    return airlineinfo.toJson(), 200

#pridobitev naziva letališča iz Lufthansa API
def getAirport(token, airportname):
    try:
        airportname = re.search("[A-z]{1,5}", airportname).group()
    except:
        return abort(400, message="Invalid Request")

    url = (f"https://api.lufthansa.com/v1/mds-references/airports/{airportname}?lang=EN&LHoperated=0")
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            data = request.json()
            i = 3
            logger.info("LH API response: %s", data)
        except:
            time.sleep(5)
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
                return abort(500, message="API Error")
            else:
                logger.info("LH API error, retry")
            pass
    try:
        airportname = (data['AirportResource']['Airports']['Airport']['Names']['Name']['$'])
        latitude = (data['AirportResource']['Airports']['Airport']['Position']['Coordinate']['Latitude'])
        longitude = (data['AirportResource']['Airports']['Airport']['Position']['Coordinate']['Longitude'])
        airportinfo = AirportInfo(airportname, latitude, longitude)
    except:
        return abort(404, message="Airport Not Found")

    return airportinfo.toJson(), 200

#pridobitev skupnih oznak leta iz Lufthansa API
def getCodeshares(token, flight, date):
    try:
        date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
        airlineid = re.search("[A-z]{1,2}", flight).group()
        flightnumber = re.search("[0-9]{1,5}", flight).group()
        flightnumber = str(flightnumber).zfill(3)
    except:
        return abort(400, message="Invalid Request")

    flight = airlineid + flightnumber

    url = 'https://api.lufthansa.com/v1/operations/customerflightinformation' + '/' + flight + '/' + date
    bearer = "Bearer " + token
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<10:
        try:
            request = requests.get(url=url, headers=headers)
            data = request.json()
            i = 10
            logger.info("(Used cache: %s) Successfull request to Lufthansa API for CODESHARE flight:  %s, date: %s ; %s", str(request.from_cache), flight, date, data)
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            if (i == 10):
                logger.error("Error (abort) request to Lufthansa API for CODESHARE flight:  %s, date: %s", flight, date)
                return abort(500, message="API Error")

            else:
                logger.info("Retry request to Lufthansa API for CODESHARE flight:  %s, date: %s",
                            flight, date)
            pass

    codeshares = []
    codeshares.clear()

    try:
        flightcodeshares = data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']
        for flightcodeshare in flightcodeshares:
            flightcodesharenew = FlightCodeshare(flightcodeshare['AirlineID'],flightcodeshare['FlightNumber'])
            codeshares.append(flightcodesharenew.toJson())
    except:
        try:
            flightcodeshare = FlightCodeshare(data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']['AirlineID'], data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']['FlightNumber'])
            codeshares.append(flightcodeshare.toJson())
            logger.info("Not array, only one marketing carrier, parsing OK")

        except:
            codeshares.clear()
            logger.error("Unsuccessful parsing codeshares, no marketing carriers")
    try:
        flightoperating = FlightOperating(
        data['FlightInformation']['Flights']['Flight']['OperatingCarrier']['AirlineID'],
        data['FlightInformation']['Flights']['Flight']['OperatingCarrier']['FlightNumber'])
        operatingcodeshares = OperatingCodeshares(flightoperating.toJson(), codeshares)
        return operatingcodeshares.toJson(), 200

    except:
        return abort(404, message="Flight Not Found")

#pridobitev aktualnega statusa za let za potrebe podatkov o starih statusih iz Lufthansa API
def getFlightObject(token, flight, date):
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    flight = re.search("^[A-z]{1,2}[0-9]{1,6}$", flight).group()

    url = (f"https://api.lufthansa.com/v1/operations/flightstatus/{flight}/{date}")
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<5:
        try:
            request = requests.get(url = url, headers = headers)
            data = request.json()
            i = 5
            logger.info("(Used cache: %s) LH API response: %s", str(request.from_cache), data)
        except:
            time.sleep(2)
            i = i + 1
            logger.info("LH API error, retry")
            if (i==5):
                logger.error("LH API error, ABORT")
                return
            else:
                logger.info("LH API error, retry")
            pass

    try:
        depairport = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['AirportCode']
    except:
        depairport = ""
    try:
        depscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeLocal']['DateTime']
    except:
        depscheduled = ""
    try:
        depscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeUTC']['DateTime']
    except:
        depscheduledUTC = ""
    try:
        depestimated = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['EstimatedTimeLocal']['DateTime']
    except:
        depestimated = ""
    try:
        depestimatedUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['EstimatedTimeUTC']['DateTime']
    except:
        depestimatedUTC = ""
    try:
        depactual = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeLocal']['DateTime']
    except:
        depactual = ""
    try:
        depactualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeUTC']['DateTime']
    except:
        depactualUTC = ""
    try:
        depterminal = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['Terminal']['Name']
    except:
        depterminal = ""
    try:
        depgate = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['Terminal']['Gate']
    except:
        depgate = ""
    try:
        deptimestatus = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['TimeStatus']['Code']
    except:
        deptimestatus = ""
    try:
        arrairport = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['AirportCode']
    except:
        arrairport = ""
    try:
        arrscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeLocal']['DateTime']
    except:
        arrscheduled = ""
    try:
        arrscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeUTC']['DateTime']
    except:
        arrscheduledUTC = ""
    try:
        arrestimated = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['EstimatedTimeLocal']['DateTime']
    except:
        arrestimated = ""
    try:
        arrestimatedUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['EstimatedTimeUTC']['DateTime']
    except:
        arrestimatedUTC = ""
    try:
        arractual = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ActualTimeLocal']['DateTime']
    except:
        arractual = ""
    try:
        arractualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ActualTimeUTC']['DateTime']
    except:
        arractualUTC = ""
    try:
        arrterminal = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['Terminal']['Name']
    except:
        arrterminal = ""
    try:
        arrgate = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['Terminal']['Gate']
    except:
        arrgate = ""
    try:
        arrtimestatus = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['TimeStatus']['Code']
    except:
        arrtimestatus = ""
    try:
        aircraftcode = data['FlightStatusResource']['Flights']['Flight'][0]['Equipment']['AircraftCode']
    except:
        aircraftcode = ""
    try:
        aircraftreg = data['FlightStatusResource']['Flights']['Flight'][0]['Equipment']['AircraftRegistration']
    except:
        aircraftreg = ""
    try:
        airlineid = data['FlightStatusResource']['Flights']['Flight'][0]['OperatingCarrier']['AirlineID']
    except:
        airlineid = ""
    try:
        flightnumber = data['FlightStatusResource']['Flights']['Flight'][0]['OperatingCarrier']['FlightNumber']
    except:
        flightnumber = ""
    try:
        flightstatus = data['FlightStatusResource']['Flights']['Flight'][0]['FlightStatus']['Code']
    except:
        flightstatus = ""

    newstatus = flight_status(depairport, depscheduled, depscheduledUTC, depestimated, depestimatedUTC, depactual, depactualUTC, depterminal, depgate,
                              deptimestatus, arrairport, arrscheduled, arrscheduledUTC, arrestimated, arrestimatedUTC, arractual,
                              arractualUTC, arrterminal, arrgate, arrtimestatus, aircraftcode,
                              aircraftreg, airlineid, flightnumber, flightstatus)

    operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
    if (operating != flight.upper() and operating != ""):
        getFlight(token, operating, date)

    if newstatus.depscheduledUTC == "":
        return
    else:
        return newstatus.toJson()

#pridobitev Lufthansa API žetona (shranjen ali nov)
token = "null"
expires_date = "2000-01-01 00:00:00.0"
def getToken():
    global expires_date
    global token
    expires = datetime.datetime.strptime(str(expires_date), '%Y-%m-%d %H:%M:%S.%f')
    if (expires < datetime.datetime.now()):
        token, expires_date = getNewToken()
    return token

#pridobitev novega Lufthansa API žetona
def getNewToken():
    url = 'https://api.lufthansa.com/v1/oauth/token'
    consumer = oauth.Consumer(key ='', secret='')
    client = oauth.Client(consumer)
    id, secret = readLHAccount()
    params = "client_id=" + id + "&" + "client_secret=" + secret + "&grant_type=client_credentials"
    i = 0
    while i < 10:
        try:
            resp, content = client.request(
                            url,
                            method = "POST",
                            body=params,
                            headers={'Content-type': 'application/x-www-form-urlencoded'}
                            )
            content_string = content.decode("utf-8")
            data = json.loads(content_string)
            access_token = data["access_token"]
            expires_in = data["expires_in"]
            expires_date = datetime.datetime.now() + datetime.timedelta(0, (expires_in - 15))
            logger.info("LH API new token, expires: %s", expires_date)
            pass
            i=10
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            i = i + 1
            if (i == 10):
                logger.error("LH API error, ABORT")
            else:
                logger.info("LH API error, retry")
            pass

    return access_token, expires_date

#branje Lufthansa računa
def readLHAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/LHaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    id = lines[0]
    secret = lines[1]
    f.close()
    return id,secret

#razred aktualnega statusa leta
class flight_status:
    depairport = ""
    depscheduled = ""
    depscheduledUTC = ""
    depestimated = ""
    depestimatedUTC = ""
    depactual = ""
    depactualUTC = ""
    depterminal = ""
    depgate = ""
    deptimestatus = ""
    arrairport = ""
    arrscheduled = ""
    arrscheduledUTC = ""
    arrestimated = ""
    arrestimatedUTC = ""
    arractual = ""
    arractualUTC = ""
    arrterminal = ""
    arrgate = ""
    arrtimestatus = ""
    aircraftcode = ""
    aircraftreg = ""
    airlineid = ""
    flightnumber = ""
    flightstatus = ""

    def toJson(self):
        return self.__dict__

    def __init__(self, depairport,depscheduled,depscheduledUTC, depestimated, depestimatedUTC, depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC, arrestimated, arrestimatedUTC, arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus):
        self.depairport = depairport
        self.depscheduled = depscheduled
        self.depscheduledUTC = depscheduledUTC
        self.depestimated = depestimated
        self.depestimatedUTC = depestimatedUTC
        self.depactual = depactual
        self.depactualUTC = depactualUTC
        self.depterminal = depterminal
        self.depgate = depgate
        self.deptimestatus = deptimestatus
        self.arrairport = arrairport
        self.arrscheduled = arrscheduled
        self.arrscheduledUTC = arrscheduledUTC
        self.arrestimated = arrestimated
        self.arrestimatedUTC = arrestimatedUTC
        self.arractual = arractual
        self.arractualUTC = arractualUTC
        self.arrterminal = arrterminal
        self.arrgate = arrgate
        self.arrtimestatus = arrtimestatus
        self.aircraftcode = aircraftcode
        self.aircraftreg = aircraftreg
        self.airlineid = airlineid
        self.flightnumber = flightnumber
        self.flightstatus = flightstatus

#razred naziva letala
class AircraftInfo:
    aircraftName= ""

    def toJson(self):
        return self.__dict__

    def __init__(self, aircraftName):
        self.aircraftName = aircraftName

#razred naziva letalske družbe
class AirlineInfo:
    airlineName = ""

    def toJson(self):
        return self.__dict__

    def __init__(self, airlineName):
        self.airlineName = airlineName

#razred naziva in lokacije letališča
class AirportInfo:
    airportName = ""
    latitude = 0
    longitude = 0

    def toJson(self):
        return self.__dict__

    def __init__(self, airportName, latitude, longitude):
        self.airportName = airportName
        self.latitude = latitude
        self.longitude = longitude

#razred podatkov o skupnih oznakah leta
class FlightCodeshare:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        return self.__dict__

    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber

#razred dejanskega leta
class FlightOperating:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        return self.__dict__

    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber

#razred skupnih oznak leta
class OperatingCodeshares:
    operating = FlightOperating
    codeshares = []

    def toJson(self):
        return self.__dict__

    def __init__(self, operating, codeshares):
        self.operating = operating
        self.codeshares = codeshares