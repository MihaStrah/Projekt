import requests

def telegram_bot_sendtext(bot_message):
    bot_token, bot_chatID = readTGAccount()
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def readTGAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/TGaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    bot_chatID = lines[0]
    bot_token = lines[1]
    f.close()
    return bot_token,bot_chatID


