from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert

#https://github.com/Pr0Ger/PyAPNs2

def sendMultipleNotifications(tokens, title, body, flightString, dateString):
    costumDict = {
        "flightString": flightString,
        "dateString": dateString,
    }
    payload = Payload(alert=PayloadAlert(title=title, body=body), custom=costumDict, sound="default", badge=0)
    topic = 'com.MihaStrah.FlightTracker'
    client = APNsClient('AppleAuthentication/key.pem', use_sandbox=False, use_alternative_port=False)
    #client.send_notification(token_hex, payload, topic)

    Notification = collections.namedtuple('Notification', ['token', 'payload'])
    notifications = []
    for token in tokens:
        #make token_hex out of token
        token_hex = 'b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b87'
        notifications.append(Notification(payload=payload, token=token_hex))
    client.send_notification_batch(notifications=notifications, topic=topic)
