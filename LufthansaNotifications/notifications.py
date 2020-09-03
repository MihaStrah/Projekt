import time
import datetime
import re
import logging
import json
import sqlite3
from applePush import sendMultipleNotifications

logger = logging.getLogger(__name__)

#preverimo MQTT sporočilo če vsebuje posodobitev o nekem letu, ki je v bazi naročenih uporabnikov
def check(data):
    update = json.loads(data)

    title = "New update for flight " + update["Update"]["FlightNumber"] + " (" + update["Update"]["ScheduledFlightDate"] + ")"
    body = update["Update"]["Message"]

    dateString = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", update["Update"]["ScheduledFlightDate"]).group()

    flightString = re.search("^([A-z]{1,2}[0-9]{1,5})$", update["Update"]["FlightNumber"]).group()

    conn = sqlite3.connect('notificationsDB/notificationUsers.db')
    c = conn.cursor()

    #pridobimo APNS žetone za uporabnike, ki so naročeni na let
    c.execute('SELECT token FROM notifications WHERE flight == ? AND date == ?', (flightString, dateString))
    rows = c.fetchall()
    conn.close()

    tokens = []

    for row in rows:
        tokens.append(row[0])

    if len(tokens) > 0:
        logger.info("subscribed: : %s, %s, %s, %s, %s", tokens, title, body, flightString, dateString)

        #pošljemo obvestilo vsem naročenim uporabnikom
        sendMultipleNotifications(tokens, title, body, update["Update"]["FlightNumber"],
                                  update["Update"]["ScheduledFlightDate"])

    return



