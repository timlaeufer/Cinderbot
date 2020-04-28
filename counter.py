# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 23:07:21 2020

@author: Timmitim (Tim Laeufer)
"""

class counter:
    num_messages = 0
    num_commands = 0

    def __init__(self):
        num_messages = 0
        num_commands = 0

    def add_message(self, time):
        self.num_messages += 1
        if((self.num_messages % 50) == 0):
            s = str(time) + "\t"
            s += str(self.num_messages) + " messages received, \t"
            s += str(self.num_commands) + " commands \t"
            s += str(self.num_commands/self.num_messages*100) + "% commands"
            print(s)
    def add_command(self):
        self.num_commands = 0
    
