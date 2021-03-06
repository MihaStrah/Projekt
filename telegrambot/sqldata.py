import time
import mysql.connector as mariadb
import re
import logging

logger = logging.getLogger(__name__)

#pridobitev statusa leta iz baze
def getSQLFlightStatus(flight,date):
    host, port, database, user, password = readDBAccount()
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    airlineid = re.search("[A-z]{1,2}", flight).group()
    flightnumber = re.search("[0-9]{1,6}", flight).group()
    flightnumber = str(flightnumber).zfill(3)

    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("DB connection successful")
        except:
            i = i + 1
            time.sleep(1)
            if (i > 3):
                time.sleep(2)
            if (i > 5):
                time.sleep(3)
            if (i == 10):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where id in (select operating_id from codeshares where DATE(depscheduled)=DATE(%(date)s) and ((codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s) OR (operating_airlineid=%(airlineid)s and operating_flightnumber=%(flightnumber)s ))) or DATE(depscheduled)=DATE(%(date)s) and airlineid=%(airlineid)s and flightnumber=%(flightnumber)s order by id DESC limit 1;",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber), 'date': str(date)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()
        if returnrow is None:
            newstatus = flight_status("","","","","","","","","","","","","","","","","","","","","","","","")
        else:
            newstatus = flight_status(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15],returnrow[15],returnrow[16],returnrow[17],returnrow[18],returnrow[19],returnrow[20],returnrow[20])

    return newstatus

#branje konfiguracije podatkovne baze
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

#razred statusa leta
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