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

class AshurBot(discord.Client):

    client = discord.Client()

    def __init__(self):
        # Initialize Client
        self.token = settings.get('Connection', 'Token')
        self.ownerID = settings.get('Owner', 'ID')
        self.ownerName = settings.get('Owner', 'Name')
        self.prefix = settings.get('Options', 'Prefix')

    async def c_ping(self, message, params):
        await client.send_message(message.channel, "Pong!")
        
    async def c_hello(self, message, params):
        await client.send_message(message.channel, "Hello, " + message.author.name + ".")
        
    async def c_help(self, message, params):
        message = "Commands:\n```"

        for func in dir(self):
            if func.startswith('c_') and func != 'c_help':
                messages += func.replace("c_", prefix) + "\n"
        
        message += "```"
        
        await client.send_message(message.channel, message)
        
    async def c_restart(self, message, params):
        if (message.author.id == ownerID):
            await client.send_message(message.channel, "Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await client.send_message(message.channel, "Sorry, only my owner(" + ownerName + ") can do that. Please @ them if I need to be restarted.")
        
    async def c_exit(self, message, params):
        if (message.author.id == ownerID):
            await client.send_message(message.channel, "Later, nerds.")
            quit()
        else:
            await client.send_message(message.channel, "Sorry, only my owner(" + ownerName + ") can do that. Please @ them if I need to be exited.")
    
    @client.event
    async def on_ready():
        print('Logged in successfully.')
        #I have no idea how to make it print this info from here, because I can't pass in self.
        #It's not particularly important though.
        #print(self.client.user.name)
        #print(self.client.user.id)
        print('------')
    
    @client.event
    async def on_message(self, message):
        
        params = message.content.split(" ", 1)
        
        if message.content.startswith(prefix + 'ping'):
            await c_ping(message, params)
        if message.content.startswith(prefix + 'hello'):
            await c_hello(message, params)
        if message.content.startswith(prefix + 'help'):
            await c_help(message, params)
        if message.content.startswith(prefix + 'exit'):
            await c_exit(message, params)
        if message.content.startswith(prefix + 'restart'):
            await c_restart(message, params)

    def start(self):
        self.client.run(self.token)
        print('Bot started.')

if __name__ == "__main__":
    ashur = AshurBot()
    ashur.start()