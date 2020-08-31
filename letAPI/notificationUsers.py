import time
import datetime
import re
import logging
import json
from flask import jsonify
import sqlite3

logger = logging.getLogger(__name__)

def setDatabase():
    try:
        conn = sqlite3.connect('notificationsDB/notificationUsers.db')
        c = conn.cursor()
        c.execute("CREATE TABLE notifications (token text, flight text, date text)")
        conn.commit()
        conn.close()
    except:
        print("notificationUsers DB already exists")

def registerFlight(token, airline, flightnumber, date):
    try:
        airlineString = re.search("[A-z]{1,2}", airline).group()
        flightnumberString = re.search("[0-9]{1,5}", flightnumber).group()
        flightnumberString = str(flightnumberString).zfill(3)
        flightString = (airlineString + flightnumberString).upper()
        tokenString = re.search("[0-9A-z]{1,64}", token).group()
        dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()
    except:
        return abort(400, message="Invalid Request")

    try:
        logger.info("registerFlight: %s, %s, %s, %s", token, airline, flightnumber, date)
        logger.info("registerFlight String: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)
        conn = sqlite3.connect('notificationsDB/notificationUsers.db')
        c = conn.cursor()
        c.execute('INSERT INTO notifications VALUES (?,?,?)', (tokenString, flightString, dateString))
        conn.commit()
        conn.close()
        logger.info("registerFlight OK: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)
        return {"info":"OK"}, 200
    except:
        return abort(500, message="API Error")


def unregisterFlight(token, airline, flightnumber, date):
    try:
        airlineString = re.search("[A-z]{1,3}", airline).group()
        flightnumberString = re.search("[0-9]{1,5}", flightnumber).group()
        flightnumberString = str(flightnumberString).zfill(3)
        flightString = (airlineString + flightnumberString).upper()

        tokenString = re.search("[0-9A-z]{1,64}", token).group()
        dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()

    except:
        return abort(400, message="Invalid Request")

    try:
        if ((airlineString.upper() == "ALL") and (flightnumberString == "000")):
            logger.info("unregisterALLFlights: %s, %s, %s, %s", token, airline, flightnumber, date)
            logger.info("unregisterALLFlights String: %s, %s, %s, %s", tokenString, airlineString, flightnumberString,
                        dateString)

            conn = sqlite3.connect('notificationsDB/notificationUsers.db')
            c = conn.cursor()
            print(tokenString)
            c.execute('DELETE from notifications WHERE token == ?', (tokenString,))
            conn.commit()
            conn.close()
            logger.info("unregisterALLFlight OK: %s, %s, %s, %s", tokenString, airlineString, flightnumberString,
                        dateString)
            return {'info': 'OK'}, 200

        else:
            logger.info("unregisterFlight: %s, %s, %s, %s", token, airline, flightnumber, date)
            logger.info("unregisterFlight String: %s, %s, %s, %s", tokenString, airlineString, flightnumberString,
                        dateString)

            conn = sqlite3.connect('notificationsDB/notificationUsers.db')
            c = conn.cursor()
            c.execute('DELETE from notifications WHERE token == ? AND flight == ? AND date == ?',
                      (tokenString, flightString, dateString))
            conn.commit()
            conn.close()
            logger.info("unregisterFlight OK: %s, %s, %s, %s", tokenString, airlineString, flightnumberString,
                        dateString)
            return {'info':'OK'}, 200

    except:
        return abort(500, message="API Error")
