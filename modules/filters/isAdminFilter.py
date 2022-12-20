from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import Message, CallbackQuery
import logging


class isAdminFilter(AdvancedCustomFilter):
    """
    Filter for admins users
    """
    def __init__(self, bot):
        self.bot = bot

    def isAdminUser(self, userId):
        adminList=[173409214]
        if userId in adminList:
            return True
        else:
            return False
        

    key = 'isAdmin'
    def check(self, message: Message, text):
      
        if isinstance(message, Message):
            user_id = message.from_user.id

        if isinstance(message, CallbackQuery):   
            user_id = message.from_user.id


        return self.isAdminUser(user_id)