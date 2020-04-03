import logging
import datetime
import re
from opensky import getAircraftImage
from getflight import getFlightStatus, getAircraftModel
from sqldata import getSQLFlightStatus
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Message)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="newfile.log", filemode='w')

logger = logging.getLogger(__name__)

START, FLIGHT, FLIGHTDATE, STATUSMORE = range(4)

def start(update, context):
    reply_keyboard = [['OK']]
    update.message.reply_text(
        'Hello, I can check a flight status for you!', parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START


def flight(update, context):
    reply_keyboard = [['LH3526', 'LH122', 'EN8860']]
    update.message.reply_text(
        'Flight Number <i>(LH000)</i>:', parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FLIGHT


def flightdate(update, context):

    reply_keyboard = [[str(datetime.date.today() - datetime.timedelta(days=1)), str(datetime.date.today()), str(datetime.date.today() + datetime.timedelta(days=1))]]
    user = update.message.from_user
    logger.info("FLight of %s: %s", user.first_name, update.message.text)
    context.user_data['flight'] = update.message.text
    update.message.reply_text('Flight Date <i>(YYYY-MM-DD)</i>:',parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FLIGHTDATE


def flightstatus(update, context):
    reply_keyboard = [['Departure', 'Arrival', 'Equipment', 'Done']]
    user = update.message.from_user
    logger.info("Date of %s: %s", user.first_name, update.message.text)
    context.user_data['flightdate'] = update.message.text
    #delete previous aircraftmodel data
    context.user_data['aircraftmodel'] = ""

    datestring = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", context.user_data['flightdate']).group()
    date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
    if ((datetime.datetime.now() - datetime.timedelta(days=3)) < date):
        flightstatus = getFlightStatus(context.user_data["flight"], context.user_data["flightdate"])
        logger.info("Getting flight from LH for %s: flight: %s, date: %s", user.first_name, context.user_data["flight"], context.user_data["flightdate"])
    else:
        flightstatus = getSQLFlightStatus(context.user_data["flight"], context.user_data["flightdate"])
        logger.info("Getting flight from DB for %s: flight: %s, date: %s", user.first_name, context.user_data["flight"], context.user_data["flightdate"])

    context.user_data['flightstatus'] = flightstatus
    if (flightstatus.depairport != ""):
        global flightstatuscodes, flightstatusdef
        if (flightstatus.flightstatusdef in flightstatuscodes):
            flightstatus.flightstatusdef = flightstatusdef[flightstatuscodes.index(flightstatus.flightstatusdef)]
        update.message.reply_text('<b>{}</b> 🛩 {}\n'
                                  '<b>{}</b> -> <b>{}</b>\n'
                                  'Status: <b>{}</b>'.format(context.user_data["flight"].upper(),context.user_data["flightdate"],flightstatus.depairport,flightstatus.arrairport,flightstatus.flightstatusdef), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        reply_keyboard = [['LH3526', 'LH122', 'EN8860']]
        update.message.reply_text('This flight does not exist, try another!', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return FLIGHT

    return STATUSMORE

def departure(update, context):
    reply_keyboard = [['Done', 'Arrival', 'Equipment']]
    user = update.message.from_user
    logger.info("Option of %s: %s", user.first_name, update.message.text)
    flightstatus = context.user_data['flightstatus']


    global timestatuscodes, timestatusdef
    if (flightstatus.deptimestatusdef in timestatuscodes):
        flightstatus.deptimestatusdef = timestatusdef[timestatuscodes.index(flightstatus.deptimestatusdef)]
    try:
        depscheduled = datetime.datetime.strptime((flightstatus.depscheduled), "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d  %H:%M")
    except:
        depscheduled = flightstatus.depscheduled
    try:
        depactual = datetime.datetime.strptime((flightstatus.depactual), "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d  %H:%M")
    except:
        depactual = flightstatus.depactual
    update.message.reply_text('Departure: <b>{}</b> 🛫\n'
                                  'Scheduled: <b>{}</b>\n'
                                  'Actual: <b>{}</b>\n'
                                  'Time Status: <b>{}</b>\n'
                                  'Terminal: <b>{}</b> '
                                  'Gate: <b>{}</b>'.format(flightstatus.depairport,depscheduled,depactual,flightstatus.deptimestatusdef,flightstatus.depterminal,flightstatus.depgate), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STATUSMORE

def arrival(update, context):
    reply_keyboard = [['Departure', 'Done', 'Equipment']]
    user = update.message.from_user
    logger.info("Option of %s: %s", user.first_name, update.message.text)
    flightstatus = context.user_data['flightstatus']
    global timestatuscodes, timestatusdef
    if (flightstatus.arrtimestatusdef in timestatuscodes):
        flightstatus.arrtimestatusdef = timestatusdef[timestatuscodes.index(flightstatus.arrtimestatusdef)]
    try:
        arrscheduled = datetime.datetime.strptime((flightstatus.arrscheduled), "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d  %H:%M")
    except:
        arrscheduled = flightstatus.arrscheduled
    try:
        arractual = datetime.datetime.strptime((flightstatus.arractual), "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d  %H:%M")
    except:
        arractual = flightstatus.arractual
    update.message.reply_text('Arrival: 🛬 <b>{}</b>\n'
                                  'Scheduled: <b>{}</b>\n'
                                  'Actual: <b>{}</b>\n'
                                  'Time Status: <b>{}</b>\n'
                                  'Terminal: <b>{}</b> '
                                  'Gate: <b>{}</b>'.format(flightstatus.arrairport,arrscheduled,arractual,flightstatus.arrtimestatusdef,flightstatus.arrterminal,flightstatus.arrgate), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STATUSMORE

def equipment(update, context):
    reply_keyboard = [['Departure', 'Arrival', 'Done']]
    user = update.message.from_user
    logger.info("Option of %s: %s", user.first_name, update.message.text)
    flightstatus = context.user_data['flightstatus']
    try:
        aircraftmodel = context.user_data['aircraftmodel']
    except:
        aircraftmodel = flightstatus.aircraftcode
    if (len(aircraftmodel) < 4):
        aircraftmodel = getAircraftModel(flightstatus.aircraftcode)
        context.user_data['aircraftmodel'] = aircraftmodel
    update.message.reply_text( 'Operating Carrier Flight: <b>{}{}</b>\n'
                                  'Aircraft: <b>{}</b>\n'
                                  'Aircraft Registration: <b>{}</b>\n'.format(flightstatus.airlineid,flightstatus.flightnumber,aircraftmodel,flightstatus.aircraftreg), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    logger.info("Getting aircraft image for registration  %s for user %s", flightstatus.aircraftreg, user.first_name)
    aircraftimage = getAircraftImage(flightstatus.aircraftreg)
    logger.info("Sending aircraft image on link  %s for user %s", aircraftimage, user.first_name)
    if (aircraftimage != ""):
        update.message.reply_photo(photo=(f"{aircraftimage}"))
    return STATUSMORE

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye',
                              reply_markup=ReplyKeyboardRemove())
    user_data.clear()

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    bot_token = readTGAccount()
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            START: [MessageHandler(Filters.text, flight)],

            FLIGHT: [MessageHandler(Filters.regex('^[A-z][A-z][0-9]{1,4}$'), flightdate),
                     MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus)],

            FLIGHTDATE: [MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus),
                         MessageHandler(Filters.regex('^[A-z][A-z][0-9]{1,4}$'), flightdate)],

            STATUSMORE: [MessageHandler(Filters.regex('^Departure$'), departure),
                         MessageHandler(Filters.regex('^Arrival$'), arrival),
                         MessageHandler(Filters.regex('^Equipment$'), equipment),
                         MessageHandler(Filters.regex('^Done$'), flight),
                         MessageHandler(Filters.regex('^[A-z][A-z][0-9]{1,4}$'), flightdate),
                         MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus)],
        },

        fallbacks=[CommandHandler('cancel', cancel),CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

def readTGAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/TGaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    bot_token = lines[0]
    f.close()
    return bot_token

flightstatuscodes = ["CD","DP","LD","RT","NA"]
flightstatusdef = ["Flight Cancelled","Flight Departed","Flight Landed","Flight Rerouted","No status"]
timestatuscodes = ["FE","NI","OT","DL","NO"]
timestatusdef = ["Flight Early","Next Information","Flight On Time","Flight Delayed","No status"]


if __name__ == '__main__':
    main()
