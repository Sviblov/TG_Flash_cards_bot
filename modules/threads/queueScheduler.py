import logging
from modules.utils.IGT_Mongo import Database, noMessagesToSend
import os
from datetime import datetime
import schedule
from modules.customAPI.custopAPI import sendCustomRequest
from time import sleep


def printSum(A, B):
    logging.info(f'Sum: {A}+{B}={A+B}')



def setAnotherThread(DB_connection, bottoken):
  
    if os.environ.get('DEBUG')=='1':
        schedule.every().minute.do(printSum, A=5, B=6)
        #logging
        pass
    else:
        schedule.every().minute.do(printSum, A=5, B=6)
    logging.info('Starting scheduler of message queue')
    while True:
        schedule.run_pending()
        sleep(60)
