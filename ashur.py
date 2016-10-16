import discord
import asyncio
import logging
import configparser
import os, sys

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

    ownerID = settings.get('Owner', 'ID')
    ownerName = settings.get('Owner', 'Name')
    prefix = settings.get('Options', 'Prefix')

    #various commands below that need docstrings...
    async def c_ping(self, message, params):
        await self.send_message(message.channel, "Pong!")
        
    async def c_hello(self, message, params):
        await self.send_message(message.channel, "Hello, " + message.author.name + ".")
        
    async def c_help(self, message, params):
        
        text = "Commands:\n```"

        for func in dir(self):
            if func.startswith('c_') and func != 'c_help':
                text += func.replace("c_", self.prefix) + "\n"
        
        text += "```"
        
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
    
    async def on_ready(self):
        print('Logged in successfully.')
        print(self.user.name)
        print(self.user.id)
        print('------')
    
    async def on_message(self, message):
        params = message.content.split(" ", 1)
        
        if message.content.startswith(self.prefix + 'ping'):
            await self.c_ping(message, params)
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