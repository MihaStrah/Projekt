import logging
import datetime
import re
from opensky import getAircraftImage
from getflight import getFlightStatus, getAircraftModel, getAirlineName, getAirportName
from sqldata import getSQLFlightStatus
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Message, ChatAction, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import time
from openskyAPI import getAirplanesAboveMe

#nastavimo beleženje
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename="telegrambot_logs_out/telegrambotPythonScriptLog.log", filemode='a')
logger = logging.getLogger(__name__)

#možne veje
START, FLIGHT, FLIGHTDATE, STATUSMORE, REQLOCATION, LOCATION = range(6)

#definiramo delovanje Bota
def start(update, context):
    reply_keyboard = [['OK']]
    update.message.reply_text(
        'Hello, I can check a flight status for you!', parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START

def flight(update, context):
    reply_keyboard = [['AC875', 'LH111', 'LH2368', 'TP6703', 'OU416']]
    update.message.reply_text(
        'Flight Number <i>(LH000)</i>:', parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FLIGHT

def flightdate(update, context):
    reply_keyboard = [[str(datetime.date.today() - datetime.timedelta(days=2)), str(datetime.date.today() - datetime.timedelta(days=1)), str(datetime.date.today()), str(datetime.date.today() + datetime.timedelta(days=1)), str(datetime.date.today() + datetime.timedelta(days=2))]]
    user = update.message.from_user
    logger.info("%s: $Flight of$ %s", user.first_name, update.message.text)
    context.user_data['flight'] = re.search("^[A-z]{1,2}[0-9]{1,6}$", update.message.text).group()
    update.message.reply_text('Flight Date <i>(YYYY-MM-DD)</i>:',parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FLIGHTDATE

def flightstatus(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    reply_keyboard = [['Departure', 'Arrival', 'Equipment', 'Done']]
    user = update.message.from_user
    logger.info("%s: $Date of$ %s", user.first_name, update.message.text)
    context.user_data['flightdate'] = update.message.text
    context.user_data['aircraftmodel'] = ""
    context.user_data['marketingairlinename'] = ""
    context.user_data['depairportname'] = ""
    context.user_data['arrairportname'] = ""
    context.user_data['aircraftimage'] = ""
    context.user_data['operatingairlinename'] = ""

    datestring = re.search("^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$", context.user_data['flightdate']).group()
    date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
    if ((datetime.datetime.now() - datetime.timedelta(days=3)) < date):
        logger.info("%s: $Getting flight from LH API$ $flight: %s, date: %s$", user.first_name,
                    context.user_data["flight"], context.user_data["flightdate"])
        flightstatus = getFlightStatus(context.user_data["flight"], context.user_data["flightdate"])
    else:
        logger.info("%s: $Getting flight from DB$ $flight: %s, date: %s$", user.first_name, context.user_data["flight"],
                    context.user_data["flightdate"])
        flightstatus = getSQLFlightStatus(context.user_data["flight"], context.user_data["flightdate"])

    context.user_data['flightstatus'] = flightstatus
    if (flightstatus.depairport != ""):
        global flightstatuscodes, flightstatusdef
        if (flightstatus.flightstatusdef in flightstatuscodes):
            flightstatus.flightstatusdef = flightstatusdef[flightstatuscodes.index(flightstatus.flightstatusdef)]
        context.user_data['marketingairlinename'] = getAirlineName((context.user_data[("flight")])[:2])
        context.user_data['depairportname'] = getAirportName(flightstatus.depairport)
        context.user_data['arrairportname'] = getAirportName(flightstatus.arrairport)
        update.message.reply_text('<b>{}</b>{} 🛩 {} \n'
                                  '<b>{}</b>{} -> <b>{}</b>{}\n'
                                  'Status: <b>{}</b>'.format(context.user_data["flight"].upper(),context.user_data['marketingairlinename'],context.user_data["flightdate"],flightstatus.depairport,context.user_data['depairportname'],flightstatus.arrairport,context.user_data['arrairportname'],flightstatus.flightstatusdef), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        reply_keyboard = [['AC875', 'LH111', 'LH2368', 'TP6703', 'OU416']]
        update.message.reply_text('This flight does not exist on this day, try another!', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return FLIGHT

    return STATUSMORE

def departure(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    reply_keyboard = [['Done', 'Arrival', 'Equipment']]
    user = update.message.from_user
    logger.info("%s: $Option: %s$", user.first_name, update.message.text)
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
    update.message.reply_text('Departure: <b>{}</b>{} 🛫\n'
                                  'Scheduled: <b>{}</b>\n'
                                  'Actual: <b>{}</b>\n'
                                  'Time Status: <b>{}</b>\n'
                                  'Terminal: <b>{}</b> '
                                  'Gate: <b>{}</b>'.format(flightstatus.depairport,context.user_data['depairportname'],depscheduled,depactual,flightstatus.deptimestatusdef,flightstatus.depterminal,flightstatus.depgate), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STATUSMORE

def arrival(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    reply_keyboard = [['Departure', 'Done', 'Equipment']]
    user = update.message.from_user
    logger.info("%s: $Option: %s$", user.first_name, update.message.text)
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
    update.message.reply_text('Arrival: 🛬 <b>{}</b>{}\n'
                                  'Scheduled: <b>{}</b>\n'
                                  'Actual: <b>{}</b>\n'
                                  'Time Status: <b>{}</b>\n'
                                  'Terminal: <b>{}</b> '
                                  'Gate: <b>{}</b>'.format(flightstatus.arrairport,context.user_data['arrairportname'],arrscheduled,arractual,flightstatus.arrtimestatusdef,flightstatus.arrterminal,flightstatus.arrgate), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STATUSMORE

def equipment(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    reply_keyboard = [['Departure', 'Arrival', 'Done']]
    user = update.message.from_user
    logger.info("%s: $Option: %s$", user.first_name, update.message.text)
    flightstatus = context.user_data['flightstatus']
    if(context.user_data['operatingairlinename'] == ""):
        context.user_data['operatingairlinename'] = getAirlineName(flightstatus.airlineid)
    if (context.user_data['aircraftmodel'] == ""):
        context.user_data['aircraftmodel'] = flightstatus.aircraftcode
    if (len(context.user_data['aircraftmodel']) < 4):
        context.user_data['aircraftmodel'] = getAircraftModel(flightstatus.aircraftcode)
    update.message.reply_text( 'Operating Carrier Flight: <b>{}{}</b>{}\n'
                                  'Aircraft: <b>{}</b>\n'
                                  'Aircraft Registration: <b>{}</b>\n'.format(flightstatus.airlineid,flightstatus.flightnumber,context.user_data['operatingairlinename'],context.user_data['aircraftmodel'],flightstatus.aircraftreg), parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    logger.info("%s: $Getting aircraft image for registration %s$",user.first_name, flightstatus.aircraftreg)
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    if (context.user_data['aircraftimage'] == ""):
        context.user_data['aircraftimage'] = getAircraftImage(flightstatus.aircraftreg)
    if (context.user_data['aircraftimage'] != ""):
        update.message.reply_photo(photo=(f"{context.user_data['aircraftimage']}"))
        logger.info("%s $Sending aircraft image on link %s$", user.first_name, context.user_data['aircraftimage'])
    return STATUSMORE


def reqlocation(update, context):
    reply_keyboard = [[KeyboardButton(text="Send my location", request_location=True)]]
    update.message.reply_text('Please send your location:', parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return LOCATION

def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    context.user_data['userlatitude'] = user_location.latitude
    context.user_data['userlongitude'] = user_location.longitude
    #print(update.message.location)
    logger.info("%s: $Location of user is %f / %f$", user.first_name, user_location.latitude, user_location.longitude)
    update.message.reply_text('Location: <b>{} {}</b>\n'.format(user_location.latitude, user_location.longitude), parse_mode='HTML')
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
    range = 200
    airplanesaboveme = getAirplanesAboveMe(context.user_data['userlatitude'], context.user_data['userlongitude'], range)
    txt = "Airplanes in range of {}km:".format(range)
    i = 0
    for airplane in airplanesaboveme:
        txt = txt + '\nCall: {} Alt: {}m Vel: {}m/s'.format(airplane.callsign,airplane.baro_altitude,airplane.velocity)
        i = i + 1
        #print(i)
        #print(txt)
        if (i>9):
            break

    update.message.reply_text(txt,parse_mode='HTML')
    return REQLOCATION

def cancel(update, context):
    user = update.message.from_user
    logger.info("%s: #User canceled the conversation.#", user.first_name)
    update.message.reply_text('Bye', reply_markup=ReplyKeyboardRemove())
    user_data.clear()

    return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    print('Update "%s" caused error "%s"', update, context.error)

#zagon in konfiguracija Bota
def main():
    logger.info("telegrambot started")
    bot_token = readTGAccount()
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            START: [MessageHandler(Filters.text, flight)],

            FLIGHT: [MessageHandler(Filters.regex('^[A-z]{1,2}[0-9]{1,6}$'), flightdate),
                     MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus),
                     MessageHandler(Filters.regex('^location'), reqlocation)],

            FLIGHTDATE: [MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus),
                         MessageHandler(Filters.regex('^[A-z][A-z][0-9]{1,4}$'), flightdate)],

            STATUSMORE: [MessageHandler(Filters.regex('^Departure$'), departure),
                         MessageHandler(Filters.regex('^Arrival$'), arrival),
                         MessageHandler(Filters.regex('^Equipment$'), equipment),
                         MessageHandler(Filters.regex('^Done$'), flight),
                         MessageHandler(Filters.regex('^[A-z]{1,2}[0-9]{1,6}$'), flightdate),
                         MessageHandler(Filters.regex('^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$'), flightstatus)],

            REQLOCATION: [MessageHandler(Filters.regex('No'), flight),
                         MessageHandler(Filters.location, location),
                         MessageHandler(Filters.regex('^Send my location'), location)],

            LOCATION: [MessageHandler(Filters.location, location),
                       MessageHandler(Filters.regex('^Send my location'), location)]
        },

        fallbacks=[CommandHandler('cancel', cancel),CommandHandler('start', start),CommandHandler('aboveme', reqlocation)]
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


#branje Telegram računa
def readTGAccount():
    import os
    path = os.path.abspath(os.path.dirname(__file__))
    fullpath = os.path.join(path, "authentication/TGaccount.txt")
    f = open(fullpath, "r")
    lines = f.read().splitlines()
    bot_token = lines[0]
    f.close()
    return bot_token

#definicije statusov
flightstatuscodes = ["CD","DP","LD","RT","NA"]
flightstatusdef = ["Flight Cancelled","Flight Departed","Flight Landed","Flight Rerouted","No status"]
timestatuscodes = ["FE","NI","OT","DL","NO"]
timestatusdef = ["Flight Early","Next Information","Flight On Time","Flight Delayed","No status"]

#zagon programa
if __name__ == '__main__':
    main()
