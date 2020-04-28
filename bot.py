# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:03:34 2020

@author: Timmitim (Tim Laeufer)
"""


import discord
from discord.ext import tasks, commands
import configparser #reading bot.ini
import datetime #time and dates
import shutil #moving files easily
import requests #for fun moves
import json #reading moves.json
import string #string.letters and string.digits
import random #rolling
import inspect
import counter
from db_handler import *

#Bot initialisation:
description = '''Manages characters, rolls, and moves
for the Monstehearts 2 Discord Server of Timmitim#2579.'''
bot = commands.Bot(command_prefix='.', description=description)

#Read bot.ini
print('Loading bot.ini ....')
a = datetime.datetime.now()
config = configparser.ConfigParser()
config.read('bot.ini')
b = datetime.datetime.now()
print('bot.ini loaded! in ' + str((b-a).microseconds) + 'ms!')

#Convert config to simple dict for ease of use:
print('Converting bot.ini to dict .... ')
a = datetime.datetime.now()
strings = {}
for section in config.sections():
    for tup in config.items(section):
        strings.update({tup[0]: tup[1]})
b = datetime.datetime.now()
print('Done converting dot.ini in ' + str((b-a).microseconds) + 'ms!')

        
print('Loading moves.json ...')
a = datetime.datetime.now()
with open('moves.json', 'r') as f:
    dic = json.load(f)
b = datetime.datetime.now()
print('Loading moves.json done in ' + str((b-a).microseconds) + 'ms!')

a = datetime.datetime.now()

db_handler = db_handler()

flags = []
with open('flags.txt', 'r') as f:
    flags = f.readlines()

for i, f in enumerate(flags):
    flags[i] = ' ' + f.replace('\n', '').strip()

counter = counter.counter()


print('Initializing bot...')
"""
Layout of server message logging:
Time§~§Category§~§Channel§~§User§~§Length§~§Occurences
so as a tuple:
(time,cat,ch,author,length,occurences_array)
"""


#--------------Events ------------------

@bot.event
async def on_ready():
    """Lets Tim know the bot loaded properly"""
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    b = datetime.datetime.now()
    print('Bot is initialized after ' + str((b-a).microseconds) + 'ms!')
    #printstats.start()

@bot.command()
async def joined(ctx, member:discord.Member):
    """Triggered if someone joins the server"""
    if(member and ctx.guild.id == 679614550286663721):
        new_amount = len(ctx.guild.members)
        db_handler.log_join(member, new_amount)

@bot.listen()
async def on_message(message):
    """Triggered if a message is read by the bot"""
    log_msg(message)

    if(message.author is not message.guild.me):
        counter.add_message(message.created_at)


@bot.listen()
async def on_message_edit(before, after):
    """Triggered if a message is edited"""
    log_edit(before, after)

def log_edit(before, after):
    db_handler.log_edit(strings['relative_database_path'], before, after)

@bot.listen()
async def on_message_delete(message):
    """Triggered if a message is deleted"""
    log_delete(message)

def log_delete(message):
    db_handler.log_delete(strings['relative_database_path'], message)


def log_msg(message):
    #save message in database
            
    db_handler.log(strings['relative_database_path'], message)
    return



@bot.event
async def on_command(ctx):
    """Triggered if a command is called"""
    counter.add_command()
    try:
        s = strings['called'].format(
            category = ctx.channel.category,
            channel = ctx.channel,
            author = ctx.author,
            message = ctx.message.content,
            server = ctx.guild.name,
            time = time())
    except AttributeError:
        s = strings['called'].format(
            category = 'DM Channel',
            channel = ctx.channel,
            author = ctx.author,
            message = ctx.message.content,
            server = 'No server',
            time = time())
    #print(s)
    #await post_log(ctx, s)    
    
#-------------------Bot Commands ------------------------
@bot.command()
async def testing(ctx):
    """A small, mod-only testing command"""
    if(await check_mod(ctx)):
       await sendmsg(ctx, ctx.message.author.name)
    else:
        await sendmsg(ctx, '`You are not a moderator`')

@bot.command()
async def opengame(ctx):
    """A command for mods to easily open games on the server. .opengamehelp for more info!"""
    is_mod = await check_mod(ctx)
    author = ctx.author
    
    if(ctx.guild.id != 679614550286663721):#main server
        return
    
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
    """Confirms a game and opens it. .opengamehelp for more info!"""
    is_mod = await check_mod(ctx)
    author = ctx.author

    if(ctx.guild.id != 679614550286663721):#main server
        return
    

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
    bot_role = get_bot_role(ctx)
    mod_role = get_mod_role(ctx)
    mc_role = get_mc_role(ctx)
    player_role = get_player_role(ctx)
    everyone_role = get_everyone_role(ctx)
    
    if (game_type == 'private'):
        overwrites[new_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        overwrites[serv.me] = discord.PermissionOverwrite(
                send_messages = True, view_channel = True)

        #bots: send True, Speak True, View True
        if(bot_role):
            overwrites[bot_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        #mods: send True, Speak True, View True
        if(mod_role):
            overwrites[mod_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        #everyone: Send False, Speak False, View False
        if(everyone_role):
            overwrites[everyone:role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = False)
        #player: Send False, Speak False, View False
        if(player_role):
            overwrites[player_role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = False)
        #Player: Send False, Speak False, View False
        if(mc_role):
            overwrites[mc_role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = False)
    else:
        #public game
        overwrites[new_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        overwrites[serv.me] = discord.PermissionOverwrite(
                send_messages = True, view_channel = True)

        #bots: send True, Speak True, View True
        if(bot_role):
            overwrites[bot_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        #mods: send True, Speak True, View True
        if(mod_role):
            overwrites[mod_role] = discord.PermissionOverwrite(
                send_messages = True, speak = True, view_channel = True)
        #everyone: Send False, Speak False, View False
        if(everyone_role):
            overwrites[everyone_role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = False)
        #player: Send False, Speak False, View True
        if(player_role):
            overwrites[player_role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = True)
        #Player: Send False, Speak False, View True
        if(mc_role):
            overwrites[mc_role] = discord.PermissionOverwrite(
                send_messages = False, speak = False, view_channel = True)


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
                    overwrites ={player_role: discord.PermissionOverwrite(send_messages=True),
                                 mc_role: discord.PermissionOverwrite(send_messages=True)})
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
                , 'confirmed/' + game_name + time(True) +'_' + str(author) + '.txt')
    

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
async def skin(ctx):
    """Lists all moves a skin has. Alias for moves(ctx)"""
    await moves(ctx)

@bot.command()
async def moves(ctx):
    """Lists all moves of a certain skin"""
    author = ctx.author
    s = ''
    if(not await check_player(ctx)):
        await sendmsg(ctx, strings['move_only_players'])
        return

    first_space = ctx.message.content.find(' ')
    skin_name = ctx.message.content[first_space:].lower().strip()
    skins = []
    s = ''
    for src in dic:
        for skin in dic[src]:
            if(skin.lower() == skin_name):
                s += 'Skin: ' + skin + '\n'
                for move in dic[src][skin]:
                    s += '\t' + move
                    s += '\n'
                await sendmsg(ctx, s)
                return

    for src in dic:
        s += 'Source: ' + src + '\n'
        for skin in dic[src]:
            s += '\tSkin: ' + skin + '\n'

    ret =strings['skin_not_found'].format(searched = skin_name) + '\n' + s
            
    await sendmsg(ctx, ret)

@bot.command()
async def skins(ctx):
    """Lists all skins"""
    author = ctx.author
    s = ''
    if(not await check_player(ctx)):
        await sendmsg(ctx, strings['move_only_players'])
        return
    for src in dic:
        s += 'Source: ' + src + '\n'
        for skin in dic[src]:
            s += '\tSkin: ' + skin + '\n'
    await sendmsg(ctx, s)

@bot.command()
async def move(ctx):
    """Standard move command. .movehelp for more info!"""
    author = ctx.author
    s = ''
    if(not await check_player(ctx)):
        await sendmsg(ctx, strings['move_only_players'])
        return

    numeric = None

    

    message = ctx.message.content[6:] #removes '.move ' from the message
    
    """
    Check all chars if they're a numeric.
    If so, it takes the numeric and saves it
    """
    for i, char in enumerate(message):
        if char in string.digits:
            if('-' in message):
                numeric = - int(char)
            else:
                numeric = + int(char)
            break
        
    replace = string.punctuation + string.digits
    #No punctuation in the command, numeric is already checked.
    

    #delete all punctuation and digits, except whitespaces
    for element in replace:
        if(element != ' '):
            message = message.replace(element, '')

    #If remaining message is empty, roll 2d6, add, and return
    if(message == '' and numeric is None):
        dice = [0, 0]
        dice[0] = random.randint(1,6)
        dice[1] = random.randint(1,6)
        if(dice[0] == dice[1] == 6):
            lucky = True
        result = dice[0] + dice[1] + 0
        s = strings['move_general'].format(
            d1 = dice[0],
            d2 = dice[1],
            mod = 0,
            res = result)
        await sendmsg(ctx, s)
        return
    elif(message == ''):
        dice = [0, 0]
        dice[0] = random.randint(1,6)
        dice[1] = random.randint(1,6)
        if(dice[0] == dice[1] == 6):
            lucky = True
        result = dice[0] + dice[1] + numeric
        s = strings['move_general'].format(
            d1 = dice[0],
            d2 = dice[1],
            mod = numeric,
            res = result)
        await sendmsg(ctx, s)
        return

    #Split message
    args = message.split(' ')

    for i in range(len(args)):
        args[i] = args[i].lower()

    #Delete empty strings, in case the caller has written '.move    +'
    data  = [x for x in args if x != '']

    #get raw_string
    raw_string = ''
    for element in data:
        raw_string += element + ' '
        
    raw_string = raw_string[:-1]
    candidates = get_move(raw_string)
    if(len(candidates) == 1): #If match is found by whole phrase
        move = candidates[0]
    elif(len(candidates) > 1):#If multiple matches are found by whole phrase
        s = ''
        #"Found multiple matches" to s
        s += strings['multiple_moves_found'].format(
            raw = raw_string,
            comm = message) + '\n'
        for element in candidates:
            #Append every match to s
            temp = strings['multiple_moves_single'].format(
                move = str(element['name']),
                skin = get_skin_by_name(str(element['raw']), True),
                call = str(element['raw']).lower()) + '\n'
            if(len(s) + len(temp) > 2000):
                pass
            else:
                s += temp
        await sendmsg(ctx, s)
        return
    else: #If no match is found by whole phrase
        for arg in data:
            candidates += get_move(arg)
        if(len(candidates) == 1): #if 1 match is found by keywords
            move = candidates[0]
        elif(len(candidates) > 1): #if multiple matches are found by keywords
            candidates = remove_dupes(candidates)
            s = ''
            s += strings['multiple_moves_found'].format(
                raw = raw_string,
                comm = message) + '\n'
            for element in candidates:
                print("Element: " + str(element))
                temp = strings['multiple_moves_single'].format(
                    move = str(element['name']),
                    skin = str(get_skin_by_name(element['raw'], True)),
                    call = str(element['raw']).lower()) + '\n'
                if(len(s) + len(temp) >= 2000):
                    pass
                else:
                    s += temp
            await sendmsg(ctx, s)
            return
        else:
            await sendmsg(ctx, strings['move_not_found'].format(
                raw = raw_string,
                comm = ctx.message.content))
            return
        
    if(numeric is not None): #If there is a numeric in it
        #check if move is actually one to roll for
        print("has numeric!")
        if(is_roll_move(move)):
            await sendmsg(ctx, strings['move_rolled'].format(
                mention = ctx.author.mention,
                move = move['name']))
            dice = [0, 0]
            dice[0] = random.randint(1,6)
            dice[1] = random.randint(1,6)
            if(dice[0] == dice[1] == 6):
                lucky = True
            result = dice[0] + dice[1] + numeric


            if(result < 7):
                await sendmsg(ctx, strings['move_failed'].format(
                    d1 = dice[0],
                    d2 = dice[1],
                    mod = numeric,
                    res = result).replace('$', '\n'))
            elif(result < 10):
                await sendmsg(ctx, strings['move_roll'].format(
                    d1 = dice[0],
                    d2 = dice[1],
                    mod = numeric,
                    res = result,
                    event = move['complication']).replace('$', '\n'))
            else:
                await sendmsg(ctx, strings['move_roll'].format(
                    d1 = dice[0],
                    d2 = dice[1],
                    mod = numeric,
                    res = result,
                    event = move['success']).replace('$', '\n'))
            
        else:
            await sendmsg(ctx, get_move_overview(move))
        
    else: #If there is no numeric in the command
        await sendmsg(ctx, get_move_overview(move))

@bot.command()
async def movelist(ctx):
    """Gives Info over the Movelist"""
    s = ''
    for src in dic:
        s += 'Source: ' + src + '\n'
        for skin in dic[src]:
            s += '\tSkin: ' + skin + '\n'
            for move in dic[src][skin]:
                s += '\t\t' + move
                s += '\n'

    await sendmsg(ctx, s, pm_to_author = True)

@bot.command()
async def name(ctx):
    """Gives boy or girl names from drycodes.com. Alias for .names"""
    await names(ctx)

@bot.command()
async def names(ctx):
    """Gives boy or girl names. .names girl, or .names boy. From drycodes.com"""

    lis = []
    s = ''
    if('boy' in ctx.message.content):
        r = requests.get('http://names.drycodes.com/10?nameOptions=boy_names')
        lis += r.json()
        s = strings['names_boy']
    elif('girl' in ctx.message.content):
        r = requests.get('http://names.drycodes.com/10?nameOptions=girl_names')
        lis += r.json()
        s = strings['names_girl']
    else:
        r = requests.get('http://names.drycodes.com/5?nameOptions=boy_names')
        lis += r.json()
        r = requests.get('http://names.drycodes.com/5?nameOptions=girl_names')
        lis += r.json()
        s = strings['names_both']

    s += '\n'
    for el in lis:
        s += el.replace('_', ' ') + '\n'

    await sendmsg(ctx, s)
        

#Event Commands:
#NPCs                
@bot.command()
async def npc(ctx):
    """Draws a random NPC question"""
    with open('npcquestions.questions', 'r') as f:
        questions = f.readlines()

    s = ''
    msg = ctx.message.content[4:].strip()
    if(msg.isnumeric()):
        num = int(msg)
        if(num > len(questions)-1):
            num = len(questions)-1
    else:
        #parse keywords
        keywords = []
        if(' ' in msg): #if ' ' in msg: multiple keywords
            keywords = msg.split(' ')
        elif(msg == ''): #if msg empty
            num = random.randint(1, len(questions)-1)
        else: #single keyword
            if(msg.lower() == 'random'):
                num = random.randint(1, len(questions)-1)
            else:
                keywords.append(msg)

        indices = []
        for element in keywords:
            indices += [i for i in range(len(questions))
                              if element in questions[i].lower()]
        if(len(indices) > 1):
            #found multiple
            indices = list(set(indices)) #delete duplicates
            s += strings['multiple_questions_found_prompt']
            for i in range(len(indices)):
                if(i > 3):
                    s += strings['multiple_questions_many_more'].format(
                        amount = len(indices) - i)
                    break
                else:
                    s += strings['multiple_questions_found_single'].format(
                        num = indices[i]+1,
                        question = questions[indices[i]])
            await sendmsg(ctx, s)
            return
        elif(len(indices) == 0 and msg != ''):
            #found none
            s += strings['question_not_found'].format(
                terms = str(keywords))
            await sendmsg(ctx, s)
            return
        elif(len(indices) == 1 and msg != ''):
            #found single
            #+1 to fix index error
            num = indices[0]+1
        
    question = questions[num-1]
    await sendmsg(ctx, strings['send_question'].format(
        question = question,
        num = num))

@bot.command()
async def npcs(ctx):
    """sends all npc questions to the author in pms """
    if('list' in ctx.message.content):
        simple = True
    else:
        simple = False
    s = ''
    with open('npcquestions.questions', 'r') as f:
        questions = f.readlines()
    s += strings['questions_list_npc'] + '\n'
    for i, q in enumerate(questions):
        s += strings['questions_list_single'].format(
            num = i+1,
            question = q).replace('\n', '').strip() + '\n'
        """
        if(len(s) > 1500):
            await sendmsg(ctx, s, pm_to_author = True)
            s = ''
        """
    await sendmsg(ctx, s, pm_to_author = True)
        
@bot.command()
async def addnpc(ctx):
    """Adds a npc question"""

    if(not await on_main_server(ctx)):
        return

    is_mod = await check_mod(ctx)
    author = ctx.author

    if(not is_mod):
        await sendmsg(ctx, strings['only_mods_add_questions'].format(
            mention = author.mention))
        return
    
    with open('npcquestions.questions', 'r') as f:
        questions = f.readlines()
    num = len(questions) + 1
    questions.append('\n' + ctx.message.content[8:].strip())
    with open('npcquestions.questions', 'w+') as f:
        f.writelines(questions)

    await sendmsg(ctx, strings['added_question'].format(
        mention = ctx.author.mention,
        question = ctx.message.content[8:],
        num = num))

@bot.command()
async def delnpc(ctx):
    """Delete an npc-question"""

    if(not await on_main_server(ctx)):
        return

    is_mod = await check_mod(ctx)
    author = ctx.author
    

    if(not is_mod):
        await sendmsg(ctx, strings['only_mods_add_questions'].format(
            mention = author.mention))
        return

    with open('npcquestions.questions', 'r') as f:
        questions = f.readlines()

    s= ''

    msg = ctx.message.content[7:].strip()
    if(msg.isnumeric()):
        num = int(msg)
        if(num > len(questions)):
            s = strings['del_given_index_too_high'].format(
                num1 = num,
                max_num = len(questions))
        else:
            s = strings['del_question_deleted'].format(
                num = num,
                question = questions[num-1])
            del questions[num-1]
            with open('npcquestions.questions', 'w+') as f:
                f.writelines(questions)
    else:
        s = strings['del_argument_not_readable']

    await sendmsg(ctx, s)
    
#Locations:
@bot.command()
async def location(ctx):
    """Draws a random location question"""
    with open('locationquestions.questions', 'r') as f:
        questions= f.readlines()
    msg = ctx.message.content[4:].strip()
    if(msg.isnumeric()):
        num = int(msg)
        if(num > len(questions)-1):
            num = len(questions)-1
    else:
        num = random.randint(1, len(questions)-1)
    question = questions[num]
    await sendmsg(ctx, strings['send_location'].format(
        question = question,
        num = num))

@bot.command()
async def locations(ctx):
    """sends all location questions to the author in pms """
    if('list' in ctx.message.content):
        simple = True
    else:
        simple = False
    s = ''
    with open('locationquestions.questions', 'r') as f:
        questions = f.readlines()
    s += strings['questions_list_location']
    for i, q in enumerate(questions):
        s += strings['questions_list_single'].format(
            num = i+1,
            question = q).replace('\n', '').strip() + '\n'
        """
        if(len(s) > 1500):
            await sendmsg(ctx, s, pm_to_author = True)
            s = ''
        """

    await sendmsg(ctx, s, pm_to_author = True)
    
@bot.command()
async def addlocation(ctx):
    """Adds a question"""
    if(not await on_main_server(ctx)):
        return
    
    is_mod = await check_mod(ctx)
    author = ctx.author
    

    if(not is_mod):
        await sendmsg(ctx, strings['only_mods_add_questions'].format(
            mention = author.mention))
        return
    
    with open('locationquestions.questions', 'r') as f:
        questions = f.readlines()
    num = len(questions)+1
    questions.append('\n' + ctx.message.content[13:])
    with open('locationquestions.questions', 'w+') as f:
        f.writelines(questions)

    await sendmsg(ctx, strings['added_question'].format(
        mention = ctx.author.mention,
        question = ctx.message.content[13:],
        num = num))

@bot.command()
async def dellocation(ctx):
    """Delete an npc-question"""

    if(not await on_main_server(ctx)):
        return

    is_mod = await check_mod(ctx)
    author = ctx.author
    

    if(not is_mod):
        await sendmsg(ctx, strings['only_mods_add_questions'].format(
            mention = author.mention))
        return

    with open('locationquestions.questions', 'r') as f:
        questions = f.readlines()

    s= ''

    msg = ctx.message.content[12:].strip()
    if(msg.isnumeric()):
        num = int(msg)
        if(num > len(questions)-1):
            s = strings['del_given_index_too_high'].format(
                num1 = num,
                max_num = len(questions)-1)
        else:
            s = strings['del_question_deleted'].format(
                num = num,
                question = questions[num])
            del questions[num-1]
            with open('locationquestions.questions', 'w+') as f:
                f.writelines(questions)
    else:
        s = strings['del_argument_not_readable']

    await sendmsg(ctx, s)

#Fun Commands
@bot.command()
async def gib(ctx):
    """Gib fun please"""
    choices = []
    choices.append('Cat picture') #0
    choices.append('Cat fact') #1
    choices.append('Dog picture') #2
    choices.append('Dog fact')#3
    choices.append('Dad joke')#4

    choice = 0
    
    if(not await check_player(ctx)):
        await sendmsg(ctx, strings['fun_only_players'])
        return
    message = ctx.message.content
    if ('fun' in message):
        choice = random.choice(choices)
    elif('dad' in message):
        choice = choices[4]
    elif('catfact' in message):
        choice = choices[1]
    elif('catpic' in message):
        choice = choices[0]
    elif('cat' in message):
        choice = choices[random.randint(1,2)]
    elif('dogfact' in message):
        choice = choices[3]
    elif('dogpic' in message):
        choice = choices[2]
    elif('dog' in message):
        choice = choices[random.randint(2,3)]
    else:
        await sendmsg(ctx, strings['gib_what'])
        return

    await sendmsg(ctx, strings['gib'].format(
            mention = ctx.author.mention,
            thing = choice))
    
        
    if(choice == choices[0]):
        await catpic(ctx)
    if(choice == choices[1]):
        await catfact(ctx)
    if(choice == choices[2]):
        await dogpic(ctx)
    if(choice == choices[3]):
        await dogfact(ctx)
    if(choice == choices[4]):
        await dadjoke(ctx)

@bot.command()
async def hammer(ctx):
    await sendmsg(ctx, 'Can\'t touch this.')
    return
    msg = ctx.message.content[7:].strip()
    await sendmsg(ctx,(strings['banhammer'].format(
                      name = msg.replace('@',''))))
    
@bot.command()
async def dadjoke(ctx):
    headers = {'Accept':'text/plain'}
    r = requests.get('https://icanhazdadjoke.com/', headers = headers)
    await sendmsg(ctx, r.text)

@bot.command()
async def daddyjoke(ctx):
    await sendmsg(ctx, 'No. Try `.dadjoke`.')

@bot.command()
async def dad(ctx):
    await dadjoke(ctx)

@bot.command()
async def cat(ctx):
    await catpic(ctx)

@bot.command()
async def catpic(ctx):
    if(not await check_player(ctx)):
        sendmsg(ctx, strings['fun_only_players'])
        return
    r = requests.get('http://aws.random.cat/meow')
    j = r.json()
    await sendmsg(ctx, j['file'])

@bot.command()
async def catfact(ctx):
    if(not await check_player(ctx)):
        sendmsg(ctx, strings['fun_only_players'])
        return
    r = requests.get('https://cat-fact.herokuapp.com/facts/random')
    j = r.json()
    await sendmsg(ctx, j['text']) 

@bot.command()
async def dog(ctx):
    await dogpic(ctx)

@bot.command()
async def dogpic(ctx):
    """Sends a random dog pic."""
    if(not await check_player(ctx)):
        sendmsg(ctx, strings['fun_only_players'])
        return
    r = requests.get('https://dog.ceo/api/breeds/image/random')
    j = r.json()
    await sendmsg(ctx, j['message'])

@bot.command()
async def dogfact(ctx):
    """Sends a random dog fact."""
    if(not await check_player(ctx)):
        sendmsg(ctx, strings['fun_only_players'])
        return
    r = requests.get('http://dog-api.kinduff.com/api/facts?number=1')
    j = r.json()
    await sendmsg(ctx, j['facts'][0])

#on_command and help functions
@bot.command()
async def helpme(ctx):
    await sendmsg(ctx, strings['general_help'].format(
        me = ctx.guild.me.mention,
        tim = bot.get_user(314135917604503553), #ID for tim
        annie = bot.get_user(132240553013280768).name,
        ollie = bot.get_user(131352795444936704).name))

@bot.command()
async def opengamehelp(ctx):
    await sendmsg(ctx, strings['og_format'])

@bot.command()
async def movehelp(ctx):
    await sendmsg(ctx, strings['move_help'].format(
        me = ctx.guild.me.mention))


#-------------------Interaction with Server and Stats -----------------
async def sendmsg(ctx, msg, pm_to_author=False):
    if(len(msg)> 1500):
        #split into parts that are as long as they can be
        secs = []
        section = ''

        #all lines
        lines = [s for s in msg.split('\n')]
        cur_length = 0
        
        for line in lines:
            section += line + '\n'
            cur_length += len(line)
            if(cur_length >= 1500):
                secs.append(section)
                section = ''
                cur_length = 0
        secs.append(section)
    else:
        secs = [msg]
    msg = ''
    for msg in secs:
        if(pm_to_author):
            if(ctx.author.dm_channel == None):
                ch = await ctx.author.create_dm()
            else:
                ch = ctx.author.dm_channel
            await ch.send(msg)
            s = strings['sendmsg'].format(
                    category = 'Private Message',
                    channel = ch,
                    message = msg,
                    server = ctx.guild.name,
                    time = time()) + "\n\n"
        else:
            await ctx.send(msg)
            try:
                s = strings['sendmsg'].format(
                        category = ctx.channel.category,
                        channel = ctx.channel.mention,
                        message = msg,
                        server = ctx.guild.name,
                        time = time()) + '\n\n'
            except AttributeError:
                s = strings['sendmsg'].format(
                        category = 'DM Channel',
                        channel = ctx.channel,
                        message = msg,
                        server = 'No Server',
                        time = time()) + '\n\n'
                
        #print(s)
        #await post_log(ctx, s, pm_to_author)


async def post_log(ctx, msg, pm_to_author = False):
    """Posts a log to the MH2 log channel"""
    #Server ID: 679614550286663721
    #Log Channel ID: 693116058575306795
    serv = bot.get_guild(679614550286663721)
    log_ch = serv.get_channel(693116058575306795)

    ch = log_ch
    
    await ch.send(msg.replace('@', 'at'))
    

async def check_mod(ctx):
    """Checks if a user that sent a message has the role <Moderator>"""
    if('dmchannel' in ctx.channel.name.lower()):
        return True
    
    author = ctx.author
    roles = author.roles
    message = ctx.message.content
    mod_role = get_mod_role(ctx) #ID for mod = 679618112122912887
    
    is_mod = False
    if(mod_role in roles):
        is_mod = True
    else:
        is_mod = False

    s = strings['ismod'].format(author = author.name,
                                result = str(is_mod),
                                msg = message,
                                channel = ctx.channel,
                                category = ctx.channel.category,
                                server = ctx.guild.name + str(ctx.guild.id),
                                time = time()) + "\n"
    print(s)
    return is_mod

async def check_player(ctx):
    """Checks if a user that sent a message has the role <Player>"""
    author = ctx.author
    roles = author.roles
    message = ctx.message.content

    if (await check_mod(ctx)):
        #If the user is a mod, it overrides needing the player role
        return True

    is_player = False

    for role in roles:
        if ('player') in role.name.lower():
            is_player = True


    s = strings['isplayer'].format(author = author.name,
                                result = str(is_player),
                                msg = message,
                                channel = ctx.channel.mention,
                                category = ctx.channel.category,
                                server = ctx.guild.name + str(ctx.guild.id),
                                time = time()) + "\n"
    print(s)
    return is_player
    
def get_admin(ctx):
    return bot.get_user(314135917604503553)

def get_mod_role(ctx):
    for role in ctx.guild.roles:
        if ('moderator' in role.name.lower()):
            return role

def get_bot_role(ctx):
    for role in ctx.guild.roles:
        if (role.id == 679620725526888581):
            return role
    return None

def get_player_role(ctx):
    for role in ctx.guild.roles:
        if(role.id == 679618147384295444):
            return role
    return None

def get_mc_role(ctx):
    for role in ctx.guild.roles:
        if(role.id == 679618972441772053):
            return role
    return None

def get_support_role(ctx):
    for role in ctx.guild.roles:
        if(role.id == 704767301043355790):
            return role
    return None

def get_everyone_role(ctx):
    return ctx.guild.default_role

async def on_main_server(ctx):
    if(ctx.guild is None): #if ctx is DM Channel
        g_id = 679614550286663721
        ch_id = 679620045256523776
        inv = await bot.get_guild(g_id).get_channel(ch_id).create_invite(
            max_age = 36000)
        await sendmsg(ctx, strings['func_only_on_main_server'].format(
                invite = inv))
        return False
    
    if(ctx.guild.id != 679614550286663721): #if not on main server
        g_id = 679614550286663721
        ch_id = 679620045256523776
        inv = await bot.get_guild(g_id).get_channel(ch_id).create_invite(
            max_age = 36000)
        await sendmsg(ctx, strings['func_only_on_main_server'].format(
            invite = inv))
        return False
    return True

# ------------- Move helper commands ------------------------
def get_move_overview(move):
    s = ''
    s += strings['move_overview'].format(
        name = move['name'],
        desc = move['desc'].replace('$','\n')) + '\n'

    if(is_roll_move(move)):
        s += strings['rollable_overview_addition'].format(
            success = move['success'].replace('$','\n'),
            complication = move['complication'].replace('$','\n'))
    return s

def is_roll_move(move):
    if('success' in move): return True
    else: return False

#JSON commands:
def get_move(keyword_or_name):
    """Searches for a move with the given name as a list, may return multiple"""
    candidates = []

    #Search for move
    for src in dic:
        for skin in dic[src]:
            for move in dic[src][skin]:
                #If name matches Exactly, return move as array
                if(dic[src][skin][move]['raw'].lower() == keyword_or_name.lower()):
                    candidates = []
                    candidates.append(dic[src][skin][move])
                    return candidates
                #If name is substring of move, add to candidates
                elif(keyword_or_name.lower() in str(move).lower()):
                    candidates.append(dic[src][skin][move])
                elif(keyword_or_name in dic[src][skin][move]['keywords']):
                    candidates.append(dic[src][skin][move])

    #If has only 1 entry, return candidates. Else, return whole array
    if(len(candidates) == 1):
        return candidates
    else:
        return candidates

    return [None]

def get_skin_by_name(search_move, only_name = False):
    """Returns the skin dict when given a move name"""
    
    for src in dic:
        for skin in dic[src]:
            for move in dic[src][skin]:
                if (move == search_move):
                    if(only_name):
                        return skin
                    else:
                        return dic[src][skin]
    return None

def get_src(search_skin):
    """Returns the src dict when given a skin"""
    for src in dic:
        for skin in dic[src]:
            if dic[src][skin] == search_skin:
                return dic[src]


#Short commands
def read_token():
    with open('token.txt') as f:
        token = f.readlines()[1]
    return token

def remove_dupes(lis):
    new_list = []
    for i, element in enumerate(lis):
        if(element not in new_list):
            new_list.append(lis[i])
    return new_list

def get_occurence_list(message_content):
    """returns a list of tuples that show the symbol occurences"""
    #tup = (<digit>, <amount of occurences>)
    digs = string.digits + string.ascii_lowercase
    lis = []
    for element in digs:
        tup = (element, message_content.count(element))
        lis.append(tup)
    return lis
        
    

def time(simple=False):
    if(simple):
        return str(datetime.datetime.now().strftime('%d-%m-%Y--%H_%M_%S'))
    return str(datetime.datetime.now())

def is_mention(arg):
    if(arg[0] == '<' and arg[-1] == '>' and '@' in arg):
        return True
    else:
        return False
    


bot.run(read_token())
