import discord
from discord.ext import commands
import logging
from discord import Webhook
import aiohttp
import asyncio

token = "" # user token
url = "" # webhook url
endchannel = 0 # < insert channel id that u want the command to be execute
logchannel = 123 # < channel that you want to log

# do not mess with this
notallowid = []
lastperson = ""
allmessid = {}
# do not mess with this

bot = commands.Bot(command_prefix='o!')
bot.remove_command('help') # // this line is important do not delete //
logging.basicConfig(level=logging.DEBUG)

async def sendwebhook(content):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        await webhook.send(content=content)

async def refreshmesslist():
    global allmessid
    lines = open("list.txt", "r").readlines()
    for i in lines:
        i = i.replace("\n", "")
        i = i.split("|")
        allmessid.update({i[0]: i[1]})

async def savemesslist(start, end):
    file = open("list.txt", 'a') #appeding the id to txt
    file.write(f"{end}|{start}\n")
    file.close()

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.offline)
    #this is to cache the id list so it doesnt get load everytime
    await refreshmesslist()

@bot.listen("on_message")
async def on_message(message: discord.Message):
    global lastperson
    if message.channel.id == logchannel:
      async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        msgurl = ""
        if message.reference:
            if str(message.reference.resolved.id) in allmessid.values():
                for k,v in allmessid.items():
                    if v == str(message.reference.resolved.id):
                        attic = bot.get_channel(endchannel)
                        msg = await attic.fetch_message(int(k))
                        msgurl = msg.jump_url

        #// when the user dont have avatar it would just error so this is the fix
        try:
            avatar_url=(message.author.avatar.url if message.author.avatar else None)
        except:
            avatar_url=None
        #// when the user dont have avatar it would just error so this is the fix

        wh_mess = await webhook.send((f"[Replied to {message.reference.resolved.author}](<{msgurl}>)\n" if message.reference else "") # reply hyperlink
                                    + (f"[Jump to message](<{message.jump_url}>)\n" if lastperson != message.author else "")
                                    + (f"{message.content if message.content else ''}"), # the message receives should have attachments of message.contnet is none
                                    #replaced id with storage system
                                    files=([await a.to_file() for a in message.attachments] if message.attachments else []), 
                                    avatar_url=avatar_url,username=str(message.author), allowed_mentions=discord.AllowedMentions.none(), embed=(message.embeds[0] if message.embeds else None), wait=True)
        
        lastperson = message.author
        await savemesslist(start=message.id, end=wh_mess.id)
        await refreshmesslist()

    # sending system

    if message.channel.id == endchannel:
        if message.content.startswith("!") and len(message.content) > 1 or message.attachments and message.content.startswith("!"): # i love checking
            if not message.reference:
                if not message.author.bot and not message.author == bot.user:
                    try:
                        if message.author.id not in notallowid:
                            onixgeneral = bot.get_channel(logchannel)
                            await onixgeneral.send((message.content)[1:], files=([await a.to_file() for a in message.attachments] if message.attachments else [])) #stole rasp code ong
                            notallowid.append(message.author.id)
                            await asyncio.sleep(5)
                            notallowid.remove(message.author.id)
                        else:
                            await message.add_reaction("❌")
                    except Exception as e:
                      async with aiohttp.ClientSession() as session:
                        await message.add_reaction("❌")
                        await sendwebhook(content=f"```{e}```")

    # edit, delete, reply

    if message.channel.id == endchannel: 
        if message.reference:
            if message.reference.resolved.author.bot:
                if message.content[:5] == ".edit": # EDIT EDIT EDIT EDIT EDIT EDIT EDIT EDIT EDIT EDIT EDIT  
                    if len(message.content) > 6:
                        try:
                            if str(message.reference.resolved.id) in allmessid.keys():
                                onixgeneral = bot.get_channel(logchannel)
                                msg = await onixgeneral.fetch_message(int(allmessid[str(message.reference.resolved.id)]))
                                await msg.edit(message.content[6:])
                                return await message.add_reaction("✅")
                        except Exception as e:
                          async with aiohttp.ClientSession() as session:
                            await message.add_reaction("❌")
                            return await sendwebhook(content=f"```{e}```")

                if message.content[:6] == ".react": # REACT REACT REACT REACT REACT REACT REACT REACT REACT REACT REACT  
                    try:
                        if str(message.reference.resolved.id) in allmessid.keys():
                            onixgeneral = bot.get_channel(logchannel)
                            msg = await onixgeneral.fetch_message(int(allmessid[str(message.reference.resolved.id)]))
                            await msg.delete()
                            return await message.add_reaction("✅")
                    except Exception as e:
                      async with aiohttp.ClientSession() as session:
                        await message.add_reaction("❌")
                        return await sendwebhook(content=f"```{e}```")

                if message.content == ".del": # DEL DEL DEL DEL DEL DEL DEL DEL DEL DEL DEL DEL DEL DEL 
                    try:
                        if str(message.reference.resolved.id) in allmessid.keys():
                            onixgeneral = bot.get_channel(logchannel)
                            msg = await onixgeneral.fetch_message(int(allmessid[str(message.reference.resolved.id)]))
                            await msg.delete()
                            return await message.add_reaction("✅")
                    except Exception as e:
                      async with aiohttp.ClientSession() as session:
                        await message.add_reaction("❌")
                        return await sendwebhook(content=f"```{e}```")

                if message.content.startswith("!") and len(message.content) > 1:
                    if str(message.reference.resolved.id) in allmessid.keys(): # REPLY REPLY REPLY REPLY REPLY REPLY REPLY REPLY 
                        try:
                            onixgeneral = bot.get_channel(logchannel)
                            msg = await onixgeneral.fetch_message(int(allmessid[str(message.reference.resolved.id)]))
                            await msg.reply(message.content[1:])
                        except Exception as e:
                            async with aiohttp.ClientSession() as session:
                                await message.add_reaction("❌")
                                await sendwebhook(content=f"```{e}```")

