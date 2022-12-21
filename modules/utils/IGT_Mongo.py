#in this module connections to mondoDB is defined
import json


import pymongo
import jsonpickle
from telebot import types
import logging
import os
from datetime import datetime




class noMessagesToSend(Exception):
    def __str__(self):
        return 'fileTooBigError'


class noRecommendationsForThisQuestionaire(Exception):
    def __str__(self):
        return 'noRecommendationsForThisQuestionaire'

#Creating class for DB connection
class Database:
    
    standardMessages=[]
    

    def __init__(self, URL=os.environ.get('DB_STRING'), database='Database'):
        self.URL=URL
        self.databaseName=database
        

    def openConnection(self):
        self.client = pymongo.MongoClient(self.URL)
        database = self.client[self.databaseName]
        self.users= database['TG_Users']
        self.user_state= database['TG_User_State']
        self.standard_messages= database['TG_Standard_Messages']
        self.flash_cards=database['TG_Flash_Cards']
        self.cards_to_repeat=database['TG_Cards_To_Repeat']
        cursor = self.standard_messages.find()
        self.standardMessages = cursor[0]

        
    def closeConnection(self):
        self.client.close()

#check have this user used bot or not
    def isExistingUser(self, userId):
        
        filter_user = {'id': userId}
        if self.users.count_documents(filter_user)==0:   
            return False
        else:
            return True

    def getStandardMessages(self):
        cursor = self.standard_messages.find()
        return cursor[0]
    
    def getAllUserCards(self, userId):
        filter_user = {'userid': userId}
        
        if self.flash_cards.find(filter_user) is not None:
            return self.flash_cards.find(filter_user)
        else:   
            pass

    def putFlashCard(self, userId, sourceLangCode, sourceVersion, targetVersion):
        
        if sourceLangCode=='ru':
            flashCard={
                'userid': userId,
                'russian': sourceVersion,
                'english': targetVersion
            }
        else:
            flashCard={
                'userid': userId,
                'russian': targetVersion,
                'english': sourceVersion
            }

        filter=flashCard
        self.flash_cards.replace_one(filter, flashCard, upsert=True)

    def isRepeatMode(self, userId):
        filter_user = {'userid': userId}

        if self.user_state.find_one(filter_user) is not None:
            return self.user_state.find(filter_user)[0]['is_repeat_mode']
        else:   
            pass
    
    def setRepeatMode(self, userId):
        filter_user = {'userid': userId}

        allCards = self.getAllUserCards(userId)

        if self.user_state.find_one(filter_user) is not None:
            self.user_state.update_one(filter_user,{ "$set":{'is_repeat_mode': True}})    
        else:   
            pass

        for card in allCards:
            filter=card
            self.cards_to_repeat.replace_one(filter, card, upsert=True)
    
    def getNumberOfCards(self, userId):
        filter_user = {'userid': userId}
        return self.flash_cards.count_documents(filter_user)
    
    def getNextCardToRepeat(self, userId):

        filter_user = {'userid': userId}
        if self.cards_to_repeat.find_one(filter_user) is not None:
            return self.cards_to_repeat.find_one(filter_user)
        else:
            return False
    
    def getCardToCompare(self,userId):
        filter_user = {'userid': userId}
        if self.user_state.find_one(filter_user) is not None:
            
            return self.user_state.find_one(filter_user)['current_card'] 
        else:   
            pass

    def setCurrentCard(self, userId, card):
        filter_user = {'userid': userId}
        self.user_state.update_one(filter_user, { "$set":{'current_card': card}})
            
    def deleteCardFromQueue(self, userId, Russian, English):
        flashCard={
                'userid': userId,
                'russian': Russian,
                'english': English
            }
        self.cards_to_repeat.delete_many(flashCard)
    
#put User to default status
#We have tables TG_Users and TG_User_State - in default status it has False for search flag and -1 in account
    def setUserToDefault(self, user):
        
        filter_user = {'userid': user.id}
        user_json = json.loads(jsonpickle.encode(user))

        if self.isExistingUser(user.id):
            self.users.replace_one({'id': user.id}, user_json, upsert=True)
            self.user_state.update_one(filter_user, { "$set":{'is_repeat_mode': False}})
            self.user_state.update_one(filter_user, { "$set":{'current_card': []}})
            self.cards_to_repeat.delete_many(filter_user)

          

        else:
            logging.info(f'Creating new user in DB userid: {user.id}')
            self.users.insert_one(user_json)
            
            defaultUserInfo = { 
                'userid': user.id,
                'name': user.first_name,
                'is_repeat_mode': False,
                'current_card': []
            }

            self.user_state.insert_one(defaultUserInfo)


    
# # for testing
if __name__ == "__main__":



    DB =Database(URL = os.environ.get('TRANSLATION_DB_STRING_DEV'),database ='Memory_Cards_Database')
    DB.openConnection()
    
   #test your code

    DB.closeConnection()