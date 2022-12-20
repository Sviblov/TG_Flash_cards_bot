#in this module markup menus are defined for messages
import telebot
from telebot import types

class IGT_Markup(object):

#Markup for start message
    @staticmethod
    def getWelcomeAdminMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("welcome", callback_data='welcome_admin_CB'))
        
           
        return markup
    
    @staticmethod
    def getWelcomeUserMarkup():
        
        markup = telebot.types.InlineKeyboardMarkup()
 
        markup.row(telebot.types.InlineKeyboardButton("welcome", callback_data='welcome_user_CB'))
        
           
        return markup