from telebot import TeleBot
from telebot.types import Message, CallbackQuery, PollAnswer
from modules.utils.IGT_Mongo import Database, noRecommendationsForThisQuestionaire
from modules.utils.IGT_Markup import IGT_Markup
import logging
from time import time
import json
import jsonpickle
from datetime import datetime, timedelta
import os




def any_message_user(message: Message, bot: TeleBot):
    
    userId=message.from_user.id
    userName=message.from_user.full_name

    replyText = message.text + "\n\n You are NOT admin"
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
    logging.info(f"Echo message: username: {userName}, userId: {userId}, message: {message.text}")



def welcome_command_user(message: Message, bot: TeleBot):
   
    DB: Database = bot.db_connection
    DB.setUserToDefault(message.from_user)
    
    #DB.clearScheduledMessagesForUser(message.from_user)
    
   
    replyText = DB.standardMessages['startNotAdmin'].format(message.from_user.first_name)
    replyMarkup = IGT_Markup.getWelcomeUserMarkup()
   
    replyMessage = bot.send_message(message.chat.id, replyText,reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")



def welcome_user_callback(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    logging.info(f"Start message: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")
