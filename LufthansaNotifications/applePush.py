from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
from apns2.credentials import TokenCredentials
import logging
import collections

#https://github.com/Pr0Ger/PyAPNs2

logger = logging.getLogger(__name__)

def sendMultipleNotifications(tokens, title, body, flightString, dateString):
    costumDict = {
        "flightString": flightString,
        "dateString": dateString,
    }
    payload = Payload(alert=PayloadAlert(title=title, body=body), custom=costumDict, sound="default", badge=0)
    topic = 'com.MihaStrah.FlightTracker'
    client = APNsClient('AppleAuthentication/pushcertdev.pem', use_sandbox=True, use_alternative_port=False)
    #token_credentials = TokenCredentials(auth_key_path="AppleAuthentication/AuthKey_85KZTANBJ8.p8", auth_key_id="85KZTANBJ8", team_id="7YNLV7443U")
    #client = APNsClient(credentials=token_credentials, use_sandbox=True)
    Notification = collections.namedtuple('Notification', ['token', 'payload'])
    notifications = []

    for token in tokens:
        print("sending notification")
        #make token_hex out of token
        #token_hex = 'b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b87'
        notifications.append(Notification(payload=payload, token=token))
    client.send_notification_batch(notifications=notifications, topic=topic)
