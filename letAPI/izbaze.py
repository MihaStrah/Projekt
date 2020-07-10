import time
import mysql.connector as mariadb
import re
import logging
import json
from flask import jsonify

logger = logging.getLogger(__name__)

def getSQLFlightStatus(flight,date):
    host, port, database, user, password = readDBAccount()
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    airlineid = re.search("[A-z]{1,2}", flight).group()
    flightnumber = re.search("[0-9]{1,4}", flight).group()
    #padding to min length 3
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
            #print("Retry DB " + str(i))
            if (i == 10):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            #search in DB for operating and for codeshare (returns operating flight)
            #cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where id in (select operating_id from codeshares where DATE(depscheduled)=DATE(%(date)s) and ((codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s) OR (operating_airlineid=%(airlineid)s and operating_flightnumber=%(flightnumber)s )) order by depscheduled DESC ) or DATE(depscheduled)=DATE(%(date)s) and airlineid=%(airlineid)s and flightnumber=%(flightnumber)s order by depscheduled DESC limit 1;",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber), 'date': str(date)})
            cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where DATE(depscheduled)=DATE( %(date)s) and airlineid= %(airlineid)s and flightnumber= %(flightnumber)s UNION SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus as a join ( select operating_id from codeshares where DATE(depscheduled)=DATE( %(date)s) and codeshare_airlineid= %(airlineid)s and codeshare_flightnumber= %(flightnumber)s) as c on a.id = c.operating_id limit 1;",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber), 'date': str(date)})
            #search in DB only for operating flights
            #cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where airlineid=%(airlineid)s and flightnumber=%(flightnumber)s and DATE(depscheduled)=DATE(%(date)s) limit 1;", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber),'date': str(date)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()
        if returnrow is None:
            newstatus = jsonify({'info': 'let ne obstaja'})
        else:
            newstatus = (flight_status(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15],returnrow[16],returnrow[17],returnrow[18],returnrow[19],returnrow[20])).toJson()

    return newstatus


def getSQLFlightStats(flight,days):
    host, port, database, user, password = readDBAccount()
    airlineid = re.search("[A-z]{1,2}", flight).group()
    flightnumber = re.search("[0-9]{1,5}", flight).group()
    #padding to min length 3
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
            #print("Retry DB " + str(i))
            if (i == 10):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            #search in DB for operating and for codeshare (returns operating flight)
            if (days == 7):
                #cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_7day where allflights_id in (select max(flightnumberkey) from allflightsstatus where (id in (select max(operating_id) from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s)) or (airlineid=%(airlineid)s and flightnumber=%(flightnumber)s));",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
                cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_7day as f7 join ( select max(flightnumberkey) as flightnumberkey from allflightsstatus as a join ( select max(operating_id) as operating_id from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s ) as c on a.id = c.operating_id ) as fn on f7.allflights_id = fn.flightnumberkey UNION select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_7day as f7 join (select max(flightnumberkey) as flightnumberkey from allflightsstatus as a where airlineid=%(airlineid)s and flightnumber=%(flightnumber)s ) as fn on f7.allflights_id = fn.flightnumberkey limit 1;", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
            else:
                #cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_30day where allflights_id in (select max(flightnumberkey) from allflightsstatus where (id in (select max(operating_id) from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s)) or (airlineid=%(airlineid)s and flightnumber=%(flightnumber)s));",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
                cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_30day as f30 join ( select max(flightnumberkey) as flightnumberkey from allflightsstatus as a join ( select max(operating_id) as operating_id from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s ) as c on a.id = c.operating_id ) as fn on f30.allflights_id = fn.flightnumberkey UNION select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_30day as f30 join (select max(flightnumberkey) as flightnumberkey from allflightsstatus as a where airlineid=%(airlineid)s and flightnumber=%(flightnumber)s ) as fn on f30.allflights_id = fn.flightnumberkey limit 1;", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
            #search in DB only for operating flights
            #cursor.execute("SELECT depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey from allflightsstatus where airlineid=%(airlineid)s and flightnumber=%(flightnumber)s and DATE(depscheduled)=DATE(%(date)s) limit 1;", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber),'date': str(date)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()

        print(returnrow)

        if returnrow is None:
            letstats = jsonify({'info': 'statistika za ta let ne obstaja'})
        else:
            letstats = (flight_stats(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15])).toJson()

    return letstats



