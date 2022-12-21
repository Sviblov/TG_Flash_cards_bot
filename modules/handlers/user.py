from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from modules.utils.IGT_Mongo import Database
from modules.utils.IGT_Markup import IGT_Markup
from modules.utils.yandex_API import YandexAPI
import logging
from time import time
import json
import jsonpickle
from datetime import datetime, timedelta
import os




def any_message_user(message: Message, bot: TeleBot):

    
    DB: Database = bot.db_connection
    YandexAPI: YandexAPI = bot.yandexAPI
    
    userId=message.from_user.id
    userName=message.from_user.full_name
    
    sourceLangCode = YandexAPI.detectLanguage(message.text)
    voiceMessage=b''

    targetLangCode='other'

    if sourceLangCode=='ru':
        targetLangCode='en'
        sourceMessage='Русский'
        targetMessage='английский'
    elif sourceLangCode=='en':
        targetLangCode='ru'
        sourceMessage='Английский'
        targetMessage='русский'
        
    if targetLangCode=='other':
    #yandex defined the language as not english or russian
        replyText = DB.standardMessages['notRussianOrEnglish']
    else:
    #yandex defined the language as english or russian
        spellCheck=YandexAPI.spellCheck(message.text, sourceLangCode)

        if not spellCheck:
    #spelling is fine
            translation = YandexAPI.translate(message.text, targetLangCode)


# save flash card in db
            
            DB.putFlashCard(message.from_user.id,sourceLangCode, message.text.lower() , translation.lower())

            replyText=DB.standardMessages['translationTemplate'].format(sourceMessage,message.text, targetMessage, translation) 
            for audioContent in YandexAPI.voiceSynthesis(translation, targetLangCode):
                voiceMessage=voiceMessage + audioContent
        else:
    #spelling is wrong
             replyText=DB.standardMessages['typeError'] + ','.join(spellCheck[0]['s'])


    
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
    if voiceMessage:
        voiceMessage = bot.send_voice(message.chat.id, voiceMessage)
    
    logging.info(f"Sent message: username: {userName}, userId: {userId}, message: {replyText}")



def welcome_command_user(message: Message, bot: TeleBot):
   
    DB: Database = bot.db_connection
    DB.setUserToDefault(message.from_user)
    
    numberOfUserCards = DB.getNumberOfCards(message.from_user.id)
    replyText = DB.standardMessages['startNotAdmin'].format(numberOfUserCards)
    #replyMarkup = IGT_Markup.getWelcomeUserMarkup()
   
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")

def repeat_command_user(message: Message, bot: TeleBot):
    DB: Database = bot.db_connection

    DB.setRepeatMode(message.from_user.id)
    numberOfUserCards = DB.getNumberOfCards(message.from_user.id)
    replyText=DB.standardMessages['switchToRepeatMode'].format(numberOfUserCards)
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Move to repeat mode username: {message.from_user.first_name}, userId: {message.from_user.id}")

    sendNextCardToRepeat(message, bot)    

def status_command_user(message: Message, bot: TeleBot):

    DB: Database = bot.db_connection

    numberOfUserCards = DB.getNumberOfCards(message.from_user.id)

    if DB.isRepeatMode(message.from_user.id):
        replyText = DB.standardMessages['statusRepeatMode'].format(numberOfUserCards)
        
    else:
        replyText = DB.standardMessages['statusStudyMode'].format(numberOfUserCards)
        

    replyMarkup = IGT_Markup.getShowAllWords(message.from_user.id)

    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', reply_markup=replyMarkup, disable_web_page_preview=True)
    logging.info(f"Request for status: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")

def repeat_message_user(message: Message, bot: TeleBot):
    DB: Database = bot.db_connection

    cardToCompare = DB.getCardToCompare(message.from_user.id)
    logging.info(f'correctAnswer: {cardToCompare["english"]}')
    if message.text == cardToCompare['english']:
        replyText='правильно'
        DB.deleteCardFromQueue(message.from_user.id, cardToCompare['russian'], cardToCompare['english'])
    else:
        replyText='не правильно'

    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    sendNextCardToRepeat(message,bot)

def sendNextCardToRepeat(message: Message, bot:TeleBot):
    DB: Database = bot.db_connection

    nextCardToRepeat = DB.getNextCardToRepeat(message.from_user.id)
    if nextCardToRepeat:
        
        replyText=DB.standardMessages['askToTranslate'].format(nextCardToRepeat['russian'])
        DB.setCurrentCard(message.from_user.id, nextCardToRepeat)
        replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)

    else:
        replyText=DB.standardMessages['allMessagesLearned']
      
        replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
        DB.setUserToDefault(message.from_user)


def show_all_cards(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    allUserCards = DB.getAllUserCards(callBack.from_user.id)

    for card in allUserCards:
        replyText=DB.standardMessages['translationTemplate'].format('Русский', card['russian'],'Английский', card['english'])
        replyMessage = bot.send_message(callBack.message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    

    logging.info(f"Showing all words: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")
