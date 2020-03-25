# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:03:34 2020

@author: Timmitim (Tim Laeufer)
"""


import discord
from discord.ext import commands
import configparser
import datetime
import shutil

#Bot initialisation:
description = '''Manages characters, rolls, and moves
for the Monstehearts 2 Discord Server of Timmitim#2579.'''
bot = commands.Bot(command_prefix='.', description=description)

#Read bot.ini
config = configparser.ConfigParser()
config.read('bot.ini')

#Convert config to simple dict for ease of use:
strings = {}
for section in config.sections():
    for tup in config.items(section):
        strings.update({tup[0]: tup[1]})


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('I read the following bot.ini sections: \n')
    
    for section in config.sections():
        print(str(section))
    print('-----------------------')
    
@bot.command()
async def testing(ctx):
    if(await check_mod(ctx)):
       await sendmsg(ctx, ctx.message.author.name)
    else:
        await sendmsg(ctx, '`You are not a moderator`')

    me = ctx.guild.me
    everyone = get_everyone_role(ctx)
    bots = get_bot_role(ctx)
    mods = get_mod_role(ctx)

    print(str(me))
    print(str(everyone))
    print(str(bots))
    print(str(mods))
    


    
    
"""
@bot.command()
async def opentext(ctx):
    msg = ctx.message.content.split()[1]
    channels = ctx.message.content.split()
    del channels[0]
    del channels[1]
    serv = ctx.message.guild
    
    
    new_role = await serv.create_role(name = msg, mentionable = True)
    await ctx.send("Created the role " + new_role.mention + "`")
    new_cat = await serv.create_category(name = msg)
    await ctx.send("`Created the category... `" + msg + "`")
    for channel in channels:
        await serv.create_text_channel(name = channel, category = new_cat)
    await ctx.send("`I created your " + len(channels) + " text channels!`")
