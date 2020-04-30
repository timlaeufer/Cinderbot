from discord.ext import commands

class Fun_commands(commands.Cog):
    """Fun commands via APIs"""
    """TODO: REWRITE NON-BLOCKING!"""
    def __init__(self, bot):
        self.bot = bot
        print("fun_commands Cog loaded!")

    @commands.command()
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

    @commands.command()
    async def hammer(ctx):
        await sendmsg(ctx, 'Can\'t touch this.')
        return
        msg = ctx.message.content[7:].strip()
        await sendmsg(ctx,(strings['banhammer'].format(
                          name = msg.replace('@',''))))
    @commands.command()
    async def dadjoke(ctx):
        headers = {'Accept':'text/plain'}
        r = requests.get('https://icanhazdadjoke.com/', headers = headers)
        await sendmsg(ctx, r.text)

    @commands.command()
    async def daddyjoke(ctx):
        await sendmsg(ctx, 'No. Try `.dadjoke`.')

    @commands.command()
    async def dad(ctx):
        await dadjoke(ctx)

    @commands.command()
    async def cat(ctx):
        await catpic(ctx)

    @commands.command()
    async def catpic(ctx):
        if(not await check_player(ctx)):
            sendmsg(ctx, strings['fun_only_players'])
            return
        r = requests.get('http://aws.random.cat/meow')
        j = r.json()
        await sendmsg(ctx, j['file'])

    @commands.command()
    async def catfact(ctx):
        if(not await check_player(ctx)):
            sendmsg(ctx, strings['fun_only_players'])
            return
        r = requests.get('https://cat-fact.herokuapp.com/facts/random')
        j = r.json()
        await sendmsg(ctx, j['text'])

    @commands.command()
    async def dog(ctx):
        await dogpic(ctx)

    @commands.command()
    async def dogpic(ctx):
        """Sends a random dog pic."""
        if(not await check_player(ctx)):
            sendmsg(ctx, strings['fun_only_players'])
            return
        r = requests.get('https://dog.ceo/api/breeds/image/random')
        j = r.json()
        await sendmsg(ctx, j['message'])

    @commands.command()
    async def dogfact(ctx):
        """Sends a random dog fact."""
        if(not await check_player(ctx)):
            sendmsg(ctx, strings['fun_only_players'])
            return
        r = requests.get('http://dog-api.kinduff.com/api/facts?number=1')
        j = r.json()
        await sendmsg(ctx, j['facts'][0])
