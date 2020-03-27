import requests, json
import oauth2 as oauth
import datetime
import time
import configparser

def getNewToken():
    url = 'https://api.lufthansa.com/v1/oauth/token'
    consumer = oauth.Consumer(key ='', secret='')
    client = oauth.Client(consumer)
    id, secret = readLHAccount()
    params = "client_id=" + id + "&" + "client_secret=" + secret + "&grant_type=client_credentials"
    print(params)
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
            print("New token, expires: ", expires_date)
            i=10
        except:
            time.sleep(10)
            print("retry " + str(i))
            i = i + 1
            pass

    return access_token


def readLHAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    print(path)
    fullpath = os.path.join(path, "authentication/LHaccount.txt")
    print(fullpath)
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    id = lines[0]
    print(id)
    secret = lines[1]
    print(secret)
    f.close()
    return id,secret