"""

@bot.command()
async def opengame(ctx):
    """A command for mods to easily open games on the server"""
    is_mod = await check_mod(ctx)
    author = ctx.author
    

    if(not is_mod):
        await sendmsg(ctx, strings['game_open_only_mods'])
        return

    channel_tuples = []
    #split message
    args = ctx.message.content.split()
    
    gametype = 0 #0 is for private, 1 is for public
    
    try:
        #check if the second position is 'private' or 'public'
        if(args[1] == 'private'):
            game_type = 'private'
        elif(args[1] == 'public'):
            game_type = 'public'
        elif(is_mention(args[1])):
             await sendmsg(ctx, strings['og_mention_instead_of_name'])
             return
        else:
            await sendmsg(ctx, strings['og_privpub_not_clear'].format(
                problem = args[1]))
            return

        #check if there is a name given at the third position
        if(args[2].startswith('<') and args[2][-1] == '>'):
            await sendmsg(ctx, strings['og_mention_instead_of_type'])
            return
        game_name = args[2]

        
    except IndexError:
        await sendmsg(ctx, strings['og_not_enough_args'])
        return
    
    
    del args[0] #command call
    del args[0] #gametype (priv/pub)
    del args[0] #gamename
    
    #get mentioned users for easy role assignment
    mentioned_users = ctx.message.mentions

    #read which args are channels to create
    channels = []
    for arg in args:
        if(not is_mention(arg)):
            channels.append(arg)

    if(len(channels) < 1):
        await sendmsg(ctx, strings['og_no_channels_given'])
        return

    #convert args to channel names with types
    tups = []
    for channel in channels:
        if(channel.startswith('v-')):
            tups.append((channel[2:], 'voice'))
        else:
            tups.append((channel, 'text'))

    #save in file, wait for confirmation
    with open('waiting_for_confirmation//' + game_name + '.txt', 'w+') as f:
        f.write(game_name + '\n')
        f.write(str(author) + '\n')
        f.write(game_type + '\n')
        for tup in tups:
            f.write(tup[0] + ":" + tup[1] + '\n')
        for user in mentioned_users:
            f.write(str(user.id) + ':member' + '\n')

    #Sum for user:
    s = ""
    s += strings['og_game_waiting_for_confirmation_1'].format(
        gamename = game_name,
        gametype = game_type)
    s += '\n' 

    for tup in tups:
        s += strings['summary_channel'].format(type = tup[1],
                                               channelname = tup[0])
        s += '\n'

    for user in mentioned_users:
        s += strings['summary_user'].format(playername = str(user))
        s += '\n'

    s += '\n ' + strings['og_game_waiting_for_confirmation_2'].format(
        gamename = game_name)
    await sendmsg(ctx, s)

@bot.command()
async def confirm(ctx):
    """Confirms a game and opens it"""
    is_mod = await check_mod(ctx)
    author = ctx.author
    

    if(not is_mod):
        await sendmsg(ctx, strings['game_confirm_only_mods'])
        return

    #split message
    args = ctx.message.content.split()
    serv = ctx.guild

    game_name = args[1]
    try:
        with open('waiting_for_confirmation/' + game_name + '.txt', 'r') as f:
            lines = f.readlines()
    except:
        print(strings['cant_open_file'].format(
            fname = 'waiting_for_confirmation/' + game_name + '.txt',
            owner = get_admin().mention
            ))
        await sendmsg(strings['cant_open_file'].format(
            fname = 'waiting_for_confirmation/' + game_name + '.txt',
            owner = get_admin().mention
            ))
        return

    """
    data[0]: Name of the Game, Role, and Category
    data[1]: Creator of Game
    data[2]: private/public

    rest is tuples:
    <name>:desc

    its either
    <name>:text
    <name>:voice

    or
    <number>:member
    L
    """
    
    data = lines[3:] #gets only the channels and members
    game_type = lines[2][:-1]
    channels = []
    member_ids = []
    members = []
    
    #parse members and channels
    #tuple: (name:type\n). the \n has to be considered
    for dat in data:
        temp = dat.split(':')
        if('member' in temp[1]):
            member_ids.append(int(temp[0]))
        else:
            channels.append((temp[0], temp[1][:-1]))

    #get members from server by ID
    if len(member_ids) > 0:
        for id in member_ids:
            mem = serv.get_member(id)
            members.append(mem)
            
    #create role
    new_role = await serv.create_role(
        name=game_name,
        colour = discord.Colour.gold())
    print(strings['role_created'].format(
        author = author,
        rolename = game_name,
        time = time()))
    

    
    #set new permissions in overwrite dict
    overwrites = {}
    if (game_type == 'private'):
        overwrites = {
            serv.me: discord.PermissionOverwrite(view_channel=True),
            get_mod_role(ctx): discord.PermissionOverwrite(view_channel=True),
            get_bot_role(ctx): discord.PermissionOverwrite(view_channel=True),
            new_role: discord.PermissionOverwrite(view_channel=True),
            get_everyone_role(ctx): discord.PermissionOverwrite(view_channel=False)
            }
        """
        Perms of private:

        Cinderbot: read True
        Mod: read True
        Bots: read True
        new_role: read True

        @everyone: read false 
        """
    else:
        overwrites = {
            serv.me: discord.PermissionOverwrite(send_messages=True),
            get_bot_role(ctx): discord.PermissionOverwrite(send_messages=True),
            get_everyone_role(ctx): discord.PermissionOverwrite(send_messages=False, speak=False),
            get_mod_role(ctx): discord.PermissionOverwrite(send_messages=True, speak=True),
            new_role: discord.PermissionOverwrite(send_messages=True, speak=True)
            }
        """
        Perms of Public:

        Cinderbot: send true
        Mod: Send true
        new_role: send true
        new_role: speak true

        @everyone: send false
        @everyone: speak false
        """

    #create new category with proper overwrites
    new_cat = await serv.create_category(game_name, overwrites = overwrites)
    print(strings['category_created'].format(
        author = author,
        category = game_name,
        time = time()))

    created_channels = []
    

    #create new channels
    for channel in channels:
        if(channel[1] == 'voice'): #if voice channel
            temp = await serv.create_voice_channel(channel[0], category = new_cat)
            created_channels.append(temp)
        elif(channel[1] == 'text'):#Text channel
            if('visitor' in channel[0]): #if 'visitor' in channel name
                temp = await serv.create_text_channel(
                    channel[0],
                    category = new_cat,
                    overwrites ={serv.default_role: discord.PermissionOverwrite(send_messages=True)})
            else:#regular text channel
                temp = await serv.create_text_channel(channel[0], category = new_cat)
            created_channels.append(temp)
            print(strings['channel_created'].format(
                author = author,
                channelname = channel[1],
                categoryname = game_name,
                time = time()))
            

    #assign roles
    if(len(members) > 0):
        for member in members:
            await member.add_roles(new_role, reason = author.name + ' told me to.')

    shutil.move('waiting_for_confirmation/' + game_name + '.txt'
                , 'confirmed/' + game_name + time(True) + +'_' + str(author) + '.txt')
    

    #Tell people what you did:
    s = strings['og_created_info'].format(
        auth_mention = author.mention,
        cat_name = new_cat.name
        )
    s += '\n'
    for channel in created_channels:
        s += strings['og_channel_created'].format(channelname = channel.mention)
        s += '\n'

    if(len(members) > 0):         
        s += strings['og_members_assigned_info'].format(role_mention = new_role.mention)
        s += '\n'
        for member in members:
                 s += member.mention + ' \n'

    await sendmsg(ctx, s)
        
        

@bot.command()
async def opengamehelp(ctx):
    await sendmsg(ctx, strings['og_format'])

@bot.event
async def on_command(ctx):
    print(strings['called'].format(
        category = ctx.channel.category,
        channel = ctx.channel,
        author = ctx.author,
        message = ctx.message.content,
        time = time()))
    


async def check_mod(ctx):
    """Checks if a user that sent a message has the role <Moderator>"""
    author = ctx.author
    roles = author.roles
    message = ctx.message.content
    mod_role = get_mod_role(ctx) #ID for mod = 679618112122912887
    
    is_mod = False
    if(mod_role in roles):
        is_mod = True
    else:
        is_mod = False

    print(strings['ismod'].format(author = author.name,
                                result = str(is_mod),
                                msg = message,
                                channel = ctx.channel,
                                category = ctx.channel.category,
                                time = time()) + "\n")
    return is_mod
    
   
def readToken():
    with open('token.txt') as f:
        token = f.readlines()[1]
    return token

def time(simple=False):
    if(simple):
        return str(datetime.datetime.now().strftime('%d-%m-%Y--%H_%M_%S'))
    return str(datetime.datetime.now())

def get_admin(ctx):
    return ctx.guild.owner

def get_mod_role(ctx):
    return ctx.guild.get_role(679618112122912887)

def get_bot_role(ctx):
    return ctx.guild.get_role(679620725526888581)

def get_everyone_role(ctx):
    return ctx.guild.get_role(679614550286663721)
    

def is_mention(arg):
    if(arg[0] == '<' and arg[-1] == '>' and '@' in arg):
        return True
    else:
        return False

async def sendmsg(ctx, msg):
    await ctx.send(msg)
    print(strings['sendmsg'].format(
        category = ctx.channel.category,
        channel = ctx.channel,
        message = msg,
        time = time()) + "\n\n")
    



bot.run(readToken())
