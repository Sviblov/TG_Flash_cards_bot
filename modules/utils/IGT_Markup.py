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
    