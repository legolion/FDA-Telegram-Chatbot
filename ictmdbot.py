from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import mysql.connector
from mysql.connector import errorcode
import time
import datetime
from mysql.connector import Error
import apiai, json
updater = Updater(token='896924842:AAHqYa9P6hsb8whmpt0P8SrMpzA9eO_03pg') # Telegram API Token
dispatcher = updater.dispatcher


# Command processing
def startCommand(bot, update):
    request = apiai.ApiAI('35549880f95e4ff49d0126fd9c447ebc').text_request() # Dialogflow API Token
    request.lang = 'en'
    request.session_id = 'ictmdbot' # ID dialog session (for bot training)
    request.query = update.message.text # Send request to AI with the user message
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Take JSON answer
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        bot.send_mexessage(chat_id=update.message.chat_id, text='I dont understand!')

def routeCommand(bot, update):
    whole_message = update.message.text
    split_message = whole_message.split()
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='dbictmd',
                                             user='root',
                                             password='')
        sql_insert_query = " INSERT INTO `eportalissuetbl`(`case_number`, `issue_desc`, `date_issued`, `requesting_user`,`requesting_user_id`) VALUES (" \
                           "'"+split_message[1]+"','"+split_message[2]+"','"+time.strftime("%Y%m%d")+"','"+update.message.from_user.first_name + "','"+str(update.message.from_user.id)+"')"
        print(sql_insert_query)
        cursor = connection.cursor()
        result = cursor.execute(sql_insert_query)
        connection.commit()
        print("Record inserted successfully into table")
    except mysql.connector.Error as error:
        connection.rollback()  # rollback if any exception occured
        print("Failed inserting record into python_users table {}".format(error))
    finally:
        # closing database connection.
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    bot.send_message(
        chat_id='575891776',
        text=update.message.from_user.first_name + " : " +
        split_message[1] + ' route to ' + split_message[2])
    print("sending to harold")
    bot.send_message(
        chat_id='547285070',
        text=update.message.from_user.first_name + " : " +
        split_message[1] + ' route to ' + split_message[2])
    print("sending to ace")
    bot.send_message(chat_id=update.message.chat_id, text='Hi ' + update.message.from_user.first_name + ' case number :' + split_message[1] +
                 ' will be routed to ' + split_message[2] + ' ASAP Thank you 😇 ☺')
    print("sending reply to user")




def doneCommand(bot, update):
    whole_message = update.message.text
    split_message = whole_message.split()
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='dbictmd',
                                             user='root',
                                             password='')
        sql_insert_query = "SELECT case_number,issue_desc,requesting_user_id,id " \
                           "FROM eportalissuetbl where case_number ='" + split_message[
                               1] + "' AND status IS NULL LIMIT 1"
        print(sql_insert_query)
        cursor = connection.cursor(buffered=True)
        cursor.execute(sql_insert_query)
        record = cursor.fetchall()
        for row in record:
            user_id = row[2]
            id = row[3]
            issue = row[1]
            case = row[0]

        sql_update_query = "Update eportalissuetbl set date_finished = '" \
                           + time.strftime("%Y%m%d") + "',status = 'Done' where id = '" + str(id) + " ' "
        cursor.execute(sql_update_query)
        connection.commit()
        print("Record Updated successfully ")
        bot.send_message(
            chat_id=user_id,
            text="Hi, we already routed the application "
                 + case + " to "
                 + issue + " ,Thank you 🥳👍\n\n\n Please dont hesistate to use my command again"
                           "\n (/reroute casenumber task) \n\nuse /help for more details")

        cursor.close()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        # closing database connection.
        if (connection.is_connected()):
            connection.close()
            print("connection is closed")

def textMessage(bot, update):
    request = apiai.ApiAI('35549880f95e4ff49d0126fd9c447ebc').text_request() # Dialogflow API Token
    request.lang = 'en'
    request.session_id = 'ictmdbot' # ID dialog session (for bot training)
    request.query = update.message.text # Send request to AI with the user message
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Take JSON answer
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='I dont understand!')



# Handlers
start_command_handler = CommandHandler('start', startCommand)
test_command_handler = CommandHandler('reroute', routeCommand)
done_command_handler = CommandHandler('done', doneCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)
# Here we add the handlers to the dispatcher
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(test_command_handler)
dispatcher.add_handler(done_command_handler)
dispatcher.add_handler(text_message_handler)
# Start search for updates
updater.start_polling(clean=True)
# Stop the bot, if Ctrl + C were pressed
updater.idle()