import time
import datetime
import mysql.connector as mariadb
import re
import logging
import json
from flask import jsonify
from liveLufthansa import getFlightStatusObjectLufthansa

from flask_restful import Resource, Api, abort

logger = logging.getLogger(__name__)



def getSQLFlightStatus(flight, date):
    host, port, database, user, password = readDBAccount()

    try:
        date = re.match("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
        airlineid = re.search("[A-z]{1,2}", flight).group()
        flightnumber = re.search("[0-9]{1,4}", flight).group()
        #padding to min length 3
        flightnumber = str(flightnumber).zfill(3)
    except:
        return abort(400, message="Invalid Request")

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
                return abort(500, message="Database Error")
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
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass


        returnrow = cursor.fetchone()
        mariadb_connection.close()

        if returnrow is None:
            return abort(404, message="Flight Not Found")
        else:
            newstatus = (FlightStatus(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15],returnrow[16],returnrow[17],returnrow[18],returnrow[19],returnrow[20]))
            return newstatus.toJson(), 200


def getSQLFlightStats(flight,days):
    host, port, database, user, password = readDBAccount()

    try:
        airlineid = re.search("[A-z]{1,2}", flight).group()
        flightnumber = re.search("[0-9]{1,5}", flight).group()
        #padding to min length 3
        flightnumber = str(flightnumber).zfill(3)
    except:
        return abort(400, message="Invalid Request")

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
                return {'info': 'database error'}
            else:
                return abort(500, message="Database Error")
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

            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()


        if returnrow is None:
            return abort(404, message="Flight Not Found")
        else:
            flightStats = (FlightStats(returnrow[0],returnrow[1],returnrow[2],returnrow[3],returnrow[4],returnrow[5],returnrow[6],returnrow[7],returnrow[8],returnrow[9],returnrow[10],returnrow[11],returnrow[12],returnrow[13],returnrow[14],returnrow[15]))
            return flightStats.toJson(), 200


