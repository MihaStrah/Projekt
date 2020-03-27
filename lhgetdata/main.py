from gettoken import getNewToken
from getflight import getFlightStatusWriteSql
from tryall import getAllFLights
import schedule
import time
import datetime

def job():
    dateToday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    print("DATETIME: ", datetime.datetime.now(), " ::: Job in progress ... getting flights for date: ", dateToday)
    token = getNewToken()
    allflights, allids = getAllFLights()
    getFlightStatusWriteSql(token,allflights,allids,dateToday,3)
    print("DATETIME: ", datetime.datetime.now(), "End of job, all flights processed for date: ", dateToday)
    return

schedule.every().day.at("21:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1) # wait one second