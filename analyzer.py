# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 15:37:19 2020

@author: Timmitim (Tim Laeufer)
"""

import db_handler
import configparser #reading bot.ini
import datetime #time and dates
import string #string.letters and string.digits
import sqlite3

"""
This class analyzes the databases with all messages and prints a .pdf

TODO graphs:

    Activity by time (past day)
        x: Time of Day
        y: Amount of messages

    Activity by time (past 7-days)
        x: Time of Day
        y: Amount of messages

    Activity by time (past 14-days)
        x: Time of Day
        y: Amount of messages

    Activity by time (past 30-days)
        x: Time of Day
        y: Amount of messages

    Activity by time (past 60-days)
        x: Time of Day
        y: Amount of messages

    Activity by time (past 180-days)
        x: Time of Day
        y: Amount of messages

    Activity by time (past year)
        x: Time of Day
        y: Amount of messages

"""

class Analyzer:
    sqls = {}
    database = ''

    def __init__(self, ini, database):
        sqls = {}
        #Read bot.ini
        config = configparser.ConfigParser()
        config.read(ini)
        #Convert config to simple dict for ease of use:
        for section in config.sections():
            for tup in config.items(section):
                sqls.update({tup[0]: tup[1]})
        database = database
        

    def get_sql_res(self, sql):
        """Returns the results of the given sql as a list of sqlite3.Row s"""
        return db_handler.fetch_sql(database, sql)

    def get_ch_activity(self,
                        server_id,
                        channel_id,
                        pts_per_day = 24,
                        last_x_days = 7):
        """Returns a list of tuples (time, #msgs) of a certain channel"""
        


    def get_cat_activity(self,
                         server_id,
                         category_id,
                         pts_per_day = 96,
                         last_x_days = 7):
        pass
        #1: get all channels of that category
        #2: do get_ch_activity for all
        #3: add all

        
        

    def get_serv_activity(self,
                          server_id,
                          pts_per_day = 96,
                          last_x_days = 7):
        pass
        #1: get all categories
        #2: do get_cat_activity for all
        #3: add all up

        msgs = [] #object to fill the msgs tuples in
        for i, category_id in enumerate(category_ids):
            msgs[i][1] += get_cat_activity(
                                server_id,
                                category_id,
                                pts_per_day = pts_per_day,
                                last_x_days = last_x_days)

    def group_messages_by_time(self, rows, amount_of_groups)


db = input('What database (from /logs/...) would you like to analyze?')

if('.db' not in db):
    db = db + '.db'

ana = Analyzer('logs/sql_statements.ini', 'logs/' + db)
