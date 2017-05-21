import discord
import asyncio
import logging
import configparser
import os, sys
import random

import requests
from bs4 import BeautifulSoup

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Config file
settings = configparser.ConfigParser()
settings.read('config.ini')
token = settings.get('Connection', 'Token')

class AshurBot(discord.Client):

    # Set settings
    # There's probably a better way to do this that doesn't involve overwriting __init__
    ownerID = settings.get('Owner', 'ID')
    ownerName = settings.get('Owner', 'Name')
    prefix = settings.get('Options', 'Prefix')

    # various commands below that need docstrings...

    # gw2 related
    async def c_forgeprofit(self, message, params):
        r = requests.get("http://www.gw2shinies.com/alchemy.php?display=All&saviewcolumn=Buy&sellchoice=Sell&viewtype=All&includegifts=Yes")
        data = BeautifulSoup(r.text, "html.parser")
        
        #grab itemtable
        table = data.find("table", {"class": "itemsTable"})
        items = table.td
        print(items)
        
        #look for our item
        if params == "":
            await self.send_message(message.channel, "Please enter an item to search for.")
        elif params in items:
            await self.send_message(message.channel, "Found " + params + ".")
        else: 
            await self.send_message(message.channel, "Couldn't find " + params + ". Did you enter the exact name?")
        
        #spit out the information
     
    async def c_kinkshame(self, message, params):
        
        fname = random.choice(os.listdir(os.path.dirname(os.path.abspath(__file__)) + "\\kinkshame\\"))
        target = params.split(" ")[0]
        
        if params.split(" ")[0] == "me":
            msg = message.author.mention
        else: 
            msg = target
        
        await self.send_file(message.channel, os.path.dirname(os.path.abspath(__file__)) + "\\kinkshame\\" + fname, filename=fname, content=msg)
     
    # japanese dictionary
    async def c_jisho(self, message, params):
        if params == "":
            await self.send_message(message.channel, "Please enter an english word, kana, or kanji to search for.")
        else:
            r = requests.get("http://jisho.org/api/v1/search/words?keyword=" + params.split(" ")[0])
            data = r.json()
            entry = data["data"][0]
            
            msg = "```markdown\n"
            
            if "reading" in entry["japanese"][0]: 
                msg += "" + entry["japanese"][0]["reading"] + "\n"
            
            if "word" in entry["japanese"][0]: 
                msg += entry["japanese"][0]["word"] + "\n------\n" 
            
            msg += "\n"
            
            for index, sense in enumerate(entry["senses"]):
            
                if ("Wikipedia definition" in sense["parts_of_speech"]) & (index > 0):
                    break
                        
                else:
                    
                    if sense["parts_of_speech"]:
                        for item in sense["parts_of_speech"]:
                            if "Wikipedia" not in item:
                                msg += item + ". \n"
                                
                    msg += str(index + 1) + ". "
                    
                    for index, engdef in enumerate(sense["english_definitions"]):
                        if (index > 0):
                            msg += ", " + engdef
                        else: 
                            msg += engdef
                    
                    msg += ". "
                    
                    if sense["tags"]:
                        for tag in sense["tags"]:
                            msg += tag + ". "
                            
                    msg += "\n"
                
            msg += "```" + "\nhttp://jisho.org/search/" + params.split(" ")[0]
            
            await self.send_message(message.channel, msg)
        
    # basic commands
    async def c_hello(self, message, params):
        await self.send_message(message.channel, "Hello, " + message.author.name + ".")
        
    async def c_help(self, message, params):
        text = "Commands:\n```"

        for func in dir(self):
            if func.startswith('c_') and func != 'c_help':
                text += func.replace("c_", self.prefix) + "\n"
        
        text += "``` \nRepo: https://github.com/stokori/ashur-discord"
        
        await self.send_message(message.channel, text)
        
    async def c_restart(self, message, params):
        if (message.author.id == self.ownerID):
            await self.send_message(message.channel, "Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await self.send_message(message.channel, "Sorry, only my owner(" + ownerName + ") can do that. Please @ them if I need to be restarted.")
        
    async def c_exit(self, message, params):
        if (message.author.id == self.ownerID):
            await self.send_message(message.channel, "Later, nerds.")
            quit()
        else:
            await self.send_message(message.channel, "Sorry, only my owner(" + ownerName + ") can do that. Please @ them if I need to be exited.")
    
    # Overwriting event methods
    async def on_ready(self):
        print('Logged in successfully.')
        print(self.user.name)
        print(self.user.id)
        print('------')
    
    async def on_message(self, message):
        params = message.content.split(" ", 1)
        if len(params) > 1:
            params = params[1]
        else: 
            params = ""
        
        # Make this dynamic at some point
        if message.content.startswith(self.prefix + 'forgeprofit'):
            await self.c_forgeprofit(message, params)
        if message.content.startswith(self.prefix + 'jisho'):
            await self.c_jisho(message, params)
        if message.content.startswith(self.prefix + 'kinkshame'):
            await self.c_kinkshame(message, params)
        if message.content.startswith(self.prefix + 'hello'):
            await self.c_hello(message, params)
        if message.content.startswith(self.prefix + 'help'):
            await self.c_help(message, params)
        if message.content.startswith(self.prefix + 'exit'):
            await self.c_exit(message, params)
        if message.content.startswith(self.prefix + 'restart'):
            await self.c_restart(message, params)

if __name__ == "__main__":
    ashur = AshurBot()
    ashur.run(token)