#@bot.event
#async def on_raw_reaction_remove(payload):
    

    
@bot.event
async def on_reaction_remove(reaction, user):
    print("asdkasdkjasakldasjkdasjkdjlasdkjl")
    onixgeneral = bot.get_channel(logchannel)
    if reaction.message.channel.id != onixgeneral.id:
        return
    if str(reaction.message.id) in allmessid.values():
        for k,v in allmessid.items():
            if v == str(reaction.message.id):
                attic = bot.get_channel(endchannel)
                msg = await attic.fetch_message(int(k))
                msgurl = msg.jump_url
    async with aiohttp.ClientSession() as session:
        await sendwebhook(content=f"`{user} Removed reaction {reaction.emoji} to` [Jump to message](<{msgurl}>)")

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id != logchannel:
        return
    if str(reaction.message.id) in allmessid.values():
        for k,v in allmessid.items():
            if v == str(reaction.message.id):
                attic = bot.get_channel(endchannel)
                msg = await attic.fetch_message(int(k))
                msgurl = msg.jump_url
    async with aiohttp.ClientSession() as session:
        await sendwebhook(content=f"`{user} Reacted {reaction.emoji} to` [Jump to message](<{msgurl}>)")

@bot.event
async def on_message_delete(message):
    if message.channel.id != logchannel:
        return
    if str(message.id) in allmessid.values():
        for k,v in allmessid.items():
            if v == str(message.id):
                attic = bot.get_channel(endchannel)
                msg = await attic.fetch_message(int(k))
                msgurl = msg.jump_url
    async with aiohttp.ClientSession() as session:
        await sendwebhook(content=f"`{message.content[:15]}...` [Jump to original message](<{msgurl}>) Event: 🗑️Deleted")

@bot.event
async def on_message_edit(message_before, message):
    if message_before.content == message.content:
        return
    if message.channel.id != logchannel:
        return
    if str(message.id) in allmessid.values():
        for k,v in allmessid.items():
            if v == str(message.id):
                attic = bot.get_channel(endchannel)
                msg = await attic.fetch_message(int(k))
                msgurl = msg.jump_url
    async with aiohttp.ClientSession() as session:
        await sendwebhook(content=f"`{message.content}` [Jump to original message](<{msgurl}>) Event: ✂️Edited"

# todo
# make that u can replace channel id in 1 line
# fix reaction 

# done
# improved perfromace abit
# fixed some janky code

bot.run(token)
