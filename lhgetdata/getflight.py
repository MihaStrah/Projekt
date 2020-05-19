import requests, json
import datetime
import time
from writetosql import writeOneFlightToSql
import logging

logger = logging.getLogger(__name__)

def getFlightStatusWriteSql(token,flights,allids,date,wait):
    a=0
    idn=0
    for flight in flights:
        id = str(allids[idn])
        idn=idn+1
        a=a+1
        url = 'https://api.lufthansa.com/v1/operations/flightstatus' + '/' + flight + '/' + date
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
                logger.info("Successfull request to Lufthansa API for flight:  %s, date: %s ; %s", flight, date, data)
            except:
                time.sleep(10)
                if (i > 3):
                    time.sleep(180)
                if (i > 5):
                    time.sleep(600)
                #print("Retry LH " + str(i))
                i = i + 1
                if (i == 10):
                    logger.error("Error (abort) request to Lufthansa API for flight:  %s, date: %s", flight, date)
                else:
                    logger.info("Retry request to Lufthansa API for flight:  %s, date: %s", flight, date)
                pass

        try:
            depairport = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['AirportCode']
        except:
            depairport = ""
        try:
            depscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeLocal'][
                'DateTime']
        except:
            depscheduled = ""
        try:
            depscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeUTC'][
                'DateTime']
        except:
            depscheduledUTC = ""
        try:
            depactual = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeLocal']['DateTime']
        except:
            depactual = ""
        try:
            depactualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeUTC'][
                'DateTime']
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
            arrscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeLocal'][
                'DateTime']
        except:
            arrscheduled = ""
        try:
            arrscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeUTC'][
                'DateTime']
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

        newstatus = flight_status(depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus)

        operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
        if (operating != flight.upper() and operating != ""):
            getFlightStatusWriteSqlOperatingRetry(token, operating, id, date, wait)
            #print(str(a) + " done. Processed flight " + str(flight) + " with ID " + id + ", " + str(len(flights) - a) + " remaining !THIS WAS INSERTED WITH OPERATING RETRY BEACUSE OF OPERATING FLIGHT MISMATCH!")
            logger.info("Processed flight: %s, date: %s ; %s remaining ; !THIS WAS INSERTED WITH OPERATING RETRY BEACUSE OF OPERATING FLIGHT MISMATCH!", flight, date, (len(flights) - a))

        else:
            writeOneFlightToSql(newstatus, id)
            #print(str(a) + " done. Processed flight " + str(flight) + " with ID " + id + ", " + str(len(flights) - a) + " remaining")
            logger.info("Processed flight: %s, date: %s ; %s remaining", flight, date, (len(flights) - a))
            #wait because of API limitations
        time.sleep(wait)

    return


def getFlightStatusWriteSqlOperatingRetry(token, flight, id, date, wait):
    url = 'https://api.lufthansa.com/v1/operations/flightstatus' + '/' + flight + '/' + date
    #print(url)
    bearer = "Bearer " + token
    headers = {"Authorization": bearer, "Accept": "application/json"}
    i = 0
    while i < 10:
        try:
            request = requests.get(url=url, headers=headers)
            #print(request)
            data = request.json()
            #print(data)
            i = 10
            logger.info("Successfull (operating retry) request to Lufthansa API for flight:  %s, date: %s ; %s", flight, date, data)
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            #print("Retry LH " + str(i))
            i = i + 1
            if (i == 10):
                logger.error("Error (abort) (operating retry) request to Lufthansa API for flight:  %s, date: %s", flight, date)
            else:
                logger.info("Retry (operating retry) request to Lufthansa API for flight:  %s, date: %s", flight, date)
            pass

    try:
        depairport = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['AirportCode']
    except:
        depairport = ""
    try:
        depscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeLocal'][
                'DateTime']
    except:
        depscheduled = ""
    try:
        depscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ScheduledTimeUTC'][
                'DateTime']
    except:
        depscheduledUTC = ""
    try:
        depactual = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeLocal']['DateTime']
    except:
        depactual = ""
    try:
        depactualUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Departure']['ActualTimeUTC'][
                'DateTime']
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
        arrscheduled = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeLocal'][
                'DateTime']
    except:
        arrscheduled = ""
    try:
        arrscheduledUTC = data['FlightStatusResource']['Flights']['Flight'][0]['Arrival']['ScheduledTimeUTC'][
                'DateTime']
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

    newstatus = flight_status(depairport, depscheduled, depscheduledUTC, depactual, depactualUTC, depterminal,
                                  depgate, deptimestatus, arrairport, arrscheduled, arrscheduledUTC, arractual,
                                  arractualUTC, arrterminal, arrgate, arrtimestatus, aircraftcode, aircraftreg,
                                  airlineid, flightnumber, flightstatus)

    operating = (f"{newstatus.airlineid}{newstatus.flightnumber}")
    if (operating != flight.upper() and operating != ""):
        #print("!!!! ERROR !!!! operating is not the same, but should be (operating retry), writing anyway")
        logger.error("Operating is not the same, but should be (operating retry), writing anyway ; flight:  %s, date: %s", flight, date)


    writeOneFlightToSql(newstatus, id)

    # wait because of API limitations
    time.sleep(wait)

    return newstatus



def getFlightCodeshares(token,flight,date,wait):
    time.sleep(wait)
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
            logger.info("Successfull request to Lufthansa API for CODESHARE flight:  %s, date: %s ; %s", flight, date, data)
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            #print("Retry LH " + str(i))
            i = i + 1
            if (i == 10):
                logger.error("Error (abort) (operating retry) request to Lufthansa API for CODESHARE flight:  %s, date: %s", flight, date)
            else:
                logger.info("Retry (operating retry) request to Lufthansa API for CODESHARE flight:  %s, date: %s",
                            flight, date)
            pass

    codeshares = []
    codeshares.clear()
    try:
        flightcodeshares = data['FlightInformation']['Flights']['Flight']['MarketingCarrierList']['MarketingCarrier']
        #print("codeshares : ", flightcodeshares)
        for flightcodeshare in flightcodeshares:
            codeshares.append([flightcodeshare['AirlineID'],flightcodeshare['FlightNumber']])
            #print(flightcodeshare['AirlineID'], flightcodeshare['FlightNumber'])
    except:
        codeshares.clear()
        logger.error("Unsuccessful parsing codeshares")

    return codeshares




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