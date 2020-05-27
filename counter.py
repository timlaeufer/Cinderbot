# -*- coding: utf-8 -*-
'''
Created on Tue Apr 28 23:07:21 2020

@author: Timmitim (Tim Laeufer)
'''
import datetime

class counter:
    num_messages = 0
    servs = {}
    num_commands = 0
    start_time = None

    def __init__(self, start_time):
        self.start_time = start_time
        num_messages = 0
        num_commands = 0

    def add_message(self, time, env_name = None, is_cmd = False):
        #dont add to msg if is_cmd, will get invoked twive by on_msg and on_cmd
        if(env_name):
            if(env_name in self.servs.keys()):
                if(is_cmd):
                    self.servs[env_name]['msg'] += 1
                    self.servs[env_name]['cmd'] += 1
                else:
                    self.servs[env_name]['msg'] += 1
                    self.servs[env_name]['cmd'] += 0
            else:
                if(is_cmd):
                    self.servs[env_name] = {}
                    self.servs[env_name]['msg'] = 0
                    self.servs[env_name]['cmd'] = 1
                else:
                    self.servs[env_name] = {}
                    self.servs[env_name]['msg'] = 1
                    self.servs[env_name]['cmd'] = 0
        if(is_cmd):
            self.num_commands += 1
        else:
            self.num_messages += 1
        
        #if((self.num_messages % 50) == 0):
        #    s = self.get_stats()
        #    print(s)
            


    def get_stats(self):
        if(self.num_messages == 0):
            self.num_messages = 1
        if(self.num_commands == 0):
            self.num_commands = 1
        running_for = str(datetime.datetime.now() - self.start_time)
        s = str(datetime.datetime.now()) + '\n'
        s += str(self.num_messages) + ' messages received, \n'
        s += str(self.num_commands) + ' commands \n'
        s += str(int((self.num_commands/self.num_messages*100)*100)/100) + '% commands \n'
        for el in self.servs.keys():
            num_msg = self.servs[el]['msg']
            num_cmd = self.servs[el]['cmd']
            perc_msg = num_msg/(self.num_messages+self.num_commands)*100
            perc_cmd = num_cmd/self.num_commands*100
            s += '<**' + el + '**> ' + str(num_msg) +' msg '
            s += str(int(perc_msg*100)/100) +'% ' + str(num_cmd) +' cmd '
            s += str(int(perc_cmd*100)/100) +'% \n'

        s += 'runtime: ' + str(running_for)
        return s
        pass
