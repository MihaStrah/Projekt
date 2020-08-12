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
        conn = sqlite3.connect('notificationUsers.db')
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

        tokenString = re.search("[0-9]{1,50}", token).group()
        dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()

        logger.info("registerFlight: %s, %s, %s, %s", token, airline, flightnumber, date)
        logger.info("registerFlight String: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)

        conn = sqlite3.connect('notificationUsers.db')
        c = conn.cursor()
        c.execute('INSERT INTO notifications VALUES (?,?,?)', (idString, flightString, dateString))
        conn.commit()
        conn.close()
        logger.info("registerFlight OK: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)

        return jsonify({'info': 'OK'})
    except:
        return jsonify({'info': 'ERROR'})

def unregisterFlight(id, airline, flightnumber, date):
    try:
        airlineString = re.search("[A-z]{1,2}", airline).group()
        flightnumberString = re.search("[0-9]{1,5}", flightnumber).group()
        flightnumberString = str(flightnumberString).zfill(3)
        flightString = (airlineString + flightnumberString).upper()

        tokenString = re.search("[0-9]{1,50}", token).group()
        dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", date).group()

        logger.info("unregisterFlight: %s, %s, %s, %s", token, airline, flightnumber, date)
        logger.info("unregisterFlight String: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)

        conn = sqlite3.connect('notificationUsers.db')
        c = conn.cursor()
        c.execute('DELETE from notifications WHERE token == ? AND flight == ? AND date == ?', (tokenString, flightString, dateString))
        conn.commit()
        conn.close()
        logger.info("unregisterFlight OK: %s, %s, %s, %s", tokenString, airlineString, flightnumberString, dateString)
        return jsonify({'info': 'OK'})
    except:
        return jsonify({'info': 'ERROR'})
