import requests, json
import oauth2 as oauth
import datetime
import time
import configparser
import logging

logger = logging.getLogger(__name__)

def getNewToken():
    url = 'https://api.lufthansa.com/v1/oauth/token'
    consumer = oauth.Consumer(key ='', secret='')
    client = oauth.Client(consumer)
    id, secret = readLHAccount()
    params = "client_id=" + id + "&" + "client_secret=" + secret + "&grant_type=client_credentials"
    #print(params)
    i = 0
    while i < 10:
        try:
            resp, content = client.request(
                            url,
                            method = "POST",
                            body=params,
                            headers={'Content-type': 'application/x-www-form-urlencoded'}
                            #force_auth_header=True
                            )
            content_string = content.decode("utf-8")
            data = json.loads(content_string)
            access_token = data["access_token"]
            expires_in = data["expires_in"]
            expires_date = datetime.datetime.now() + datetime.timedelta(0, (expires_in - 15))
            #print("New token, expires: ", expires_date)
            logger.info("Successfull request to Lufthansa API for token, expires:  %s", expires_date)
            i=10
        except:
            time.sleep(10)
            if (i>3):
                time.sleep(180)
            if (i>5):
                time.sleep(600)
            #print("Retry LH token " + str(i))
            i = i + 1
            if (i == 10):
                logger.error("Error (abort) request to Lufthansa API for token")
            else:
                logger.info("Retry request to Lufthansa API for token")
            pass

    return access_token


def readLHAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/LHaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    id = lines[0]
    secret = lines[1]
    f.close()
    return id,secret