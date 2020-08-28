import time
import requests
from flask import jsonify
import json
import re
from aircraftImage import getSQLicao24

import logging
logger = logging.getLogger(__name__)

def getAircraftLocation(aircraftreg):

    aircraftregstring = re.search("[a-zA-Z0-9]{5,6}", aircraftreg).group().upper()

    if (aircraftregstring == ""):
        return jsonify({'info': 'no location found'})

    icao24 = getSQLicao24(aircraftregstring)

    if (icao24 == ""):
        return jsonify({'info': 'no location found'})

    username, password = readOSAccount()

    try:
        URL = (f"https://opensky-network.org/api/states/all?icao24={icao24}")
        r = requests.get(url=URL, auth=(username, password))
        data = r.json()
        logger.info("opensky API call successful: %s", data)
    except:
        logger.info("opensky API call unsuccessful")
        return jsonify({'info': 'no location found'})

    try:
        state = data["states"][0]
        longitude = state[5]
        latitude = state[6]
        baro_altitude = state[7]
        velocity = state[9]
        true_track = state[10]
        currentlocation = location(longitude,latitude,baro_altitude,velocity,true_track).toJson()
        return currentlocation
    except:
        logger.error("opensky data not resolved")
        return jsonify({'info': 'no location found'})


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
        return json.dumps(self, default=lambda o: o.__dict__)



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

