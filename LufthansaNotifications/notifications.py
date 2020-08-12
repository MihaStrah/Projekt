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

    print(update["Update"])

    title = "New update for flight " + update["Update"]["FlightNumber"] + " (" + update["Update"]["ScheduledFlightDate"] + ")"
    body = update["Update"]["Message"]

    dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", update["Update"]["ScheduledFlightDate"]).group()
    print(dateString)
    flightString = re.search("^([A-z]{1,2}[0-9]{1,5})$", update["Update"]["FlightNumber"]).group()
    print(flightString)

    conn = sqlite3.connect('notificationsDB/notificationUsers.db')
    c = conn.cursor()
    print("connection ok")
    #c.execute('SELECT token FROM notifications WHERE flight == ? AND date == ?', (flightString, dateString))
    c.execute('SELECT token FROM notifications WHERE flight == ? AND date == ?', ("LH997", "2020-08-12"))
    rows = c.fetchall()
    conn.close()

    print("ids: ")
    tokens = []

    for row in rows:
        tokens.append(row[0])

    if len(tokens) > 0:
        #sendMultipleNotifications(tokens, title, body, flightString, dateString)
        print(tokens, title, body, flightString, dateString)

    return



