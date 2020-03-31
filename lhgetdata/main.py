from gettoken import getNewToken
from getflight import getFlightStatusWriteSql
from tryall import getAllFLights
import schedule
import time
import datetime

def job():
    print("DATETIME: ", datetime.datetime.now(), " checking hour")
    if (datetime.datetime.now().strftime("%H") == "21"):
        print("DATETIME: ", datetime.datetime.now(), " hour is 21")
        dateFlight = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        print("DATETIME: ", datetime.datetime.now(), " ::: Job in progress ... getting flights for date: ", dateFlight)
        token = getNewToken()
        allflights, allids = getAllFLights()
        getFlightStatusWriteSql(token,allflights,allids,dateFlight,3)
        print("DATETIME: ", datetime.datetime.now(), "End of job, all flights processed for date: ", dateFlight)
    print("DATETIME: ", datetime.datetime.now(), "hour is not 00")
    return

#schedule.every().day.at("21:01").do(job) NE DELA

#workaround
schedule.every().hour.at(":01").do(job)


while True:
    schedule.run_pending()
    time.sleep(1) # wait one second
