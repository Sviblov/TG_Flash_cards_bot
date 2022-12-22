#in this module markup menus are defined for messages
import telebot
from telebot import types

class IGT_Markup(object):

#Markup for start message
    @staticmethod
    def getShowAllWords(userId):
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("Показать сохраненные слова", callback_data=f'show_all_cards_{userId}'))
        
        return markup
    
    @staticmethod
    def getStatusMarkup(userId):
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("Показать все слова", callback_data=f'show_all_cards_{userId}'))
        markup.row(telebot.types.InlineKeyboardButton("Показать все Ваши модули", callback_data=f'show_all_modules_{userId}'))
        markup.row(telebot.types.InlineKeyboardButton("Добавить новый модуль", callback_data=f'add_new_module_{userId}'))
        
        return markup

    @staticmethod
    def deleteModule(userId, moduleId, isGeneral):
        markup=telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("Показать все слова этого модуля", callback_data=f'show_all_module_cards_{userId}_{moduleId}'))
            
        if not isGeneral:
            markup.row(telebot.types.InlineKeyboardButton("Удалить модуль", callback_data=f'delete_module_{userId}_{moduleId}_{isGeneral}'))
            return markup
        else:
            markup.row(telebot.types.InlineKeyboardButton("Удалить все слова из модуля", callback_data=f'delete_module_{userId}_{moduleId}_{isGeneral}'))
            return markup

    @staticmethod
    def cardInfo(userId, cardId):
        markup=telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("Удалить слово", callback_data=f'delete_card_{userId}_{cardId}'))
        markup.row(telebot.types.InlineKeyboardButton("Перенести слово в другой модуль", callback_data=f'move_card_{userId}_{cardId}'))
        return markup

    @staticmethod
    def getModulesToRepeat(userModules):
        markup=telebot.types.InlineKeyboardMarkup()
        for module in userModules:
            moduleId=module['_id']
            moduleName=module['module_name']
            userId=module['userid']
            markup.row(telebot.types.InlineKeyboardButton(moduleName, callback_data=f'repeat_module_{userId}_{moduleId}'))
        
        return markup