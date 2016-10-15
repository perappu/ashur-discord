import discord
import asyncio
import logging
import configparser

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

# Initialize Client
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def ping(message):
    await client.send_message(message.channel, "Pong!")
    
async def exit(message):
    await client.send_message(message.channel, "Later, nerds.")
    quit()
    
@client.event
async def on_message(message):
    if message.content.startswith('!ping'):
        await ping(message)
    if message.content.startswith('!exit'):
        await exit(message)

client.run(token)