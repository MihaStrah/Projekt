import time
import mysql.connector as mariadb
from writetosql import readDBAccount
import logging

logger = logging.getLogger(__name__)

def getAllFLights():
    host, port, database, user, password = readDBAccount()
    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("Successfull connection to SQL")
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            print("Retry DB " + str(i))
            if (i == 10):
                logger.error("Unsuccessful connection to SQL")
            else:
                logger.info("Retry connection to SQL")
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("SELECT OperatingCarrier, FlightNumber, max(id) FROM allflightsnewver group by OperatingCarrier, FlightNumber order by FlightNumber;")
            mariadb_connection.close()
            logger.info("Successfull select from SQL")
            i = 10
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))
            logger.error("MariaDB SQL error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful select from SQL")
            else:
                logger.info("Retry select from SQL")
            pass

    allflights = []
    allids = []
    allflights.clear()
    allids.clear()
    try:
        for OperatingCarrier, FlightNumber, id in cursor:
            allids.append(id)
            allflights.append(str(OperatingCarrier) + str(FlightNumber))
    except:
        allflights.clear()
        allids.clear()
        logger.error("Unsuccessful parsing allids, allflights")

    print(allflights)
    print(allids)

    return allflights, allids


def getAllFLightsForDay(date):
    host, port, database, user, password = readDBAccount()
    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
            logger.info("Successfull connection to SQL")
        except:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            print("Retry DB " + str(i))
            if (i == 10):
                logger.error("Unsuccessful connection to SQL")
            else:
                logger.info("Retry connection to SQL")
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute((f"SELECT id, airlineid, flightnumber, depscheduled FROM allflightsstatus where DATE(depscheduled)=DATE('{date}')"))
            mariadb_connection.close()
            i = 10
        except mariadb.Error as error:
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            i = i + 1
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))
            logger.error("MariaDB SQL error: %s", error)
            if (i == 10):
                logger.error("Unsuccessful select from SQL")
            else:
                logger.info("Retry select from SQL")
            pass

    allids = []
    allids.clear()
    try:
        for id, airlineid, flightnumber, depscheduled in cursor:
            iddata = [id, airlineid, flightnumber, depscheduled]
            allids.append(iddata)
    except:
        allids.clear()
        logger.error("Unsuccessful parsing allids")

    return allids
