import requests, json
import datetime
import time
import oauth2 as oauth
import re

def getFlightStatus(flight, date):
    token = getToken()
    flightstatus = getFlight(token, flight, date)
    return flightstatus

def getAircraftModel(aircraftcode):
    token = getToken()
    aircraftmodel = getAircraft(token, aircraftcode)
    return aircraftmodel

def getAirlineName(airlineid):
    token = getToken()
    airlinename = getAirline(token, airlineid)
    return airlinename

def getAirportName(airportid):
    token = getToken()
    airportname = getAirport(token, airportid)
    return airportname

def getFlight(token, flight, date):
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    flight = re.search("^[A-z][A-z][0-9]{1,4}$", flight).group()


    url = (f"https://api.lufthansa.com/v1/operations/flightstatus/{flight}/{date}")
    print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    print (bearer)
    i = 0
    while i<10:
        try:
            request = requests.get(url = url, headers = headers)
            print(request)
            data = request.json()
            print(data)
            i = 10
        except:
            time.sleep(5)
            print("retry " + str(i))
            i = i + 1
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
        deptimestatusdef = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['TimeStatus']['Definition']
    except:
        deptimestatusdef = ""
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
        arrtimestatusdef = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['TimeStatus']['Definition']
    except:
        arrtimestatusdef = ""
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
    try:
        flightstatusdef = data['FlightStatusResource']['Flights']['Flight'][0]['FlightStatus']['Definition']
    except:
        flightstatusdef = ""

    newstatus = flight_status(depairport, depscheduled, depscheduledUTC, depactual, depactualUTC, depterminal, depgate,
                              deptimestatus, deptimestatusdef, arrairport, arrscheduled, arrscheduledUTC, arractual,
                              arractualUTC, arrterminal, arrgate, arrtimestatus, arrtimestatusdef, aircraftcode,
                              aircraftreg, airlineid, flightnumber, flightstatus, flightstatusdef)

    #check status for operating carrier flight if not operating carrier
    operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
    if (operating != flight.upper() and operating != ""):
        newstatus = getFlight(token, operating, date)

    return newstatus



def getAircraft(token, aircraftcode):
    url = (f"https://api.lufthansa.com/v1/mds-references/aircraft/{aircraftcode}")
    print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            print(request)
            data = request.json()
            print(data)
            i = 3
        except:
            time.sleep(5)
            print("retry " + str(i))
            i = i + 1
            pass

    try:
        aircraftmodel = data['AircraftResource']['AircraftSummaries']['AircraftSummary']['Names']['Name']['$']
    except:
        aircraftmodel = aircraftcode

    return aircraftmodel


def getAirline(token, airlinecode):
    url = (f"https://api.lufthansa.com/v1/mds-references/airlines/{airlinecode}")
    print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            print(request)
            data = request.json()
            print(data)
            i = 3
        except:
            time.sleep(5)
            print("retry " + str(i))
            i = i + 1
            pass

    try:
        airlinename = (data['AirlineResource']['Airlines']['Airline']['Names']['Name']['$'])
        airlinename = (f' ({airlinename}) ')
    except:
        airlinename = ""

    return airlinename


def getAirport(token, airportname):
    url = (f"https://api.lufthansa.com/v1/mds-references/airports/{airportname}?lang=EN&LHoperated=0")
    print(url)
    bearer = (f"Bearer {token}")
    headers = {"Authorization":bearer, "Accept":"application/json"}
    print (bearer)
    i = 0
    while i<3:
        try:
            request = requests.get(url = url, headers = headers)
            print(request)
            data = request.json()
            print(data)
            i = 3
        except:
            time.sleep(5)
            print("retry " + str(i))
            i = i + 1
            pass
    try:
        airportname = (data['AirportResource']['Airports']['Airport']['Names']['Name']['$'])
        airportname = (f' ({airportname}) ')
    except:
        airportname = ""

    return airportname

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
    print(params)
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
            print("New token, expires: ", expires_date)
            i=10
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            print("Retry LH token " + str(i))
            i = i + 1
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
    deptimestatusdef = ""
    arrairport = ""
    arrscheduled = ""
    arrscheduledUTC = ""
    arractual = ""
    arractualUTC = ""
    arrterminal = ""
    arrgate = ""
    arrtimestatus = ""
    arrtimestatusdef = ""
    aircraftcode = ""
    aircraftreg = ""
    airlineid = ""
    flightnumber = ""
    flightstatus = ""
    flightstatusdef = ""

    def __init__(self, depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,deptimestatusdef,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,arrtimestatusdef,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightstatusdef):
        self.depairport = depairport
        self.depscheduled = depscheduled
        self.depscheduledUTC = depscheduledUTC
        self.depactual = depactual
        self.depactualUTC = depactualUTC
        self.depterminal = depterminal
        self.depgate = depgate
        self.deptimestatus = deptimestatus
        self.deptimestatusdef = deptimestatusdef
        self.arrairport = arrairport
        self.arrscheduled = arrscheduled
        self.arrscheduledUTC = arrscheduledUTC
        self.arractual = arractual
        self.arractualUTC = arractualUTC
        self.arrterminal = arrterminal
        self.arrgate = arrgate
        self.arrtimestatus = arrtimestatus
        self.arrtimestatusdef = arrtimestatusdef
        self.aircraftcode = aircraftcode
        self.aircraftreg = aircraftreg
        self.airlineid = airlineid
        self.flightnumber = flightnumber
        self.flightstatus = flightstatus
        self.flightstatusdef = flightstatusdef
