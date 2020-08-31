import time
import mysql.connector as mariadb
import re
import logging
import requests
import json
import datetime
from flask import jsonify
from flask_restful import Resource, Api, abort

logger = logging.getLogger(__name__)


# API https://www.airport-data.com

def getAircraftImageURL(aircraftreg):

    try :
        aircraftregstring = re.search("[a-zA-Z0-9]{5,6}", aircraftreg).group().lower()
    except:
        return abort(400, message="Invalid Request")

    try:
        #try with aircraftregstring with "-" on second character
        N = 1
        newaircraftregstring = aircraftregstring[: N] + "-" + aircraftregstring[N:]
        URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={newaircraftregstring}&n=1")
        # print(URL)
        r = requests.get(url=URL)
        data = r.json()
        # print(data)
        aircraftImageURL = data["data"][0]["image"]
        aircraftImageURL = aircraftImageURL.replace('/thumbnails', '')
        photographer = data["data"][0]["photographer"]
        aircraftimage = AircraftImage(aircraftImageURL, photographer)

    except:
        aircraftImageURL = ""
        logger.info("airport-data image API call unsuccessful, trying with '-' option 2")

    if (aircraftImageURL == ""):
        try:
            #try with aircraftregstring with "-" on third character
            N = 2
            newaircraftregstring = aircraftregstring[: N] + "-" + aircraftregstring[N:]
            URL = (f"https://www.airport-data.com/api/ac_thumb.json?r={newaircraftregstring}&n=1")
            r = requests.get(url=URL)
            data = r.json()
            # print(data)
            aircraftImageURL = data["data"][0]["image"]
            aircraftImageURL = aircraftImageURL.replace('/thumbnails', '')
            photographer = data["data"][0]["photographer"]
            aircraftimage = AircraftImage(aircraftImageURL, photographer)
            logger.info("airport-data image API call successful")

        except:
            aircraftImageURL = ""
            logger.info("airport-data image API call unsuccessful, trying with 'icao24'")
        if (aircraftImageURL == ""):
            try:
                icao24 = getSQLicao24(aircraftregstring)
            except:
                return abort(500, message="API Error")
            try:
                #try with icao24
                URL = (f"https://www.airport-data.com/api/ac_thumb.json?m={icao24}&n=1")
                r = requests.get(url=URL)
                data = r.json()
                aircraftImageURL = data["data"][0]["image"]
                aircraftImageURL = aircraftImageURL.replace('/thumbnails', '')
                photographer = data["data"][0]["photographer"]
                aircraftimage = AircraftImage(aircraftImageURL, photographer)
                logger.info("airport-data image API call successful")

            except:
                logger.info("airport-data image API call unsuccessful")
                return abort(404, message="Image URL Not Found")

    return aircraftimage.toJson(), 200



def getSQLicao24(aircraftreg):
    aircraftregstring = re.search("[a-zA-Z0-9]{5,6}", aircraftreg).group().lower()
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
                time.sleep(1)
            if (i > 5):
                time.sleep(1)
            # print("Retry DB " + str(i))
            if (i == 10):
                logger.error("DB error, ABORT")
                icao24 = ""
                return icao24
            else:
                logger.info("DB error, retry")
            pass
    i = 0
    while i < 3:
        try:
            cursor.execute(
                "SELECT icao24 from aircraftDatabase where REPLACE(registration,'-','') LIKE %(registration)s limit 1;",
                {'registration': str(aircraftregstring)})
            mariadb_connection.close()
            i = 3
        except mariadb.Error as error:
            i = i + 1
            time.sleep(1)
            if (i > 0):
                time.sleep(1)
            if (i > 2):
                time.sleep(1)
            # print("Mariadb Error: {}".format(error))
            # print("Retry DB SELECT " + str(i))
            logger.error("DB error: %s", error)
            if (i == 3):
                logger.error("DB error, ABORT")
                icao24 = ""
                return icao24
            else:
                logger.info("DB error, retry")
            pass

        returnrow = cursor.fetchone()
        if returnrow is None:
            icao24 = ""
        else:
            icao24 = returnrow[0]

    return icao24


class AircraftImage:
    aircraftimage= ""
    photographer = ""

    def toJson(self):
        #return json.dumps(self, default=lambda o: o.__dict__)
        return self.__dict__

    def __init__(self, aircraftImageURL, photographer):
        self.aircraftimage = aircraftImageURL
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