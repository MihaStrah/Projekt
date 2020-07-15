import time
import mysql.connector as mariadb
import re
import logging
import requests
import json
from flask import jsonify

logger = logging.getLogger(__name__)


# API https://www.airport-data.com

def getAircraftImageURL(aircraftreg):
    icao24 = getSQLicao24(aircraftreg)

    if (aircraftreg == ""):
        return jsonify({'info': 'no image found'})

    try:
        URL = (f"https://www.airport-data.com/api/ac_thumb.json?m={icao24}&n=1")
        r = requests.get(url=URL)
        data = r.json()
        aircraftimage = data["data"][0]["image"]
        aircraftimage = aircraftimage.replace('/thumbnails', '')
        photographer = data["data"][0]["photographer"]
        aircraftimagejson = aircraft_image(aircraftimage,photographer).toJson()
        logger.info("airport-data image API call successful")
    except:
        aircraftimage = ""
        logger.info("airport-data image API call unsuccessful, trying with '-'")

    if (aircraftimage == ""):
        try:
            # try with aircraftreg with "-" on second character
            N = 1
            aircraftreg = aircraftreg[: N] + "-" + aircraftreg[N:]
            URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={aircraftreg}&n=1")
            r = requests.get(url=URL)
            data = r.json()
            # print(data)
            aircraftimage = data["data"][0]["image"]
            aircraftimage = aircraftimage.replace('/thumbnails', '')
            photographer = data["data"][0]["photographer"]
            aircraftimagejson = aircraft_image(aircraftimage, photographer).toJson()
            logger.info("airport-data image API call successful")
        except:
            aircraftimage = ""
            logger.info("airport-data image API call unsuccessful, trying with '-' option 2")
        if (aircraftimage == ""):
            try:
                # try with aircraftreg with "-" on third character
                N = 2
                aircraftreg = aircraftreg[: N] + "-" + aircraftreg[N:]
                URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={aircraftreg}&n=1")
                # print(URL)
                r = requests.get(url=URL)
                data = r.json()
                # print(data)
                aircraftimage = data["data"][0]["image"]
                aircraftimage = aircraftimage.replace('/thumbnails', '')
                photographer = data["data"][0]["photographer"]
                aircraftimagejson = aircraft_image(aircraftimage, photographer).toJson()
            except:
                logger.info("airport-data image API call unsuccessful")
                return jsonify({'info': 'no image found'})

    return aircraftimagejson


def getSQLicao24(aircraftreg):
    host, port, database, user, password = readDBAccount()
    i = 0
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
            # print("Retry DB " + str(i))
            if (i == 10):
                logger.error("DB error, ABORT")
            else:
                logger.info("DB error, retry")
            pass
    i = 0
    while i < 3:
        try:
            cursor.execute(
                "SELECT icao24 from aircraftDatabase where REPLACE(registration,'-','') LIKE %(registration)s limit 1;",
                {'registration': str(aircraftreg)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(1)
            if (i > 0):
                time.sleep(2)
            if (i > 2):
                time.sleep(3)
            # print("Mariadb Error: {}".format(error))
            # print("Retry DB SELECT " + str(i))
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


class aircraft_image:
    aircraftimage = ""
    photographer = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, aircraftimage, photographer):
        self.aircraftimage = aircraftimage
        self.photographer = photographer


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