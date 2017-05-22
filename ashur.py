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
    commands = []

    # various commands below that need docstrings...
    
    # Overwriting event methods
    async def on_ready(self):
        print('Logged in successfully.')
        print(self.user.name)
        print(self.user.id)
        
        for func in dir(self):
            if func.startswith('c_'):
                self.commands.append(func.replace("c_", ""))
        
        print("Loaded commands: " + str(self.commands))
        print('------')
    
    async def on_message(self, message):
        params = message.content.split(" ", 1)
        command = message.content.split(" ", 1)[0].strip(self.prefix)
        if len(params) > 1:
            params = params[1]
        else: 
            params = ""
            
        if (message.content.startswith(self.prefix)) & (command in self.commands):
            functionName = "c_" + command
            commandCalled = getattr(self, functionName)
            await commandCalled(message, params)

    async def c_norn(self, message, params):
    
        name1 = ["Crunch", "Olaf", "Beef", "Chunk", "Smoke", "Brick", "Crash", "Thick", "Bold", "Buff", "Drunk", "Punch", "Crud", "Grizzle", "Slab", "Hack", "Big"]
        name2 = ["Mac", "Mc", ""]
        name3 = ["Butt", "Steak", "Hard", "Rock", "Large", "Huge", "Beef", "Thrust", "Big", "Bigger", "Meat", "Hard", "Fight", "Fizzle", "Run", "Fast", "Drink", "Lots",        "Slam", "Chest", "Groin", "Bone", "Meal", "Thorn", "Body", "Squat"]
        
        await self.send_message(message.channel, random.choice(name1) + " " + random.choice(name2) + random.choice(name3) + str.lower(random.choice(name3)))
            
    async def c_gw2daily(self, message, params):
        if "tomorrow" in params:
            r = requests.get("https://api.guildwars2.com/v2/achievements/daily/tomorrow")
        elif params.strip() == "":
            await self.send_message(message.channel, "Please specify PvE, PvP, WvW, Fractal, or Event achievements. (You can also add \"tomorrow\" to get tomorrow's dailies.)")
            return
        else:
            r = requests.get("https://api.guildwars2.com/v2/achievements/daily")
        dailies = r.json()
        
        category = params.split(" ")[0]
        cheevList = ""
        
        if category == "pve":
            list = dailies["pve"]
        elif category == "pvp":
            list = dailies["pvp"]
        elif category == "wvw":
            list = dailies["wvw"]
        elif "fractal" in category:
            list = dailies["fractals"]
        elif "event" or "special" in category:
            list = dailies["special"]
        
        if not list:
            await self.send_message(message.channel, "Sorry, looks like there isn't any dailies in that category today.")
            return
        else:
            for cheev in list:
                if cheev["level"]["max"] == 80:
                    cheevList += str(cheev["id"]) + ","
                    
        r = requests.get("https://api.guildwars2.com/v2/achievements?ids=" + cheevList)
        cheevs = r.json()
        
        msg = "\n\n"
        
        for cheev in cheevs:
            msg += "```markdown\n# " + cheev["name"] + " #"
            if cheev["description"]:
                msg += "\n> " + cheev["description"] + ""
            msg += "\n" + cheev["requirement"]
            msg += "```"
        
        await self.send_message(message.channel, msg)     
     
    async def c_kinkshame(self, message, params):
        
        fname = random.choice(os.listdir(os.path.dirname(os.path.abspath(__file__)) + "//kinkshame//"))
        target = params.split(" ")[0]
        
        if params.split(" ")[0] == "me":
            msg = message.author.mention
        else: 
            msg = target
        
        await self.send_file(message.channel, os.path.dirname(os.path.abspath(__file__)) + "//kinkshame//" + fname, filename=fname, content=msg)
     
    async def c_corbin(self, message, params):
    
        fname = random.choice(os.listdir(os.path.dirname(os.path.abspath(__file__)) + "//corbin//"))
        
        await self.send_file(message.channel, os.path.dirname(os.path.abspath(__file__)) + "//corbin//" + fname, filename=fname)
        await self.send_message(message.channel, "<:corbin:315013269540700161>")
    
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

if __name__ == "__main__":
    ashur = AshurBot()
    ashur.run(token)