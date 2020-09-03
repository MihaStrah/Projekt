from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
from apns2.credentials import TokenCredentials
import logging
import collections

logger = logging.getLogger(__name__)

#pošiljanje obvestila na APNS
def sendMultipleNotifications(tokens, title, body, flightString, dateString):
    costumDict = {
        "flightString": flightString,
        "dateString": dateString,
    }
    payload = Payload(alert=PayloadAlert(title=title, body=body), custom=costumDict, sound="default", badge=0)
    topic = 'com.MihaStrah.FlightTracker'
    token_credentials = TokenCredentials(auth_key_path="AppleAuthentication/AuthKey_85KZTANBJ8.p8", auth_key_id="85KZTANBJ8", team_id="7YNLV7443U")
    client = APNsClient(credentials=token_credentials, use_sandbox=False)
    Notification = collections.namedtuple('Notification', ['token', 'payload'])
    notifications = []

    for token in tokens:
        logger.info("notification sent to APNS")
        notifications.append(Notification(payload=payload, token=token))

    #pošljemo skupek obvestil (za vse uporabnike, ki so naročeni na let)
    client.send_notification_batch(notifications=notifications, topic=topic)