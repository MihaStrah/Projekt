import time
import datetime
import re
import logging
import json
import ssl
import paho.mqtt.client as mqtt
from notifications import check

#za delovanje je potrebna baza iz "letAPI"

def main():
    #nastavimo dnevnik
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO, filename="LufthansaNotifications_logs_out/LufthansaNotificationsPythonScriptLog.log", filemode='a')
    logger = logging.getLogger(__name__)

    #nastavimo podatke za MQTT odjemalca
    client = mqtt.Client(client_id="lufthansanotificationinstance1", clean_session=True, userdata=None, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(ca_certs="lhcerts/CAcert.pem", certfile="lhcerts/cert.pem", keyfile="lhcerts/rsaprivkey.pem", cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.enable_logger(logger=logger)

    #povežemo se na MQTT strežnik Lufthanse
    client.connect("A35IXNRWYOLJWQ.iot.eu-central-1.amazonaws.com", port=8883, keepalive=60)

    client.loop_forever()

#ob povezavi se naročimo na vse teme
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s", str(rc))
    client.subscribe("prd/FlightUpdate/#")

#ob prihodu sporočila preverimo vsebino
def on_message(client, userdata, msg):
    check(msg.payload)

#ob padcu povezave
def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.info("Unexpected disconnection.")

#zagon programa
if __name__ == '__main__':
    main()