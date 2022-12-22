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

            replyText=DB.standardMessages['translationTemplate'].format(sourceMessage,message.text, targetMessage, translation, 'General') 
            
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
    
    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Start message: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")

def repeat_command_user(message: Message, bot: TeleBot):
    DB: Database = bot.db_connection

    DB.setRepeatMode(message.from_user.id)
    
    userModules=DB.getUserModules(message.from_user.id)

    replyText=DB.standardMessages['switchToRepeatMode']
    replyMarkup=IGT_Markup.getModulesToRepeat(userModules)

    replyMessage = bot.send_message(message.chat.id, replyText, reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    logging.info(f"Move to repeat mode username: {message.from_user.first_name}, userId: {message.from_user.id}")

      

def repeat_module_selected(callBack: CallbackQuery, bot: TeleBot):
    
    DB: Database = bot.db_connection
    
    userId=callBack.data.split('_')[2]
    moduleId=callBack.data.split('_')[3]

    allModuleCards = DB.getAllUserModuleCards(callBack.from_user.id, moduleId)

    for card in allModuleCards:
        
        DB.putCardToRepeat(card)

    sendNextCardToRepeat(callBack.from_user, callBack.message.chat.id , bot)  

def status_command_user(message: Message, bot: TeleBot):

    DB: Database = bot.db_connection

    numberOfUserCards = DB.getNumberOfCards(message.from_user.id)
    numberOfModules = DB.getNumberOfModules(message.from_user.id)
    if DB.isRepeatMode(message.from_user.id):
        replyText = DB.standardMessages['statusRepeatMode'].format(numberOfUserCards, numberOfModules)
    else:
        replyText = DB.standardMessages['statusStudyMode'].format(numberOfUserCards, numberOfModules)
        

    replyMarkup = IGT_Markup.getStatusMarkup(message.from_user.id)

    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', reply_markup=replyMarkup, disable_web_page_preview=True)
    logging.info(f"Request for status: username: {message.from_user.first_name}, userId: {message.from_user.id}, message: {message.text}")

def repeat_message_user(message: Message, bot: TeleBot):
    DB: Database = bot.db_connection

    cardToCompare = DB.getCardToCompare(message.from_user.id)
    #logging.info(f'correctAnswer: {cardToCompare["english"]}')
    if message.text.lower() == cardToCompare['english']:
        replyText=DB.standardMessages['correctAnswer']
        DB.deleteCardFromQueue(message.from_user.id, cardToCompare['russian'], cardToCompare['english'])
    else:
        replyText=DB.standardMessages['wrongAnswer']

    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    sendNextCardToRepeat(message.from_user, message.chat.id,  bot)


def set_new_module_name(message: Message, bot: TeleBot):
    DB: Database = bot.db_connection

#TODO: check that module name is fine
    DB.createNewModule(message.from_user.id, message.text)

    replyText=DB.standardMessages['newModuleCreated'].format(message.text)

    replyMessage = bot.send_message(message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    DB.setUserToDefault(message.from_user)


def sendNextCardToRepeat(user, chatId, bot:TeleBot):
    DB: Database = bot.db_connection

    nextCardToRepeat = DB.getNextCardToRepeat(user.id)
    if nextCardToRepeat:
        
        replyText=DB.standardMessages['askToTranslate'].format(nextCardToRepeat['russian'])
        DB.setCurrentCard(user.id, nextCardToRepeat)
        replyMessage = bot.send_message(chatId, replyText, parse_mode='html', disable_web_page_preview=True)

    else:
        replyText=DB.standardMessages['allMessagesLearned']
      
        replyMessage = bot.send_message(chatId, replyText, parse_mode='html', disable_web_page_preview=True)
        DB.setUserToDefault(user)


def show_all_modules(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    allUserModules = DB.getAllUserModules(callBack.from_user.id)

    for module in allUserModules:
        
        moduleName = module['module_name']
        moduleId=module['_id']
        numberOfCardsInModule = DB.getNumberOfCardsInModule(callBack.from_user.id, moduleId)

        isGeneral=False
        if moduleName=='General':
            isGeneral=True

        replyText=DB.standardMessages['moduleInfo'].format(moduleName, numberOfCardsInModule)
        replyMarkup=IGT_Markup.deleteModule(callBack.from_user.id, moduleId, isGeneral)
        replyMessage = bot.send_message(callBack.message.chat.id, replyText, reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    

    logging.info(f"Showing all words: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")


def show_all_module_cards(callBack: CallbackQuery, bot: TeleBot):
    DB: Database = bot.db_connection

    moduleId=callBack.data.split('_')[5]

    moduleCards = DB.getAllUserModuleCards(callBack.from_user.id, moduleId)

    for card in moduleCards:
        cardModule = card['moduleId']
        moduleName = DB.getModuleNameById(cardModule)
   
        
        replyText=DB.standardMessages['cardInfo'].format('Русский', card['russian'],'Английский', card['english'],moduleName )
        replyMarkup=IGT_Markup.cardInfo(card['userid'], card['_id'])
        replyMessage = bot.send_message(callBack.message.chat.id, replyText, reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    


def show_all_cards(callBack: CallbackQuery, bot: TeleBot):
   
    DB: Database = bot.db_connection
    allUserCards = DB.getAllUserCards(callBack.from_user.id)

    for card in allUserCards:
        cardModule = card['moduleId']
        moduleName = DB.getModuleNameById(cardModule)
   
        
        replyText=DB.standardMessages['cardInfo'].format('Русский', card['russian'],'Английский', card['english'],moduleName )
        replyMarkup=IGT_Markup.cardInfo(card['userid'], card['_id'])
        replyMessage = bot.send_message(callBack.message.chat.id, replyText, reply_markup=replyMarkup, parse_mode='html', disable_web_page_preview=True)
    

    logging.info(f"Showing all words: username: {callBack.from_user.first_name}, userId: {callBack.from_user.id}, message: {callBack.data}")



def delete_card(callBack: CallbackQuery, bot: TeleBot):

    DB: Database = bot.db_connection
    DB.deleteCard(callBack.data.split('_')[3])
    replyText=DB.standardMessages['cardDeleteConfirmation']
    replyMessage = bot.send_message(callBack.message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)


def delete_module(callBack: CallbackQuery, bot: TeleBot):

    DB: Database = bot.db_connection
    DB.deleteModule( callBack.data.split('_')[3],callBack.data.split('_')[4])
    
    replyText=DB.standardMessages['moduleDeleteConfirmation']
    replyMessage = bot.send_message(callBack.message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
def add_new_module(callBack: CallbackQuery, bot: TeleBot):

    DB: Database = bot.db_connection

    replyText=DB.standardMessages['requestNewModuleName']
    DB.setModuleNameRequestMode(callBack.from_user.id)

    replyMessage = bot.send_message(callBack.message.chat.id, replyText, parse_mode='html', disable_web_page_preview=True)
    
    logging.info(f'User requested to add new module: userId: {callBack.from_user.id}')