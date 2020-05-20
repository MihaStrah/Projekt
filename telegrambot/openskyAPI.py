import requests
from aircraftlocations import boundingBox
import logging
logger = logging.getLogger(__name__)

#https://opensky-network.org/apidoc/rest.html

def getAirplanesAboveMe(latitude, longtitude, range):
    lamin,lomin,lamax,lomax = boundingBox(latitude, longtitude, range)

    username, password = readOSAccount()

    states = []

    try:
        URL = (f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}")
        #print(URL)
        r = requests.get(url=URL, auth=(username, password))
        #print(r)
        data = r.json()
        #print(data)
        logger.info("opensky API call successful: %s", data)
    except:
        states.clear()
        logger.info("opensky API call unsuccessful")

    try:
        states.clear()
        statesdata = data["states"]
        #print(statesdata)
        #print(statesdata[0])
        for statedata in statesdata:
            icao24 = statedata[0]
            callsign = statedata[1]
            origin_country = statedata[2]
            time_position = statedata[3]
            last_contact = statedata[4]
            longitude = statedata[5]
            latitude = statedata[6]
            baro_altitude = statedata[7]
            on_ground = statedata[8]
            velocity = statedata[9]
            true_track = statedata[10]
            vertical_rate = statedata[1]
            sensors = statedata[12]
            geo_altitude = statedata[13]
            squawk = statedata[14]
            spi = statedata[15]
            position_source = statedata[16]

            new_airplane_status = airplane_status(icao24,callsign,origin_country,time_position,last_contact,longitude,latitude,baro_altitude,on_ground,velocity,true_track,vertical_rate,sensors,geo_altitude,squawk,spi,position_source)
            states.append(new_airplane_status)
            #print(new_airplane_status)
    except:
        states.clear()
        logger.error("opensky data not resolved")
    #print("STATES:")
    #print(states)

    return states


#user with select priviledges
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



class airplane_status:
    icao24 = ""
    callsign = ""
    origin_country = ""
    time_position = ""
    last_contact = ""
    longitude = ""
    latitude = ""
    baro_altitude = ""
    on_ground = ""
    velocity = ""
    true_track = ""
    vertical_rate = ""
    sensors = ""
    geo_altitude = ""
    squawk = ""
    spi = ""
    position_source = ""

    def __init__(self,icao24,callsign,origin_country,time_position,last_contact,longitude,latitude,baro_altitude,on_ground,velocity,true_track,vertical_rate,sensors,geo_altitude,squawk,spi,position_source):
        self.icao24 = icao24
        self.callsign = callsign
        self.origin_country = origin_country
        self.time_position = time_position
        self.last_contact = last_contact
        self.longitude = longitude
        self.latitude = latitude
        self.baro_altitude = baro_altitude
        self.on_ground = on_ground
        self.velocity = velocity
        self.true_track = true_track
        self.vertical_rate = vertical_rate
        self.sensors = sensors
        self.geo_altitude = geo_altitude
        self.squawk = squawk
        self.spi = spi
        self.position_source = position_source