def getSQLFlightCodeshares(flight,date):
    host, port, database, user, password = readDBAccount()
    date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    airlineid = re.search("[A-z]{1,2}", flight).group()
    flightnumber = re.search("[0-9]{1,5}", flight).group()
    #padding to min length 3
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
            #print("Retry DB " + str(i))
            if (i == 10):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            #search in DB for operating and for codeshare (returns operating flight)
            #cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_7day where allflights_id in (select max(flightnumberkey) from allflightsstatus where (id in (select max(operating_id) from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s)) or (airlineid=%(airlineid)s and flightnumber=%(flightnumber)s));",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
            cursor.execute("select c.operating_airlineid, c.operating_flightnumber,  c.codeshare_airlineid, c.codeshare_flightnumber from codeshares as c join (select operating_airlineid, operating_flightnumber, depscheduled from codeshares as c2 where ((c2.operating_airlineid=%(airlineid)s and c2.operating_flightnumber=%(flightnumber)s) or (c2.codeshare_airlineid=%(airlineid)s and c2.codeshare_flightnumber=%(flightnumber)s)) and DATE(c2.depscheduled)=DATE(%(date)s) limit 1) as o on c.operating_flightnumber = o.operating_flightnumber and c.operating_airlineid = o.operating_airlineid and DATE(c.depscheduled)=DATE(o.depscheduled);", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber), 'date': str(date)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass


        returnrows = cursor.fetchall()

        print("returnrows")
        print(returnrows)

        if returnrows:
            codeshares = []
            for row in returnrows:
                flightoperating = (flight_codeshare(row[0], row[1]))
                flightcodeshare = (flight_codeshare(row[2], row[3]))
                codeshares.append(flightcodeshare.__dict__)

            print(json.dumps(codeshares))
            operatingcodeshares = operating_codeshares(flightoperating,codeshares)
            operatingcodeshares = operatingcodeshares.toJson()
        else:
            operatingcodeshares = jsonify({'info': 'codeshare leti za ta let ne obstajajo'})

    return operatingcodeshares

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


class flight_stats:
    Allflights = ""
    Cancelled = ""
    Dep_OT = ""
    Dep_FE = ""
    Dep_DL = ""
    AverageTimeDep = ""
    AverageTimeDep_OT = ""
    AverageTimeDep_FE = ""
    AverageTimeDep_DL = ""
    Arr_OT = ""
    Arr_FE = ""
    Arr_DL = ""
    AverageTimeArr = ""
    AverageTimeArr_OT = ""
    AverageTimeArr_FE = ""
    AverageTimeArr_DL = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL):
        self.Allflights = Allflights
        self.Cancelled = Cancelled
        self.Dep_OT = Dep_OT
        self.Dep_FE = Dep_FE
        self.Dep_DL = Dep_DL
        self.AverageTimeDep = AverageTimeDep
        self.AverageTimeDep_OT = AverageTimeDep_OT
        self.AverageTimeDep_FE = AverageTimeDep_FE
        self.AverageTimeDep_DL = AverageTimeDep_DL
        self.Arr_OT = Arr_OT
        self.Arr_FE = Arr_FE
        self.Arr_DL = Arr_DL
        self.AverageTimeArr = AverageTimeArr
        self.AverageTimeArr_OT = AverageTimeArr_OT
        self.AverageTimeArr_FE = AverageTimeArr_FE
        self.AverageTimeArr_DL = AverageTimeArr_DL



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
