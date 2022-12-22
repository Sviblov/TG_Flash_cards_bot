#Telegram Bot

import logging
import os

import telebot

#importing handlers
from modules.handlers.user import welcome_command_user, any_message_user, show_all_module_cards,set_new_module_name, add_new_module,delete_card, delete_module,show_all_modules ,repeat_module_selected, repeat_command_user,repeat_message_user, status_command_user,show_all_cards

#DB connection and Markup setup

from modules.utils.IGT_Mongo import Database
from modules.utils.yandex_API import YandexAPI

from modules.filters.userModeFilter import isRepeatModeFilter, isRequestNewModuleNameMode


# creating bot

if os.environ.get('DEBUG')=='1':

    #bot = telebot.TeleBot(os.environ.get('Nikita_bot_key'))
    bot = telebot.TeleBot(os.environ.get('BOT_KEY_DEV'))
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
    bot.register_message_handler(repeat_command_user, commands=['repeat'], pass_bot='True')
    bot.register_message_handler(status_command_user, commands=['status'], pass_bot='True')
    
    bot.register_message_handler(repeat_message_user, func=lambda message: True, pass_bot='True', isRepeatModeUser='True')
    bot.register_message_handler(set_new_module_name, func=lambda message: True, pass_bot='True', isRequestNewModuleNameMode='True')
    
    bot.register_message_handler(any_message_user, func=lambda message: True, pass_bot='True')
    
    bot.register_callback_query_handler(show_all_cards,func=lambda call: 'show_all_cards_' in call.data, pass_bot='True')
    bot.register_callback_query_handler(show_all_modules,func=lambda call: 'show_all_modules_' in call.data, pass_bot='True')
    
    bot.register_callback_query_handler(add_new_module,func=lambda call: 'add_new_module_' in call.data, pass_bot='True')
    bot.register_callback_query_handler(show_all_module_cards,func=lambda call: 'show_all_module_cards_' in call.data, pass_bot='True')
   

    bot.register_callback_query_handler(delete_card,func=lambda call: 'delete_card_' in call.data, pass_bot='True')
    bot.register_callback_query_handler(delete_module,func=lambda call: 'delete_module_' in call.data, pass_bot='True')
    
    bot.register_callback_query_handler(repeat_module_selected,func=lambda call: 'repeat_module_' in call.data, pass_bot='True')
   
registerHandlers()



bot.add_custom_filter(isRepeatModeFilter(bot))
bot.add_custom_filter(isRequestNewModuleNameMode(bot))
        

while True:
    try:
        logging.info('Starting Bot Polling...')
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f'Bot restarted after the error. Error: {e}')
