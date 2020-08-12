import time
import datetime
import re
import logging
import json
import ssl
import paho.mqtt.client as mqtt
from notifications import check



##IS DEPENDED ON DATABASE FROM LETAPI!


def main():
    #set database

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO, filename="LufthansaNotifications_logs_out/LufthansaNotificationsPythonScriptLog.log", filemode='a')
    logger = logging.getLogger(__name__)

    client = mqtt.Client(client_id="lufthansanotificationinstance1", clean_session=True, userdata=None, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(ca_certs="lhcerts/CAcert.pem", certfile="lhcerts/cert.pem", keyfile="lhcerts/rsaprivkey.pem", cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.enable_logger(logger=logger)

    client.connect("A35IXNRWYOLJWQ.iot.eu-central-1.amazonaws.com", port=8883, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("prd/FlightUpdate/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    check(msg.payload)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")



if __name__ == '__main__':
    main()