#Telegram Bot

import logging
import os

import telebot

#importing handlers
from modules.handlers.user import welcome_command_user, any_message_user, welcome_user_callback

#DB connection and Markup setup

from modules.utils.IGT_Mongo import Database
from modules.utils.yandex_API import YandexAPI



# creating bot

if os.environ.get('DEBUG')=='1':

    bot = telebot.TeleBot(os.environ.get('Nikita_bot_key'))
    #bot = telebot.TeleBot(os.environ.get('BOT_KEY_DEV'))
    #DB_name = 'Memory_Cards_Database'
    DB=Database(URL = os.environ.get('TRANSLATION_DB_STRING_DEV'), database ='Memory_Cards_Database')
    loggingLevel = logging.INFO
    YandexAPI=YandexAPI()

else:
    DB=Database()
    bottoken = os.environ.get('BOT_KEY')
    bot = telebot.TeleBot(os.environ.get('BOT_KEY'))
    loggingLevel = logging.INFO
    YandexAPI=YandexAPI()

#starting mongoDB connection
#Logging setup
logging.basicConfig(handlers=[logging.StreamHandler()], encoding='utf-8', level=loggingLevel, format=' %(asctime)s - %(levelname)s - %(message)s')




DB.openConnection()
bot.db_connection = DB
bot.yandexAPI=YandexAPI


def registerHandlers():
     
    bot.register_message_handler(welcome_command_user, commands=['start'], pass_bot='True')
    bot.register_message_handler(welcome_command_user, commands=['repeat'], pass_bot='True')
    bot.register_message_handler(any_message_user, func=lambda message: True, pass_bot='True')
    

    #bot.register_callback_query_handler(welcome_user_callback,func=lambda call: 'welcome_user_CB' in call.data, pass_bot=True)
    
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
