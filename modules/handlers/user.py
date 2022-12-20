from telebot import TeleBot
from telebot.types import Message, CallbackQuery, PollAnswer
from modules.utils.IGT_Mongo import Database, noRecommendationsForThisQuestionaire
from modules.utils.IGT_Markup import IGT_Markup
from modules.utils.yandex_API import YandexAPI
import logging
from time import time
import json
import jsonpickle
from datetime import datetime, timedelta
import os




def any_message_user(message: Message, bot: TeleBot):

    YandexAPI: YandexAPI = bot.yandexAPI
    DB: Database = bot.db_connection

    userId=message.from_user.id
    userName=message.from_user.full_name
    
    langCode = YandexAPI.detectLanguage(message.text)
    voiceMessage=b''

    
    if langCode=='ru':
        spellCheck=YandexAPI.spellCheck(message.text, 'ru')
        if not spellCheck:
        
            translation = YandexAPI.translate(message.text, 'en')
            replyText=DB.standardMessages['translationTemplate'].format('Русский',message.text, 'английской', translation) 
          
            for audioContent in YandexAPI.voiceSynthesis(translation,'en-US'):
                voiceMessage=voiceMessage + audioContent
        else:

            replyText=DB.standardMessages['typeError'] + ','.join(spellCheck[0]['s'])


    elif langCode=='en':
        spellCheck=YandexAPI.spellCheck(message.text, 'en')
        if not spellCheck:
            YandexAPI.spellCheck(message.text, 'en')
            translation = YandexAPI.translate(message.text, 'ru')
            replyText=DB.standardMessages['translationTemplate'].format('Английский',message.text, 'русский', translation)
            
            for audioContent in YandexAPI.voiceSynthesis(translation,'en-US'):
                voiceMessage=voiceMessage + audioContent
        else:
            replyText=DB.standardMessages['typeError'] + ','.join(spellCheck[0]['s'])

    else: 
        replyText = DB.standardMessages['notRussianOrEnglish']
    
    
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
    if voiceMessage:
        voiceMessage = bot.send_voice(message.chat.id, voiceMessage)
    
    logging.info(f"Sent message: username: {userName}, userId: {userId}, message: {replyText}")



def welcome_command_user(message: Message, bot: TeleBot):
   
    DB: Database = bot.db_connection
    DB.setUserToDefault(message.from_user)
    
   
    replyText = DB.standardMessages['startNotAdmin'].format(message.from_user.first_name)
    #replyMarkup = IGT_Markup.getWelcomeUserMarkup()
   
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")



def welcome_user_callback(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    logging.info(f"Start message: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")
