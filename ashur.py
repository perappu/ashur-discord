# -*- coding: UTF-8 -*-

import discord
import asyncio
import logging
import configparser
import os, sys
import random
import markoving
import re

import aiohttp
from io import BytesIO

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
        await self.change_presence(game=discord.Game(name='a!help'))
        
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

    #find who has logs
    async def c_logs(self, message, params):
        names = "I have logs for these people: ```"
        fileList = [f.replace(".txt","") for f in os.listdir(str(os.getcwd()) + "/logs/") if os.path.isfile(os.path.join(str(os.getcwd()) + "/logs/", f))]
        
        for i in fileList:
            names += message.server.get_member(i).name + "\n"
            
        names += "``` Please use `b!clearlogs` if you would like yourself removed."
        
        await self.send_message(message.channel, names)
        
    
    #read logs for use in other commands
    async def c_readlogs(self, message, params):
            
        badMessage = ["http","www","a!","b!","p!","<@!","AM]","PM]"]
            
        if (message.author.id == self.ownerID):
        
            #try:
                if (params == ""):
                    userID = str(message.author.id)
                    username = message.author.name
                    messageLimit = 1000
                else:
                    params = params.split(" ", 2)
                    userID = params[0].strip()
                    username = message.server.get_member(userID).name
                    messageLimit = int(params[1].strip())
                
                path = str(os.getcwd())
                
                logfile = None
                
                try:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="a",encoding="utf-8")
                except FileNotFoundError:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="w+",encoding="utf-8")
                else:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="a",encoding="utf-8")
                
                async for logmessage in self.logs_from(message.channel, messageLimit):
                    
                    if (logmessage.author.id in userID):
                        if(all(s not in logmessage.content for s in badMessage)):
                            print(logmessage.content)
                            logfile.write(logmessage.content.encode('unicode-escape').decode('unicode-escape') + "\n")
                
                logfile.close()
                await self.send_message(message.channel, "Okay, I read the last " + str(messageLimit) + " messages in " + message.channel.mention + " from " + username + ".")
            #except:
             #             await self.send_message(message.channel, "Something went wrong. Did you enter the params right?")
            
        else:
            try:
                userID = str(message.author.id)
                username = message.author.name
                
                path = str(os.getcwd())
                
                logfile = None
                
                try:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="a",encoding="utf-8")
                except FileNotFoundError:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="w+",encoding="utf-8")
                else:
                    logfile = open(path + "/logs/" + userID + ".txt",mode="a",encoding="utf-8")
                
                async for logmessage in self.logs_from(message.channel, messageLimit):
                    
                    if (logmessage.author.id in userID):
                        if(all(s not in logmessage.content for s in badMessage)):
                            print(logmessage.content)
                            logfile.write(logmessage.content + "\n")
                
                logfile.close()
                await self.send_message(message.channel, "Okay, I read your last 1000 messages in " + message.channel.mention + ". If you want me to read more, please @ " + self.ownerName + ".")
            except:
                await self.send_message(message.channel, "Something went wrong. Did you enter the params right?")
    
    #clear any saved logs for a user
    async def c_clearlogs(self, message, params):
    
        if (message.author.id == self.ownerID):
            try:
                if (params == ""):
                    userID = str(message.author.id)
                    username = message.author.name
                else:
                    userID = params.replace(" ","")
                    username = message.server.get_member(userID).name
            
                path = str(os.getcwd())
            
                try:
                    os.remove(path + "/logs/" + userID + ".txt")
                    await self.send_message(message.channel, "Okay, I deleted all stored logs from " + username + ".")
                except FileNotFoundError:
                    await self.send_message(message.channel, "There are no logs to delete for " + username + ".")
            except:
                await self.send_message(message.channel, "Something went wrong. Did you enter the params right?")
        else:
            userID = str(message.author.id)
            username = message.author.name
        
            path = str(os.getcwd())
        
            try:
                os.remove(path + "/logs/" + userID + ".txt")
                await self.send_message(message.channel, "I cleared your logs for you.")
            except FileNotFoundError:
                await self.send_message(message.channel, "You don't have any logs to delete.")
            
    
    #makes a fake quote for a user based off a markov model
    async def c_quote(self, message, params):

        userID = ""
        param = params.split(" ")[0]
        if param == "me" or param == "":
            userID = message.author.id
        elif "<@" in param:
            userID = re.sub("[^0-9]", "", param)
        else: 
            try:
                userID = message.server.get_member_named(params.split(" ")[0]).id
            except:
                await self.send_message(message.channel, "I couldn't find that user. This is case sensitive, did you enter it right?")
        username = message.server.get_member(userID).name    
        path = str(os.getcwd())
         
        try:
            text = ""
            
            with open(path + "/logs/" + userID + ".txt", mode="r", encoding="utf-8") as sampleFile:
                text = sampleFile.read().replace("\n", " ")
            
            fakeQuote = markoving.makeASentence(text)
            print(fakeQuote)
            
            await self.send_message(message.channel, "\"" + fakeQuote + "\" - " + username + ", probably")
        except FileNotFoundError:
            await self.send_message(message.channel, "There are no logs for " + username + ".")
    
    async def c_norn(self, message, params):
    
        name1 = ["Crunch", "Olaf", "Beef", "Chunk", "Smoke", "Brick", "Crash", "Thick", "Bold", "Buff", "Drunk", "Punch", "Crud", "Grizzle", "Slab", "Hack", "Big"]
        name2 = ["Mac", "Mc", ""]
        name3 = ["Butt", "Steak", "Hard", "Rock", "Large", "Huge", "Beef", "Thrust", "Big", "Bigger", "Meat", "Hard", "Fight", "Fizzle", "Run", "Fast", "Drink", "Lots", "Slam", "Chest", "Groin", "Bone", "Meal", "Thorn", "Body", "Squat"]
        
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
    
    async def c_gotosleep(self, message, params):
    
        target = params.split(" ")[0]
        
        if params.split(" ")[0] == "me":
            msg = message.author.mention
        else: 
            msg = target
    
        await self.send_file(message.channel, os.path.dirname(os.path.abspath(__file__)) + "//sleepobeepo.jpg", filename="sleepobeepo.jpg", content=msg)
        
    #random colorpalette from the colourlovers api    
    async def c_colors(self, message, params):
        if params == "":
            r = requests.get("http://www.colourlovers.com/api/palettes/random?format=json")
            palette = r.json()[0]
            image = palette["imageUrl"]
            url = palette["url"]
           
            async with aiohttp.ClientSession() as session:
            # note that it is often preferable to create a single session to use multiple times later - see below for this.
                async with session.get(image) as resp:
                    buffer = BytesIO(await resp.read())

            await self.send_file(message.channel, fp=buffer, filename="palette.png")
            await self.send_message(message.channel, "<" + url + ">")
        
    
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
        
        if (params == "") :
            for func in dir(self):
                if func.startswith('c_') and func != 'c_help':
                    text += func.replace("c_", self.prefix) + "\n"
            
            text += "``` \nType " + self.prefix + "help followed by the name of the command to get more information. \nRepo: https://github.com/stokori/ashur-discord"
        
        else:
            helpText = { 
            "clearlogs" : "Clears any stored logs you have. If used by my owner, can remove other people's logs.",
            "colors" : "Gets a random color palette from colourlovers.com.",
            "corbin" : "Gives you a random photo of Corbin!",
            "exit" : "I'm not telling you how to MURDER ME",
            "gotosleep" : "GO TO BED",
            "gw2daily" : "Like gw2bot, but shittier.",
            "hello" : "Hi.",
            "jisho" : "Looks up an english word, kana, or kanji from jisho.org.",
            "kinkshame" : "When you see or post some real bad content. If you don't specify, I'm just going to kinkshame you.",
            "logs" : "Shows the list of users with logs.",
            "norn" : "Generates a norn name.",
            "quote" : "Gives you something either you or someone else _probably_ said.",
            "readlogs" : "Stores the last 1000 messages you said in the current channel. If used by my owner, can read other people's logs.",
            "restart" : "Have you tried turning it off and on again?"
            }
            
            try:
                text = helpText[params.strip()]
            except:
                text = "That command doesn't exist, doesn't have help text yet, or you made a typo."
        
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
            
   # async def c_update(self, message, params):
    #    if (message.author.id == self.ownerID):
     #       await self.send_message(message.channel, "Updating. Better hope this doesn't crash me or you're gonna have to open up SSH anyways.")
      #      subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U','https://github.com/stokori/ashur-discord.git'])
       #     os.execl(sys.executable, sys.executable, *sys.argv)
        #else:
         #   await self.send_message(message.channel, "Sorry, only my owner(" + ownerName + ") can do that. Please @ them if I need to be updated.")

if __name__ == "__main__":
    ashur = AshurBot()
    ashur.run(token)