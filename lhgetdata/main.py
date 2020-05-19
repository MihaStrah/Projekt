from gettoken import getNewToken
from getflight import getFlightStatusWriteSql, getFlightCodeshares
from tryall import getAllFLights, getAllFLightsForDay
from telegrambot import telegram_bot_sendtext
from codeshares import getandwriteCodeshares
import schedule
import time
import datetime

def job():
    print("DATETIME: ", datetime.datetime.now(), " checking hour")

    # workaround
    if (datetime.datetime.now().strftime("%H") == "11"):
        print("DATETIME: ", datetime.datetime.now(), " Hour is 11")

        dateFlight = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        notification = "DATETIME: {} ::: Job in progress ... getting flights for date: {}".format(datetime.datetime.now(), dateFlight)
        print(notification)
        sendTG = telegram_bot_sendtext(notification)
        print("TELEGRAM BOT: ", sendTG)

        token = getNewToken()
        allflights, allids = getAllFLights()
        getFlightStatusWriteSql(token,allflights,allids,dateFlight,3)

        notification = "DATETIME: {} ::: End of job, all flights processed for date: {}".format(datetime.datetime.now(), dateFlight)
        print(notification)
        sendTG = telegram_bot_sendtext(notification)
        print("TELEGRAM BOT: ", sendTG)

        notification = "DATETIME: {} ::: Job in progress - CODESHARE ... getting flights for date: {}".format(
            datetime.datetime.now(), dateFlight)
        print(notification)
        sendTG = telegram_bot_sendtext(notification)
        print("TELEGRAM BOT: ", sendTG)

        getandwriteCodeshares(dateFlight)

        notification = "DATETIME: {} ::: End of job - CODESHARE, all flights processed for date: {}".format(datetime.datetime.now(),
                                                                                                dateFlight)
        print(notification)
        sendTG = telegram_bot_sendtext(notification)
        print("TELEGRAM BOT: ", sendTG)

    print("DATETIME: ", datetime.datetime.now(), "Hour is not 21")
    return

# schedule.every().day.at("21:01").do(job) NE DELA
# workaround
schedule.every().hour.at(":10").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # wait one second