#this one also gets data from lufthansa for last day
def getSQLFlightPastStats(flight):
    host, port, database, user, password = readDBAccount()

    try:
        airlineid = re.search("[A-z]{1,2}", flight).group()
        flightnumber = re.search("[0-9]{1,5}", flight).group()
        #padding to min length 3
        flightnumber = str(flightnumber).zfill(3)
    except:
        return abort(400, message="Invalid Request")

    flightString = airlineid + flightnumber

    daybeforeyesterday = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    startdate = (datetime.date.today() - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    enddate = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")

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
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            #search in DB for operating and for codeshare (returns operating flight)
            cursor.execute("select depscheduled, deptimestatus, arrtimestatus, flightstatus from allflightsstatus where (DATE(depscheduled) between DATE(%(startdate)s) and DATE(%(enddate)s)) and airlineid=%(airlineid)s and flightnumber=%(flightnumber)s;", {'startdate': str(startdate), 'enddate': str(enddate), 'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass

        flightPastStatArray = []

        try:
            i = 0
            for depscheduled, deptimestatus, arrtimestatus, flightstatus in cursor:
                i = 1
                flightPastStat = FlightPastStat(depscheduled, deptimestatus, arrtimestatus, flightstatus)
                flightPastStatArray.append(flightPastStat.toJson())
            if i == 0:
                return abort(404, message="Flight Not Found")
            try:
                yesterdayStatus = getFlightStatusObjectLufthansa(flightString, yesterday)
                flightPastStat = FlightPastStat(yesterdayStatus["depscheduled"], yesterdayStatus["deptimestatus"], yesterdayStatus["arrtimestatus"], yesterdayStatus["flightstatus"])
                flightPastStatArray.append(flightPastStat.toJson())
            except:
                logger.info("No flight yesterday for past stat")

            #check if lhgetdata is in progress
            start = '22:00:00'
            end = '09:00:00'
            current_time = datetime.datetime.today().strftime("%H:%M:%S")
            if ((current_time > start) | (current_time < end)):
                try:
                    yesterdayStatus = getFlightStatusObjectLufthansa(flightString, daybeforeyesterday)
                    flightPastStat = FlightPastStat(yesterdayStatus["depscheduled"], yesterdayStatus["deptimestatus"],
                                                    yesterdayStatus["arrtimestatus"], yesterdayStatus["flightstatus"])
                    flightPastStatArray.append(flightPastStat.toJson())
                except:
                    logger.info("No flight yesterday for past stat (lhgetdata in progress)")

            cursor.close()
            mariadb_connection.close()
            return {'flightDayArray':flightPastStatArray}, 200

        except:
            cursor.close()
            mariadb_connection.close()
            flightPastStatArray.clear()
            return abort(404, message="Flight Not Found")


def getSQLFlightCodeshares(flight,date):
    host, port, database, user, password = readDBAccount()

    try:
        date = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
        airlineid = re.search("[A-z]{1,2}", flight).group()
        flightnumber = re.search("[0-9]{1,5}", flight).group()
        #padding to min length 3
        flightnumber = str(flightnumber).zfill(3)
    except:
        return abort(400, message="Invalid Request")

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
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass

    i = 0
    while i < 3:
        try:
            #search in DB for operating and for codeshare (returns operating flight)
            #cursor.execute("select Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL from flightstats_7day where allflights_id in (select max(flightnumberkey) from allflightsstatus where (id in (select max(operating_id) from codeshares where codeshare_airlineid=%(airlineid)s and codeshare_flightnumber=%(flightnumber)s)) or (airlineid=%(airlineid)s and flightnumber=%(flightnumber)s));",{'airlineid': str(airlineid), 'flightnumber': str(flightnumber)})
            cursor.execute("select c.operating_airlineid, c.operating_flightnumber,  c.codeshare_airlineid, c.codeshare_flightnumber from codeshares as c join (select operating_airlineid, operating_flightnumber, depscheduled from codeshares as c2 where ((c2.operating_airlineid=%(airlineid)s and c2.operating_flightnumber=%(flightnumber)s) or (c2.codeshare_airlineid=%(airlineid)s and c2.codeshare_flightnumber=%(flightnumber)s)) and DATE(c2.depscheduled)=DATE(%(date)s) limit 1) as o on c.operating_flightnumber = o.operating_flightnumber and c.operating_airlineid = o.operating_airlineid and DATE(c.depscheduled)=DATE(o.depscheduled);", {'airlineid': str(airlineid), 'flightnumber': str(flightnumber), 'date': str(date)})
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(2)
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i==3):
                logger.error("DB error, ABORT")
                return abort(500, message="Database Error")
            else:
                logger.info("DB error, retry")
            pass


        returnrows = cursor.fetchall()

        #("returnrows")
        #print(returnrows)

        if returnrows:
            codeshares = []
            for row in returnrows:
                flightoperating = (FlightCodeshare(row[0], row[1]))
                flightcodeshare = (FlightCodeshare(row[2], row[3]))
                codeshares.append(flightcodeshare.toJson())

            operatingcodeshares = OperatingCodeshares(flightoperating.toJson(),codeshares)
            cursor.close()
            mariadb_connection.close()
            return operatingcodeshares.toJson(), 200
        else:
            cursor.close()
            mariadb_connection.close()
            return abort(404, message="Flight Not Found")


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



class FlightStatus:
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
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

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


class FlightStats:
    allflights = ""
    cancelled = ""
    dep_OT = ""
    dep_FE = ""
    dep_DL = ""
    averageTimeDep = ""
    averageTimeDep_OT = ""
    averageTimeDep_FE = ""
    averageTimeDep_DL = ""
    arr_OT = ""
    arr_FE = ""
    arr_DL = ""
    averageTimeArr = ""
    averageTimeArr_OT = ""
    averageTimeArr_FE = ""
    averageTimeArr_DL = ""

    def toJson(self):
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

    def __init__(self, allflights, cancelled, dep_OT, dep_FE, dep_DL, averageTimeDep, averageTimeDep_OT, averageTimeDep_FE, averageTimeDep_DL, arr_OT, arr_FE, arr_DL, averageTimeArr, averageTimeArr_OT, averageTimeArr_FE, averageTimeArr_DL):
        self.allflights = allflights
        self.cancelled = cancelled
        self.dep_OT = dep_OT
        self.dep_FE = dep_FE
        self.dep_DL = dep_DL
        self.averageTimeDep = averageTimeDep
        self.averageTimeDep_OT = averageTimeDep_OT
        self.averageTimeDep_FE = averageTimeDep_FE
        self.averageTimeDep_DL = averageTimeDep_DL
        self.arr_OT = arr_OT
        self.arr_FE = arr_FE
        self.arr_DL = arr_DL
        self.averageTimeArr = averageTimeArr
        self.averageTimeArr_OT = averageTimeArr_OT
        self.averageTimeArr_FE = averageTimeArr_FE
        self.averageTimeArr_DL = averageTimeArr_DL


class FlightPastStat:
    depscheduled = ""
    deptimestatus = ""
    arrtimestatus = ""
    flightstatus = ""

    def toJson(self):
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

    def __init__(self, depscheduled, deptimestatus, arrtimestatus, flightstatus):
        self.depscheduled = depscheduled
        self.deptimestatus = deptimestatus
        self.arrtimestatus = arrtimestatus
        self.flightstatus = flightstatus



class FlightCodeshare:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        return self.__dict__
        #return json.dumps(self, default=lambda o: o.__dict__)


    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber


class FlightOperating:
    airlineid = ""
    flightnumber = ""

    def toJson(self):
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

    def __init__(self, airlineid, flightnumber):
        self.airlineid = airlineid
        self.flightnumber = flightnumber


class OperatingCodeshares:
    operating = ""
    codeshares = ""

    def toJson(self):
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

    def __init__(self, operating, codeshares):
        self.operating = operating
        self.codeshares = codeshares
