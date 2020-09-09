import time
import mysql.connector as mariadb
import re
import requests
import logging

logger = logging.getLogger(__name__)

#pridobitev icao24 iz baze
def getSQLicao24(registration):
    host, port, database, user, password = readDBAccount()

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
            cursor.execute("SELECT icao24 from aircraftDatabase where REPLACE(registration,'-','') LIKE %(registration)s limit 1;", {'registration': str(registration)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(1)
            if (i > 0):
                time.sleep(2)
            if (i > 2):
                time.sleep(3)
            logger.error("DB error: %s", error)
            if (i == 3):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()
        if returnrow is None:
            icao24 = ""
        else:
            icao24 = returnrow[0]

    return icao24

#pridobitev URL slike letala iz airport-data.com API
def getAircraftImage(registration):
    icao24 = getSQLicao24(registration)

    if (registration == ""):
        aircraftimage = ""
        return aircraftimage

    try:
        URL = (f"https://www.airport-data.com/api/ac_thumb.json?m={icao24}&n=1")
        r = requests.get(url=URL)
        data = r.json()
        aircraftimage = data["data"][0]["image"]
        aircraftimage = aircraftimage.replace('/thumbnails', '')
        logger.info("airport-data image API call successful")
    except:
        aircraftimage=""
        logger.info("airport-data image API call unsuccessful, trying with '-'")

    if (aircraftimage == ""):
        try:
            N=1
            registration = registration[ : N] + "-" + registration[N : ]
            URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={registration}&n=1")
            r = requests.get(url=URL)
            data = r.json()
            aircraftimage = data["data"][0]["image"]
            aircraftimage = aircraftimage.replace('/thumbnails', '')
            logger.info("airport-data image API call successful")
        except:
            aircraftimage = ""
            logger.info("airport-data image API call unsuccessful, trying with '-' option 2")
        if (aircraftimage == ""):
            try:
                N = 2
                registration = registration[: N] + "-" + registration[N:]
                URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={registration}&n=1")
                r = requests.get(url=URL)
                data = r.json()
                aircraftimage = data["data"][0]["image"]
                aircraftimage = aircraftimage.replace('/thumbnails', '')
            except:
                aircraftimage = ""
                logger.info("airport-data image API call unsuccessful")

    return aircraftimage


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