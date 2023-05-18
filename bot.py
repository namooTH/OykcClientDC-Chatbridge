import discord
from discord.ext import commands
import logging
from discord import Webhook
import aiohttp
import asyncio

token = "<insert token here>"
url = "<insert webhook url here>"
endchannel = "<insert your channel u want bot to send here>"

notallowid = []


bot = commands.Bot(command_prefix='o!')
bot.remove_command('help') # // this line is important do not delete ///

logging.basicConfig(level=logging.DEBUG)

@bot.listen("on_message")
async def on_message(message: discord.Message):
    if message.channel.id == 930842597759541328:
      async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        msgurl = ""
        file = open("list.txt", "r")
        lines = file.readlines()
        allmessid = {}
        for i in lines:
            i = i.replace("\n", "")
            i = i.split("|")
            allmessid.update({i[0]: i[1]})
        if message.reference:
            if str(message.reference.resolved.id) in allmessid.values():
                for k,v in allmessid.items():
                    if v == str(message.reference.resolved.id):
                        attic = bot.get_channel(endchannel)
                        msg = await attic.fetch_message(int(k))
                        msgurl = msg.jump_url
        wh_mess = await webhook.send((f"[Replied to {message.reference.resolved.author}](<{msgurl}>)\n" if message.reference else "") # reply hyperlink
                                    + f"[Jump to message](<{message.jump_url}>)\n"
                                    + f"{message.content if message.content else ''}", # the message receives should have attachments of message.contnet is none
                                    #replaced id with storage system
                                    files=([await a.to_file() for a in message.attachments] if message.attachments else []), 
                                    avatar_url= message.author.avatar.url,username=str(message.author), allowed_mentions=discord.AllowedMentions.none(), wait=True)
        file = open("list.txt", 'a') #appeding the id to txt
        file.write(f"{wh_mess.id}|{message.id}\n")
        file.close()
 
    #reply system
    
    if message.channel.id == endchannel:   
        if message. reference:
            if message.reference.resolved.author.bot:
                file = open("list.txt", "r")
                lines = file.readlines()
                allmessid = {}
                for i in lines:
                    i = i.replace("\n", "")
                    i = i.split("|")
                    allmessid.update({i[0]: i[1]})
                if str(message.reference.resolved.id) in allmessid.keys():
                    onixgeneral = bot.get_channel(930842597759541328)
                    msg = await onixgeneral.fetch_message(int(allmessid[str(message.reference.resolved.id)]))
                    await msg.reply(message.content)

@bot.command()
async def send(ctx, *,arg):
    if ctx.channel.id == endchannel:
        if ctx.author.id not in notallowid:
            onixgeneral = bot.get_channel(930842597759541328)
            await onixgeneral.send(arg)
            notallowid.append(ctx.author.id)
            await asyncio.sleep(5)
            notallowid.remove(ctx.author.id)
        else:
            await ctx.message.add_reaction("❌")

bot.run(token)