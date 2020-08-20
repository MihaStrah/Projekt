import requests, json
import datetime
import time
import oauth2 as oauth
import re
import logging
from flask import jsonify, request

import requests_cache


#cache for external API requests (1 minute)
requests_cache.install_cache(cache_name='lufthansa_cache', backend='sqlite', expire_after=60)

logger = logging.getLogger(__name__)

def getFlightStatusLufthansa(flight, date):
    token = getToken()
    flightstatus = getFlight(token, flight, date)
    return flightstatus

def getAircraftModelLufthansa(aircraftcode):
    token = getToken()
    aircraftmodel = getAircraft(token, aircraftcode)
    return aircraftmodel.toJson()

def getAirlineNameLufthansa(airlineid):
    token = getToken()
    airlinename = getAirline(token, airlineid)
    return airlinename.toJson()

def getAirportNameLufthansa(airportid):
    token = getToken()
    airportname = getAirport(token, airportid)
    return airportname

def getCodesharesLufthansa(flight, date):
    token = getToken()
    codeshares = getCodeshares(token, flight, date)
    return codeshares



def getFlight(token, flight, date):
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    flight = re.search("^[A-z]{1,2}[0-9]{1,6}$", flight).group()

    url = (f"https://api.lufthansa.com/v1/operations/flightstatus/{flight}/{date}")
    #print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    #print (bearer)
    i = 0
    while i<5:
        try:
            request = requests.get(url = url, headers = headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 5
            #print("Used Cache: %s" % request.from_cache)
            logger.info("(Used cache: %s) LH API response: %s", str(request.from_cache), data)
        except:
            time.sleep(2)
            #print("retry " + str(i))
            i = i + 1
            logger.info("LH API error, retry")
            if (i==5):
                logger.error("LH API error, ABORT")
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

    newstatus = flight_status(depairport, depscheduled, depscheduledUTC, depactual, depactualUTC, depterminal, depgate,
                              deptimestatus, arrairport, arrscheduled, arrscheduledUTC, arractual,
                              arractualUTC, arrterminal, arrgate, arrtimestatus, aircraftcode,
                              aircraftreg, airlineid, flightnumber, flightstatus)

    #check status for operating carrier flight if not operating carrier
    operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
    if (operating != flight.upper() and operating != ""):
        getFlight(token, operating, date)

    if newstatus.depscheduledUTC == "":
        newstatus = jsonify({'info': 'flight does not exist'})
    else:
        newstatus = newstatus.toJson()

    return newstatus



def getAircraft(token, aircraftcode):
    aircraftcode = re.search("[A-z,0-9]{1,10}", aircraftcode).group()
    url = (f"https://api.lufthansa.com/v1/mds-references/aircraft/{aircraftcode}")
    #print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    #print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 3
            logger.info("LH API response: %s", data)
        except:
            time.sleep(2)
            #print("retry " + str(i))
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
            else:
                logger.info("LH API error, retry")
            pass

    try:
        aircraftmodel = data['AircraftResource']['AircraftSummaries']['AircraftSummary']['Names']['Name']['$']
        aircraftinfo = aircraft_info(aircraftmodel)
    except:
        aircraftmodel = aircraftcode
        aircraftinfo = aircraft_info(aircraftmodel)

    return aircraftinfo


def getAirline(token, airlinecode):
    airlinecode = re.search("[A-z]{1,5}", airlinecode).group()
    url = (f"https://api.lufthansa.com/v1/mds-references/airlines/{airlinecode}")
    #print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    #print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 3
            logger.info("LH API response: %s", data)

        except:
            time.sleep(2)
            #print("retry " + str(i))
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
            else:
                logger.info("LH API error, retry")
            pass

    try:
        airlinename = (data['AirlineResource']['Airlines']['Airline']['Names']['Name']['$'])
        airlineinfo = airline_info(airlinename)
    except:
        airlinename = ""
        airlineinfo = airline_info(airlinename)

    return airlineinfo


def getAirport(token, airportname):
    airportname = re.search("[A-z]{1,5}", airportname).group()
    url = (f"https://api.lufthansa.com/v1/mds-references/airports/{airportname}?lang=EN&LHoperated=0")
    #print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    #print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 3
            logger.info("LH API response: %s", data)
        except:
            time.sleep(5)
            #print("retry " + str(i))
            i = i + 1
            if (i==3):
                logger.error("LH API error, ABORT")
            else:
                logger.info("LH API error, retry")
            pass
    try:
        airportname = (data['AirportResource']['Airports']['Airport']['Names']['Name']['$'])
        latitude = (data['AirportResource']['Airports']['Airport']['Position']['Coordinate']['Latitude'])
        longitude = (data['AirportResource']['Airports']['Airport']['Position']['Coordinate']['Longitude'])
        airportinfo = airport_info(airportname, latitude, longitude).toJson()
    except:
        airportinfo = jsonify({'info': 'airport does not exist'})

    return airportinfo


def getCodeshares(token, flight, date):
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    airlineid = re.search("[A-z]{1,2}", flight).group()
    flightnumber = re.search("[0-9]{1,5}", flight).group()
    flight = airlineid + flightnumber

    url = 'https://api.lufthansa.com/v1/operations/customerflightinformation' + '/' + flight + '/' + date
    #print(url)
    bearer = "Bearer " + token
    headers = {"Authorization":bearer, "Accept":"application/json"}
    i = 0
    while i<10:
        try:
            request = requests.get(url=url, headers=headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 10
            logger.info("(Used cache: %s) Successfull request to Lufthansa API for CODESHARE flight:  %s, date: %s ; %s", str(request.from_cache), date, data)
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            #print("Retry LH " + str(i))
            i = i + 1
            if (i == 10):
                logger.error("Error (abort) request to Lufthansa API for CODESHARE flight:  %s, date: %s", flight, date)
            else:
                logger.info("Retry request to Lufthansa API for CODESHARE flight:  %s, date: %s",
                            flight, date)
            pass

    codeshares = []
    codeshares.clear()

    try:
        flightcodeshares = data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']
        for flightcodeshare in flightcodeshares:
            flightcodesharenew = flight_codeshare(flightcodeshare['AirlineID'],flightcodeshare['FlightNumber'])
            codeshares.append(flightcodesharenew.__dict__)
    except:
        try:
            flightcodeshare = flight_codeshare(data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']['AirlineID'], data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']['FlightNumber'])
            codeshares.append(flightcodeshare.__dict__)
            logger.info("Not array, only one marketing carrier, parsing OK")

        except:
            codeshares.clear()
            logger.error("Unsuccessful parsing codeshares, no marketing carriers")
    try:
        flightoperating = flight_operating(
        data['FlightInformation']['Flights']['Flight']['OperatingCarrier']['AirlineID'],
        data['FlightInformation']['Flights']['Flight']['OperatingCarrier']['FlightNumber'])
        operatingcodeshares = operating_codeshares(flightoperating, codeshares)
        codesharesInfo = operatingcodeshares.toJson()

    except:
        codesharesInfo = jsonify({'info': 'no codeshare flights'})

    return codesharesInfo









token = "null"
expires_date = "2000-01-01 00:00:00.0"
def getToken():
    global expires_date
    global token
    expires = datetime.datetime.strptime(str(expires_date), '%Y-%m-%d %H:%M:%S.%f')
    if (expires < datetime.datetime.now()):
        token, expires_date = getNewToken()
    return token

def getNewToken():
    url = 'https://api.lufthansa.com/v1/oauth/token'
    consumer = oauth.Consumer(key ='', secret='')
    client = oauth.Client(consumer)
    id, secret = readLHAccount()
    params = "client_id=" + id + "&" + "client_secret=" + secret + "&grant_type=client_credentials"
    #print(params)
    i = 0
    while i < 10:
        try:
            resp, content = client.request(
                            url,
                            method = "POST",
                            body=params,
                            headers={'Content-type': 'application/x-www-form-urlencoded'}
                            #force_auth_header=True
                            )
            content_string = content.decode("utf-8")
            data = json.loads(content_string)
            access_token = data["access_token"]
            expires_in = data["expires_in"]
            expires_date = datetime.datetime.now() + datetime.timedelta(0, (expires_in - 15))
            #print("New token, expires: ", expires_date)
            logger.info("LH API new token, expires: %s", expires_date)
            pass
            i=10
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            #print("Retry LH token " + str(i))
            i = i + 1
            if (i == 10):
                logger.error("LH API error, ABORT")
            else:
                logger.info("LH API error, retry")
            pass

    return access_token, expires_date


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


class flight_status:
    depairport = ""
    depscheduled = ""
    depscheduledUTC = ""
    depactual = ""
    depactualUTC = ""
    depterminal = ""
    depgate = ""
    deptimestatus = ""
    arrairport = ""
    arrscheduled = ""
    arrscheduledUTC = ""
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
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus):
        self.depairport = depairport
        self.depscheduled = depscheduled
        self.depscheduledUTC = depscheduledUTC
        self.depactual = depactual
        self.depactualUTC = depactualUTC
        self.depterminal = depterminal
        self.depgate = depgate
        self.deptimestatus = deptimestatus
        self.arrairport = arrairport
        self.arrscheduled = arrscheduled
        self.arrscheduledUTC = arrscheduledUTC
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


class aircraft_info:
    aircraftName= ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, aircraftName):
        self.aircraftName = aircraftName


class airline_info:
    airlineName = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, airlineName):
        self.airlineName = airlineName

class airport_info:
    airportName = ""
    latitude = 0
    longitude = 0

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, airportName, latitude, longitude):
        self.airportName = airportName
        self.latitude = latitude
        self.longitude = longitude




class flight_codeshare:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber

class flight_operating:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber

class operating_codeshares:
    operating = flight_operating
    codeshares = []

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, operating, codeshares):
        self.operating = operating
        self.codeshares = codeshares