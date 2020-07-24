import mysql.connector as mariadb
import time
import logging

logger = logging.getLogger(__name__)

def writeOneFlightToSql(flight, id, date):
    host, port, database, user, password = readDBAccount()
    i = 0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("Successfull connection to SQL")
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            i = i + 1
            #print("Retry DB " + str(i))

            if (i == 10):
                logger.error("Unsuccessful connection to SQL")
            else:
                logger.info("Retry connection to SQL")
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("INSERT INTO allflightsstatus (depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (flight.depairport,flight.depscheduled,flight.depscheduledUTC,flight.depactual,flight.depactualUTC,flight.depterminal,flight.depgate,flight.deptimestatus,flight.arrairport,flight.arrscheduled,flight.arrscheduledUTC,flight.arractual,flight.arractualUTC,flight.arrterminal,flight.arrgate,flight.arrtimestatus,flight.aircraftcode,flight.aircraftreg,flight.airlineid,flight.flightnumber,flight.flightstatus,id))
            #print("successful write to database")
            i = 10
            logger.info("Successfull write to SQL")
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB INSERT " + str(i))
            logger.error("MariaDB SQL error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful write to SQL")
            else:
                logger.info("Retry write to SQL")
            pass

    i = 0
    while i < 10:
        try:
            interval = -7+1
            cursor.execute("INSERT IGNORE INTO flightstats_7day (allflights_id, Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL) SELECT new_update.allflights_id, new_update.Allflights, new_update.Cancelled, new_update.Dep_OT, new_update.Dep_FE, new_update.Dep_DL, new_update.AverageTimeDep, new_update.AverageTimeDep_OT, new_update.AverageTimeDep_FE, new_update.AverageTimeDep_DL, new_update.Arr_OT, new_update.Arr_FE, new_update.Arr_DL, new_update.AverageTimeArr, new_update.AverageTimeArr_OT, new_update.AverageTimeArr_FE, new_update.AverageTimeArr_DL FROM (SELECT %s as allflights_id, COUNT(CASE WHEN flightstatus is not null and flightstatus <> '' THEN 1 END) as Allflights, COUNT(CASE WHEN flightstatus='CD' THEN 1 END) as Cancelled, COUNT(CASE WHEN deptimestatus = 'OT' THEN 1 END) as Dep_OT, COUNT(CASE WHEN deptimestatus = 'FE' THEN 1 END) as Dep_FE, COUNT(CASE WHEN deptimestatus = 'DL' THEN 1 END) as Dep_DL, CAST(AVG(CASE WHEN depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep, CAST(AVG(CASE WHEN deptimestatus = 'OT' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_OT, CAST(AVG(CASE WHEN deptimestatus = 'FE' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_FE, CAST(AVG(CASE WHEN deptimestatus = 'DL' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_DL, COUNT(CASE WHEN arrtimestatus = 'OT' THEN 1 END) as Arr_OT, COUNT(CASE WHEN arrtimestatus = 'FE' THEN 1 END) as Arr_FE, COUNT(CASE WHEN arrtimestatus = 'DL' THEN 1 END) as Arr_DL, CAST(AVG(CASE WHEN arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr, CAST(AVG(CASE WHEN arrtimestatus = 'OT' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_OT, CAST(AVG(CASE WHEN arrtimestatus = 'FE' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_FE, CAST(AVG(CASE WHEN arrtimestatus = 'DL' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_DL from allflightsstatus where (DATE(depscheduled) between DATE_ADD(DATE(%s), INTERVAL %s DAY) and DATE(%s)) and flightnumberkey = %s) as new_update where Allflights <> 0 ON DUPLICATE KEY UPDATE Allflights = new_update.Allflights, Cancelled = new_update.Cancelled, Dep_OT = new_update.Dep_OT, Dep_DL = new_update.Dep_DL, Dep_FE = new_update.Dep_FE, AverageTimeDep = new_update.AverageTimeDep, AverageTimeDep_OT = new_update.AverageTimeDep_OT, AverageTimeDep_FE = new_update.AverageTimeDep_FE, AverageTimeDep_DL = new_update.AverageTimeDep_DL, Arr_OT = new_update.Arr_OT, Arr_FE = new_update.Arr_FE, Arr_DL = new_update.Arr_DL, AverageTimeArr = new_update.AverageTimeArr, AverageTimeArr_OT = new_update.AverageTimeArr_OT, AverageTimeArr_FE = new_update.AverageTimeArr_FE, AverageTimeArr_DL = new_update.AverageTimeArr_DL;", (id, date, interval, date, id))
            interval = -30+1
            cursor.execute("INSERT IGNORE INTO flightstats_30day (allflights_id, Allflights, Cancelled, Dep_OT, Dep_FE, Dep_DL, AverageTimeDep, AverageTimeDep_OT, AverageTimeDep_FE, AverageTimeDep_DL, Arr_OT, Arr_FE, Arr_DL, AverageTimeArr, AverageTimeArr_OT, AverageTimeArr_FE, AverageTimeArr_DL) SELECT new_update.allflights_id, new_update.Allflights, new_update.Cancelled, new_update.Dep_OT, new_update.Dep_FE, new_update.Dep_DL, new_update.AverageTimeDep, new_update.AverageTimeDep_OT, new_update.AverageTimeDep_FE, new_update.AverageTimeDep_DL, new_update.Arr_OT, new_update.Arr_FE, new_update.Arr_DL, new_update.AverageTimeArr, new_update.AverageTimeArr_OT, new_update.AverageTimeArr_FE, new_update.AverageTimeArr_DL FROM (SELECT %s as allflights_id, COUNT(CASE WHEN flightstatus is not null and flightstatus <> '' THEN 1 END) as Allflights, COUNT(CASE WHEN flightstatus='CD' THEN 1 END) as Cancelled, COUNT(CASE WHEN deptimestatus = 'OT' THEN 1 END) as Dep_OT, COUNT(CASE WHEN deptimestatus = 'FE' THEN 1 END) as Dep_FE, COUNT(CASE WHEN deptimestatus = 'DL' THEN 1 END) as Dep_DL, CAST(AVG(CASE WHEN depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep, CAST(AVG(CASE WHEN deptimestatus = 'OT' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_OT, CAST(AVG(CASE WHEN deptimestatus = 'FE' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_FE, CAST(AVG(CASE WHEN deptimestatus = 'DL' and depactualUTC is not null and depactualUTC <> '' THEN (timestampdiff(minute,depscheduledUTC, depactualUTC)) END) as int) as AverageTimeDep_DL, COUNT(CASE WHEN arrtimestatus = 'OT' THEN 1 END) as Arr_OT, COUNT(CASE WHEN arrtimestatus = 'FE' THEN 1 END) as Arr_FE, COUNT(CASE WHEN arrtimestatus = 'DL' THEN 1 END) as Arr_DL, CAST(AVG(CASE WHEN arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr, CAST(AVG(CASE WHEN arrtimestatus = 'OT' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_OT, CAST(AVG(CASE WHEN arrtimestatus = 'FE' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_FE, CAST(AVG(CASE WHEN arrtimestatus = 'DL' and arractualUTC is not null and arractualUTC <> '' THEN (timestampdiff(minute,arrscheduledUTC, arractualUTC)) END) as int) as AverageTimeArr_DL from allflightsstatus where (DATE(depscheduled) between DATE_ADD(DATE(%s), INTERVAL %s DAY) and DATE(%s)) and flightnumberkey = %s) as new_update where Allflights <> 0 ON DUPLICATE KEY UPDATE Allflights = new_update.Allflights, Cancelled = new_update.Cancelled, Dep_OT = new_update.Dep_OT, Dep_DL = new_update.Dep_DL, Dep_FE = new_update.Dep_FE, AverageTimeDep = new_update.AverageTimeDep, AverageTimeDep_OT = new_update.AverageTimeDep_OT, AverageTimeDep_FE = new_update.AverageTimeDep_FE, AverageTimeDep_DL = new_update.AverageTimeDep_DL, Arr_OT = new_update.Arr_OT, Arr_FE = new_update.Arr_FE, Arr_DL = new_update.Arr_DL, AverageTimeArr = new_update.AverageTimeArr, AverageTimeArr_OT = new_update.AverageTimeArr_OT, AverageTimeArr_FE = new_update.AverageTimeArr_FE, AverageTimeArr_DL = new_update.AverageTimeArr_DL;", (id, date, interval, date, id))
            #print("successful write to database")
            i = 10
            if (flight.depscheduledUTC == ''):
                logger.info("Flight null, updating alltimeflightstats")
            else:
                logger.info("Successfull write flightstats to SQL")
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB INSERT " + str(i))
            logger.error("MariaDB SQL flightstats error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful write flightstats to SQL")
            else:
                logger.info("Retry write flightstats to SQL")
            pass


    mariadb_connection.commit()
    mariadb_connection.close()



def writeCodeshareToSql(codeshare_airlineid, codeshare_flightnumber, operating_airlineid, operating_flightnumber, operating_id, depscheduled):
    host, port, database, user, password = readDBAccount()
    i = 0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("Successfull connection to SQL")
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            i = i + 1
            #print("Retry DB " + str(i))
            if (i == 10):
                logger.error("Unsuccessful connection to SQL")
            else:
                logger.info("Retry connection to SQL")
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("INSERT INTO codeshares (codeshare_airlineid, codeshare_flightnumber, operating_airlineid, operating_flightnumber, operating_id, depscheduled) values (%s,%s,%s,%s,%s,%s);", (codeshare_airlineid, codeshare_flightnumber, operating_airlineid, operating_flightnumber, operating_id, depscheduled))
            #print("successful write to database")
            i = 10
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB INSERT " + str(i))
            logger.error("MariaDB SQL error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful write to SQL")
            else:
                logger.info("Retry write to SQL")

    mariadb_connection.commit()
    mariadb_connection.close()



def updateDuplicatesSql():
    host, port, database, user, password = readDBAccount()
    i = 0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("Successfull connection to SQL")
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            i = i + 1
            #print("Retry DB " + str(i))
            if (i == 10):
                logger.error("Unsuccessful connection to SQL")
            else:
                logger.info("Retry connection to SQL")
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("update allflightsstatus set Duplicates='D' where id IN (select t.id from (select *, count(*) cnt from allflightsstatus where airlineid != '' and Duplicates is  null group by flightnumber, airlineid, depscheduled) t where t.cnt > 1);")
            #print("successful write to database")
            i = 10
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            #print("Mariadb Error: {}".format(error))
            #print("Retry DB INSERT " + str(i))
            logger.error("MariaDB SQL error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful update to SQL")
            else:
                logger.info("Retry update to SQL")

    mariadb_connection.commit()
    mariadb_connection.close()


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