import time
import mysql.connector as mariadb
from writetosql import readDBAccount

def getAllFLights():
    host, port, database, user, password = readDBAccount()
    i=0
    while i < 10:
        try:
            mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
            cursor = mariadb_connection.cursor()
            i = 10
        except:
            i = i + 1
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            print("Retry DB " + str(i))
            pass

    i = 0
    while i < 10:
        try:
            cursor.execute("SELECT OperatingCarrier, FlightNumber, max(id) FROM allflightsnewver group by OperatingCarrier, FlightNumber order by FlightNumber;")
            mariadb_connection.close()
            i = 10
        except mariadb.Error as error:
            i = i + 1
            time.sleep(10)
            if (i > 3):
                time.sleep(180)
            if (i > 5):
                time.sleep(600)
            print("Mariadb Error: {}".format(error))
            print("Retry DB SELECT " + str(i))

    allflights = []
    allids = []
    allflights.clear()
    allids.clear()
    for OperatingCarrier, FlightNumber, id in cursor:
        allids.append(id)
        allflights.append(str(OperatingCarrier) + str(FlightNumber))
    print(allflights)
    print(allids)

    return allflights, allids
