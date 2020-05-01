# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 23:07:21 2020

@author: Timmitim (Tim Laeufer)
"""
import datetime

class counter:
    num_messages = 0
    num_commands = 0
    start_time = None

    def __init__(self, start_time):
        self.start_time = start_time
        num_messages = 0
        num_commands = 0

    def add_message(self, time):
        self.num_messages += 1
        if((self.num_messages % 50) == 0):
            running_for = str(datetime.datetime.now() - self.start_time)
            s = str(time) + "\t"
            s += str(self.num_messages) + " messages received, \t"
            s += str(self.num_commands) + " commands \t"
            s += str(self.num_commands/self.num_messages*100) + "% commands"
            s += '\n\t runtime: ' + running_for
            print(s)
    def add_command(self):
        self.num_commands += 1
    

    def get_stats(self):
        if(self.num_messages == 0):
            self.num_messages = 1
        running_for = str(datetime.datetime.now() - self.start_time)
        s = str(datetime.datetime.now()) + "\n"
        s += str(self.num_messages) + " messages received, \n"
        s += str(self.num_commands) + " commands \n"
        s += str(self.num_commands/self.num_messages*100) + "% commands \n"
        s += 'runtime: ' + str(running_for)
        return s
