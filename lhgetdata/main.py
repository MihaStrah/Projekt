from gettoken import getNewToken
from getflight import getFlightStatusWriteSql, getFlightCodeshares
from tryall import getAllFLights, getAllFLightsForDay
from telegrambot import telegram_bot_sendtext
from codeshares import getandwriteCodeshares
import schedule
import time
import datetime
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="pythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)


def job():
    #print("DATETIME: ", datetime.datetime.now(), " checking hour")
    # workaround
    if (datetime.datetime.now().strftime("%H") == "16"):
        #print("DATETIME: ", datetime.datetime.now(), " Hour is 21")


        dateFlight = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        notification = "DATETIME: {} ::: Job in progress ... getting flights for date: {}".format(datetime.datetime.now(), dateFlight)
        #print(notification)
        logger.info("Hour OK, started job, getting flights for date: %s", dateFlight)
        sendTG = telegram_bot_sendtext(notification)
        #print("TELEGRAM BOT: ", sendTG)
        logger.info("Sent telegram notification: %s", sendTG)

        token = getNewToken()
        allflights, allids = getAllFLights()
        getFlightStatusWriteSql(token,allflights,allids,dateFlight,3)

        notification = "DATETIME: {} ::: End of job, all flights processed for date: {}".format(datetime.datetime.now(), dateFlight)
        logger.info("Ended job, all flights processed for date: %s", dateFlight)
        #print(notification)
        sendTG = telegram_bot_sendtext(notification)
        #print("TELEGRAM BOT: ", sendTG)
        logger.info("Sent telegram notification: %s", sendTG)


        notification = "DATETIME: {} ::: Job in progress - CODESHARE ... getting flights for date: {}".format(
            datetime.datetime.now(), dateFlight)
        #print(notification)
        logger.info("Started job, getting codeshare flights for date: %s", dateFlight)
        sendTG = telegram_bot_sendtext(notification)
        #print("TELEGRAM BOT: ", sendTG)
        logger.info("Sent telegram notification: %s", sendTG)

        getandwriteCodeshares(dateFlight)

        notification = "DATETIME: {} ::: End of job - CODESHARE, all flights processed for date: {}".format(datetime.datetime.now(),
                                                                                                dateFlight)
        #print(notification)
        logger.info("Ended job, all codeshare flights processed for date: %s", dateFlight)
        sendTG = telegram_bot_sendtext(notification)
        #print("TELEGRAM BOT: ", sendTG)
        logger.info("Sent telegram notification: %s", sendTG)

    #print("DATETIME: ", datetime.datetime.now(), "Hour is not 21")
    logger.info("Hour NOT OK, sleeping")
    return

# schedule.every().day.at("21:01").do(job) NE DELA
# workaround

logger.info("Started Python script")
schedule.every().hour.at(":30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # wait one second
