from gettoken import getNewToken
from getflight import getFlightStatusWriteSql
from tryall import getAllFLights
import schedule
import time
import datetime

def job():
    print("DATETIME: ", datetime.datetime.now(), " checking hour")
    if (datetime.datetime.now.strftime("%H") == "00"):
        print("DATETIME: ", datetime.datetime.now(), " hour is 00")
        #dateToday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        dateToday = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        print("DATETIME: ", datetime.datetime.now(), " ::: Job in progress ... getting flights for date: ", dateToday)
        token = getNewToken()
        allflights, allids = getAllFLights()
        getFlightStatusWriteSql(token,allflights,allids,dateToday,3)
        print("DATETIME: ", datetime.datetime.now(), "End of job, all flights processed for date: ", dateToday)
    print("DATETIME: ", datetime.datetime.now(), "hour is not 00")
    return

#schedule.every().day.at("00:30").do(job)
#spremeni datum nazaj na dan prej ko spremeniš uro!

#testno
schedule.every().hour.at(":35").do(job)



while True:
    schedule.run_pending()
    time.sleep(1) # wait one second
