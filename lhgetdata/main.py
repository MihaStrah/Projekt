from gettoken import getNewToken
from getflight import getFlightStatusWriteSql, getFlightCodeshares
from allflights import getAllFLights, getAllFLightsForDay
from telegrambot import telegram_bot_sendtext
from codeshares import getandwriteCodeshares
import schedule
import time
import datetime
import logging

def job():
    #preverimo uro, in ob 18 uri po strežniškem času nadaljujemo
    if (datetime.datetime.now().strftime("%H") == "18"):

        #določimo dan, za katerega bomo pridobivali lete
        dateFlight = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        #pošljemo sporočilo o začetku in vpišemo v dnevnik
        notification = "DATETIME: {} ::: Job in progress ... getting flights for date: {}".format(datetime.datetime.now(), dateFlight)
        logger.info("Hour OK, started job, getting flights for date: %s", dateFlight)
        sendTG = telegram_bot_sendtext(notification)
        logger.info("Sent telegram notification: %s", sendTG)

        #pridobimo nov token za Lufthansa API
        token = getNewToken()

        #pridobimo vse možne lete za katere bomo preverili status
        allflights, allids = getAllFLights()

        #preverimo status vsakega leta na Lufthansa API in let vpišemo v bazo
        getFlightStatusWriteSql(token, allflights, allids, dateFlight, 4)

        #vpišemo v beležnik
        logger.info("Ended job, all flights processed for date: %s", dateFlight)
        logger.info("Started job, getting codeshare flights for date: %s", dateFlight)

        #pridobimo deljene lete iz Lufthansa API in jih vpišemo v bazo
        getandwriteCodeshares(dateFlight)

        #pošljemo sporočilo o koncu in vpišemo v dnevnik
        notification = "DATETIME: {} ::: End of job, all flights processed (regular + codeshare) for date: {}".format(datetime.datetime.now(), dateFlight)
        logger.info("Ended job, all codeshare flights processed for date: %s", dateFlight)
        sendTG = telegram_bot_sendtext(notification)
        logger.info("Sent telegram notification: %s", sendTG)

    logger.info("Hour NOT OK, sleeping")
    return

#konfiguracija dnevnika
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="lhgetdata_logs_out/lhgetdataPythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)

logger.info("lhgetdata started")

#konfiguracija zagona opravila vsako uro ob :01
schedule.every().hour.at(":01").do(job)

while True:
    #zagon časovnega razporejevalnika
    schedule.run_pending()
    time.sleep(1)






