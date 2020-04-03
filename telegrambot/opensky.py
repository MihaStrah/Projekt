import time
import mysql.connector as mariadb
import re
import requests

def getSQLicao24(registration):
    host, port, database, user, password = readDBAccount()

    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
        except:
            i = i + 1
            time.sleep(1)
            if (i > 3):
                time.sleep(2)
            if (i > 5):
                time.sleep(3)
            print("Retry DB " + str(i))
            pass

    i = 0


    while i < 10:
        try:
            cursor.execute("SELECT icao24 from aircraftDatabase where REPLACE(registration,'-','') LIKE %(registration)s limit 1;", {'registration': str(registration)})
            mariadb_connection.close()
            i = 10
        except mariadb.Error as error:
            i = i + 1
            time.sleep(1)
            if (i > 3):
                time.sleep(2)
            if (i > 5):
                time.sleep(3)
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))

        returnrow = cursor.fetchone()
        if returnrow is None:
            icao24 = ""
        else:
            icao24 = returnrow[0]

    return icao24


#API https://www.airport-data.com
def getAircraftImage(registration):
    icao24 = getSQLicao24(registration)
    try:
        URL = (f"https://www.airport-data.com/api/ac_thumb.json?m={icao24}&n=1")
        r = requests.get(url=URL)
        data = r.json()
        print(data)
        aircraftimage = data["data"][0]["image"]
        aircraftimage = aircraftimage.replace('/thumbnails', '')
    except:
        aircraftimage=""

    return aircraftimage


#user with select priviledges
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

