import time
import mysql.connector as mariadb
import re

def getSQLFlightStatus(flight,date):
    host, port, database, user, password = readDBAccount()

    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    airlineid = re.search("[A-z]{2}", flight).group()
    flightnumber = re.search("[0-9]{1,4}", flight).group()
    #padding to min length 3
    flightnumber = str(flightnumber).zfill(3)

    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
        except:
            i = i + 1
            time.sleep(1)
            if (i > 3):
                time.sleep(2)
            if (i > 5):
                time.sleep(3)
            print("Retry DB " + str(i))
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where airlineid=%(airlineid)s and flightnumber=%(flightnumber)s and DATE(depscheduled)=DATE(%(date)s) limit 1;", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber),'date': str(date)})
            mariadb_connection.close()
            i = 10
        except mariadb.Error as error:
            i = i + 1
            time.sleep(1)
            if (i > 3):
                time.sleep(2)
            if (i > 5):
                time.sleep(3)
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))

        returnrow = cursor.fetchone()
        if returnrow is None:
            newstatus = flight_status("","","","","","","","","","","","","","","","","","","","","","","","")
        else:
            newstatus = flight_status(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15],returnrow[15],returnrow[16],returnrow[17],returnrow[18],returnrow[19],returnrow[20],returnrow[20])

    return newstatus


#user with select priviledges
def readDBAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/DBaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    host = lines[0]
    port = lines[1]
    database = lines[2]
    user = lines[3]
    password = lines[4]
    f.close()
    return host, port, database, user, password


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