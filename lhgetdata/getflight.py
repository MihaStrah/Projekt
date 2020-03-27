import requests, json
import datetime
import time
from writetosql import writeOneFlightToSql

def getFlightStatusWriteSql(token,flights,allids,date,wait):
    flightsstatus = []
    a=0
    idn=0
    for flight in flights:
        id = str(allids[idn])
        idn=idn+1
        a=a+1
        url = 'https://api.lufthansa.com/v1/operations/flightstatus' + '/' + flight + '/' + date
        print(url)
        bearer = "Bearer " + token
        headers = {"Authorization":bearer, "Accept":"application/json"}
        i = 0
        while i<10:
            try:
                request = requests.get(url=url, headers=headers)
                print(request)
                data = request.json()
                print(data)
                i = 10
            except:
                time.sleep(10)
                if (i > 3):
                    time.sleep(180)
                if (i > 5):
                    time.sleep(600)
                print("Retry LH " + str(i))
                i = i + 1
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
        flightsstatus.append(newstatus)

        writeOneFlightToSql(newstatus,id)

        print(str(a) + " done. Processed flight " + str(flight) + " with ID " + id + ", " + str(len(flights)-a) + " remaining")

        #wait because of API limitations
        time.sleep(wait)

    return





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