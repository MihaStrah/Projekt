import time
import mysql.connector as mariadb
from writetosql import readDBAccount

def getAllFLights():
    host, port, database, user, password = readDBAccount()
    mariadb_connection = mariadb.connect(user=user, password=password, database=database, host=host, port=port)
    cursor = mariadb_connection.cursor()

    cursor.execute("SELECT OperatingCarrier, FlightNumber, max(id) FROM allflightsnewver group by OperatingCarrier, FlightNumber order by FlightNumber;")
    mariadb_connection.close()
    allflights = []
    allids = []
    allflights.clear()
    allids.clear()
    for OperatingCarrier, FlightNumber, id in cursor:
        # print(id-1)
        allids.append(id)
        allflights.append(str(OperatingCarrier) + str(FlightNumber))
    print(allflights)
    print(allids)
    return allflights, allids