import mysql.connector as mariadb
import time
import logging

logger = logging.getLogger(__name__)

def writeOneFlightToSql(flight, id):
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


    mariadb_connection.commit()
    mariadb_connection.close()


def writeOneFlightToSqlOperatingRetry(flight, id):
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
            cursor.execute("INSERT INTO allflightsstatus (depairport,depscheduled,depscheduledUTC,depactual,depactualUTC,depterminal,depgate,deptimestatus,arrairport,arrscheduled,arrscheduledUTC,arractual,arractualUTC,arrterminal,arrgate,arrtimestatus,aircraftcode,aircraftreg,airlineid,flightnumber,flightstatus,flightnumberkey,otheroperating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (flight.depairport,flight.depscheduled,flight.depscheduledUTC,flight.depactual,flight.depactualUTC,flight.depterminal,flight.depgate,flight.deptimestatus,flight.arrairport,flight.arrscheduled,flight.arrscheduledUTC,flight.arractual,flight.arractualUTC,flight.arrterminal,flight.arrgate,flight.arrtimestatus,flight.aircraftcode,flight.aircraftreg,flight.airlineid,flight.flightnumber,flight.flightstatus,id,1))
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