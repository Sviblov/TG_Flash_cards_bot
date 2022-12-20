#Telegram Bot

import logging
import os


from threading import Thread
from modules.threads.queueScheduler import setAnotherThread


import telebot

#importing handlers
from modules.handlers.user import welcome_command_user, any_message_user, welcome_user_callback
from modules.handlers.admin import welcome_command_admin, any_message_admin, welcome_admin_callback

from modules.filters.isAdminFilter import isAdminFilter

#DB connection and Markup setup

from modules.utils.IGT_Mongo import Database




# creating bot

if os.environ.get('DEBUG')=='1':
    bottoken = os.environ.get('BOT_KEY_DEV')
    bot = telebot.TeleBot(os.environ.get('BOT_KEY_DEV'))
    DB_name = 'VR_Database'
    DB=Database(URL = os.environ.get('DB_STRING_DEV'),database ='VR_Database')
    DBTaskScheduler=Database(URL = os.environ.get('DB_STRING_DEV'),database ='VR_Database')
    loggingLevel = logging.INFO

else:
    DB=Database()
    DBTaskScheduler=Database()
    bottoken = os.environ.get('BOT_KEY')
    bot = telebot.TeleBot(os.environ.get('BOT_KEY'))
    loggingLevel = logging.INFO

#starting mongoDB connection
#Logging setup
logging.basicConfig(handlers=[logging.StreamHandler()], encoding='utf-8', level=loggingLevel, format=' %(asctime)s - %(levelname)s - %(message)s')




DB.openConnection()
standardMessages = DB.getStandardMessages()
bot.db_connection = DB
bot.token=bottoken

bot.add_custom_filter(isAdminFilter(bot))


def registerHandlers():
    bot.register_message_handler(welcome_command_admin, commands=['start'], pass_bot=True, isAdmin=True)
    bot.register_message_handler(any_message_admin, func=lambda message: True, pass_bot='True', isAdmin=True)
    
    bot.register_message_handler(welcome_command_user, commands=['start'], pass_bot='True')
    bot.register_message_handler(any_message_user, func=lambda message: True, pass_bot='True')
    

    bot.register_callback_query_handler(welcome_admin_callback,func=lambda call: 'welcome_admin_CB' in call.data, pass_bot=True, isAdmin=True)
    bot.register_callback_query_handler(welcome_user_callback,func=lambda call: 'welcome_user_CB' in call.data, pass_bot=True)
    
    #bot.register_message_handler(all_messages_handler, func=lambda pollAnswer: True, pass_bot=True, isSubscribed=True)

registerHandlers()




# sendTaskThread = Thread(target=setAnotherThread, args = (DBTaskScheduler, bottoken))
# sendTaskThread.start()
        

while True:
    try:
        logging.info('Starting Bot Polling...')
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f'Bot restarted after the error. Error: {e}')
