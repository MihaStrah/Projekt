import time
import requests
from flask import jsonify
import json
import re
from aircraftImage import getSQLicao24
from flask_restful import Resource, Api, abort

import logging
logger = logging.getLogger(__name__)

#pridobitev trenutne lokacije letala iz opensky-network.org API
def getAircraftLocation(aircraftreg):
    try:
        aircraftregstring = re.search("[a-zA-Z0-9]{5,6}", aircraftreg).group().upper()
    except:
        return abort(400, message="Invalid Request")

    try:
        icao24 = getSQLicao24(aircraftregstring)
    except:
        return abort(500, message="API Error")

    if not icao24:
        return abort(404, message="Aircraft Not Found")

    username, password = readOSAccount()

    try:
        URL = (f"https://opensky-network.org/api/states/all?icao24={icao24}")
        print(URL)
        r = requests.get(url=URL, auth=(username, password))
        data = r.json()
        print(data)
        logger.info("opensky API call successful: %s", data)
    except:
        logger.info("opensky API call unsuccessful")
        return abort(500, message="API Error")

    try:
        state = data["states"][0]
        longitude = state[5]
        latitude = state[6]
        baro_altitude = state[7]
        velocity = state[9]
        true_track = state[10]
        currentlocation = location(longitude,latitude,baro_altitude,velocity,true_track)
        return currentlocation.toJson(), 200
    except:
        logger.info("opensky data not resolved, aircraft not found")
        return abort(404, message="Aircraft Not Found")

#razred trenutne lokacije letala
class location:
    longitude = ""
    latitude = ""
    baro_altitude = ""
    velocity = ""
    true_track = ""

    def __init__(self,longitude,latitude,baro_altitude,velocity,true_track):
        self.longitude = longitude
        self.latitude = latitude
        self.baro_altitude = baro_altitude
        self.velocity = velocity
        self.true_track = true_track

    def toJson(self):
        return self.__dict__

#branje podatkov opensky računa
def readOSAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/OSaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    username = lines[0]
    password = lines[1]
    f.close()
    return username, password