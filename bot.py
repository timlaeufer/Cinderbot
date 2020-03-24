# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:03:34 2020

@author: Timmitim (Tim Laeufer)
"""


import discord
from discord.ext import commands

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='.', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def readToken():
    with open('token.txt') as f:
        token = f.readlines()[1]
    return token
        


await bot.run(readToken())