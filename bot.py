# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:03:34 2020

@author: Timmitim (Tim Laeufer)
"""


import discord
from discord.ext import commands

description = '''Manages characters, rolls, and moves
for the Monstehearts 2 Discord Server of Timmitim#2579.'''
bot = commands.Bot(command_prefix='.', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.command()
async def testing(ctx):
    await ctx.send(ctx.message.author.name)
    

@bot.command()
async def opentext(ctx):
    if(ctx.message.author.name != "Timmitim"): return
    msg = ctx.message.content.split()[1]
    channels = ctx.message.content.split()
    del channels[0]
    del channels[1]
    serv = ctx.message.guild
    
    
    new_role = await serv.create_role(name = msg, mentionable = True)
    await ctx.send("Created the role " + new_role.mention)
    new_cat = await serv.create_category(name = msg)
    await ctx.send("Created the category... `" + msg + "`")
    for channel in channels:
        await serv.create_text_channel(name = channel, category = new_cat)
    await ctx.send("I created your " + len(channels) + " text channels!") 

    
    
    



def readToken():
    with open('token.txt') as f:
        token = f.readlines()[1]
    return token

bot.run(readToken())
