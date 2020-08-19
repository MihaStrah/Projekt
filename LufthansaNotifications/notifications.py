import time
import datetime
import re
import logging
import json
import sqlite3
from applePush import sendMultipleNotifications

logger = logging.getLogger(__name__)

def check(data):
    update = json.loads(data)

    title = "New update for flight " + update["Update"]["FlightNumber"] + " (" + update["Update"]["ScheduledFlightDate"] + ")"
    body = update["Update"]["Message"]

    dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", update["Update"]["ScheduledFlightDate"]).group()

    flightString = re.search("^([A-z]{1,2}[0-9]{1,5})$", update["Update"]["FlightNumber"]).group()

    conn = sqlite3.connect('notificationsDB/notificationUsers.db')
    c = conn.cursor()

    c.execute('SELECT token FROM notifications WHERE flight == ? AND date == ?', (flightString, dateString))
    #c.execute('SELECT token FROM notifications WHERE flight == ? AND date == ?', ("LH997", "2020-08-12"))
    rows = c.fetchall()
    conn.close()

    tokens = []

    for row in rows:
        tokens.append(row[0])

    if len(tokens) > 0:
        #sendMultipleNotifications(tokens, title, body, flightString, dateString)
        logger.info("subscribed: : %s, %s, %s, %s, %s", tokens, title, body, flightString, dateString)

    sendMultipleNotifications(tokens, title, body, update["Update"]["FlightNumber"], update["Update"]["ScheduledFlightDate"])

    return



