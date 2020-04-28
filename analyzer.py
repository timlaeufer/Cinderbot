# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 15:37:19 2020

@author: Timmitim (Tim Laeufer)
"""

import db_handler
import configparser #reading .ini
import datetime #time and dates
import string #string.letters and string.digits
import sqlite3
from os import listdir
from os.path import isfile, join, getsize
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

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
    handler = None

    def __init__(self, ini = "logs/sql_statements.ini", database = "messages"):
        #Read bot.ini
        config = configparser.ConfigParser()
        config.read(ini)
        #Convert config to simple dict for ease of use:
        for section in config.sections():
            for tup in config.items(section):
                self.sqls.update({tup[0]: tup[1]})
        self.database = database
        self.handler = db_handler.db_handler()

    def get_sql_res(self, sql):
        """Returns the results of the given sql as a list of sqlite3.Row s"""
        return self.handler.fetch_sql_rows(self.database, sql)

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
                          server_id = 679614550286663721,
                          time_step_in_min = 120,
                          last_x_days = 7,
                          days_ago = 0):
        """Returns a list of tuples with (time, count_msg) grouped my time_steps"""

        #get end point for given time interval
        td_days_ago = datetime.timedelta(days=days_ago)
        end = datetime.datetime.now() - td_days_ago
        end.replace(hour = 0,
                    minute = 0,
                    second = 0,
                    microsecond = 0)

        #get start point for given time interval
        td_last_x_days = datetime.timedelta(days = last_x_days)
        start = end - td_last_x_days
        
        query = self.sqls['get_serv_msg_by_range'].format(
            serv_id = server_id,
            end = self.get_time_as_db_string(end),
            start = self.get_time_as_db_string(start))
        rows = self.get_sql_res(query)
        tups = self.count_msg_per_time(rows, time_step_in_min = time_step_in_min)

        return tups

    def get_time_as_db_string(self, time_obj):
        """Returns a time obj as a >YYYY-MM-DD HH:MM:SS.mmmmmmUTC< format obj"""
        x = time_obj

        #year
        if(x.year):
            year = x.year
        else:
            year = datetime.datetime.now().year

        #month
        if(x.month):
            month = x.month
        else:
            month = datetime.datetime.now().month

        #day
        if(x.day):
            day = x.day
        else:
            day = datetime.datetime.now().day

        #time
        if(x.hour):
            hour = x.hour
        else:
            hour = 0
        if(x.minute):
            minute = x.minute
        else:
            minute = 0
        if(x.second):
            second = x.second
        else:
            second = 0
        if(x.microsecond):
            microsecond = x.microsecond
        else:
            microsecond = 0

        new_time = str(datetime.datetime(
            year = year,
            month = month,
            day = day,
            hour = hour,
            minute = minute,
            second = second,
            microsecond = microsecond)) + 'UTC'
        
        return new_time        

    def count_msg_per_time(self, rows, time_step_in_min = 30):
        """Counts how many msg per time_step_in_min step were are in the rows"""
        #returns tuple (time, msg_counted_from_last_time)
        
        lis = []
        tup = []

        start_time = rows[0]['time']
        end_time = rows[-1]['time']


        next_time = self.get_next_time(start_time, time_step_in_min, as_str = True)
        lis = [(start_time, 0)]
        tup = [next_time, 0]
        
        for i in range(len(rows)):
            #if rows[i]['time'] >= next time: append tup to lis, start new tup
            if(rows[i]['time'] >= next_time):
                tup = (next_time, tup[1])
                lis.append(tup)
                next_time = self.get_next_time(
                    next_time,
                    time_step_in_min,
                    as_str = True)
                tup = [next_time, 0]
            else:#if current row time < next_time, increment tup[1] by 1
                tup[1] = tup[1] + 1
        return lis

    def get_next_time(self, time_str, time_step_in_min, as_str = False):
        """Returns a time_str that is time_step_in_min minutes later in time"""

        td = datetime.timedelta(minutes = time_step_in_min)
        start_time = self.parse_time_from_string(time_str)
        new_time = start_time + td

        if(as_str):
            return self.get_time_as_db_string(new_time)
        else:
            return new_time
        

    def get_time(self, days_ago = 0, days_back = 7, date_x = None, as_string = False):
        """Get's the time x that's days_back days behind y, or returns date_x"""

        """
        date_x format:
        YYYY-MM-DD
        
        
                Time ->
        |x|              |y|            |now|
            <days_back>      <days_ago>
        """
        date_x = '2020-04-011'

        if(date_x == None):
            now = datetime.datetime.now().astimezone(datetime.timezone.utc)

            td_days_ago = datetime.timedelta(days=days_ago)
            td_days_back = datetime.timedelta(days=days_back)

            x = now - td_days_ago - td_days_back
            if(as_string):
                return str(x) + 'UTC'
            return x
        else:
            x = self.parse_time_from_string(date_x)
            if(as_string):
                return str(x) + 'UTC'
            return x
        
        

    def parse_time_from_string(self, s):
        """Returns UTC object from strings like: 2020-04-11 12:02:44.588500UTC"""
        if(s[-3:] == 'UTC'):
            s = s[:-3] #remove 'UTC'
        args = s.split(' ') #split date and time
        date_info = args[0].split('-')

        year = int(date_info[0])
        month = int(date_info[1])
        day = int(date_info[2])

        if(len(args)>1):
            time_info = args[1].split(':')
            hour = int(time_info[0])
            minute = int(time_info[1])

            sec_info = time_info[2].split('.')
            second = int(sec_info[0])
            microsecond = int(sec_info[1])

            time = datetime.datetime(
                year = year,
                month = month,
                day = day,
                hour = hour,
                minute = minute,
                second = second,
                microsecond = microsecond,
                tzinfo = datetime.timezone.utc)
        else:
            time = datetime.datetime(
                year = year,
                month = month,
                day = day,
                hour = 0,
                minute = 0,
                second = 0,
                microsecond = 0,
                tzinfo = datetime.timezone.utc)
        return time

    def plot_data(self, data, title = None, y_label = None, x_label = None):
        """Plots a list of (x,y) tuples)"""
        
        hours = mdates.HourLocator()
        hours_fmt = mdates.DateFormatter('%H')
        days = mdates.DayLocator()
        days_fmt = mdates.DateFormatter('%d')
        
        fig, ax = plt.subplots() #create the figure
        x_vals = [self.parse_time_from_string(i[0]) for i in data] #time values
        y_vals = [i[1] for i in data] #sum values

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        ax.grid(True)
        
        for tup in data:
            ax.plot(x_vals, y_vals)

        plt.show()

        

path = 'logs/'
dbs = [f for f in listdir(path) if isfile(join(path, f)) and
             '.db' in f]

print('There are the following databases:')
for el in dbs:
    print('\t' + str(el) + '\n\t\t(' + str(getsize(path+el)/10000000) + 'mb)')
db = input('What database (from ' + path + '...) would you like to analyze?')

if('.db' not in db):
    db = db + '.db'

ana = Analyzer(path + 'sql_statements.ini', path + db)

serv_id = 679614550286663721 #Lonesome Town = 695629497709494303

time_step = int(input("Which time step in minutes?"))
if(time_step < 15):
    time_step = 15

last_x_days = int(input("How many days from now?"))
if(last_x_days < 1):
    last_x_days = 1

tups = ana.get_serv_activity(time_step_in_min = time_step, last_x_days = 7, server_id = serv_id)
ana.plot_data(tups, x_label = 'time in UTC',
              y_label = 'amount of messages per ' + str(time_step) + ' min',
              title = 'Messages the last ' + str(last_x_days) + ' days, server_id = ' + str(serv_id))
