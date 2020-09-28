import discord
from discord.ext import commands
from discord.ext.commands import bot

import pickle
import json

import os
from os.path import join
from os.path import dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = ('!chest ')

JAR = ('discord.pkl')

description='''Treasurebot for Dungeons & Dragons'''
bot = commands.Bot(command_prefix = BOT_PREFIX, description=description)

async def checkPickle(server_id):
    if os.path.getsize(JAR) > 0:
        pickle_data = pickle.load(open(JAR, "rb"))
        if server_id in pickle_data:
            return pickle_data
        else:
            money = {}
            items = []
            pickle_data[server_id] = {'money': money,'items': items}
            return pickle_data
    else:
        pickle_data = {}
        money = {}
        items = {}
        pickle_data[server_id] = {'money': money, 'items': items}
        outfile = open(JAR, 'wb')
        pickle.dump(pickle_data, outfile)
        outfile.close()
        return pickle_data

async def writeToPickle(pickle_data):
    outfile = open(JAR, 'wb')
    pickle.dump(pickle_data, outfile)
    outfile.close()


@bot.command(name='listAll', description='List all money and items in party treasury', pass_context=True)
async def listAll(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    msg = f"{json.dumps(pickle_data[server_id], indent=2, sort_keys=True)}"
    await context.send(msg)

@bot.command(name='Money', description='List all under money-index', pass_context=True)
async def listMoney(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    msg = f"{json.dumps(pickle_data[server_id]['money'], indent=2, sort_keys=True)}"
    await context.send(msg)

@bot.command(name='Items', description='List all under item-index', pass_context=True)
async def listItems(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    msg = f"{json.dumps(pickle_data[server_id]['items'], indent=2, sort_keys=True)}"
    await context.send(msg)

@bot.command(name='addMoney', description='Add money/valuables to party treasury', pass_context=True)
async def addMoney(context, amount: int, money_type):
    server_id = context.guild.id
    emoji = '\N{THUMBS UP SIGN}'
    pickle_data = await checkPickle(server_id)
    if money_type in pickle_data[server_id]['money']:
        pickle_data[server_id]['money'][money_type] += amount
    else:
        pickle_data[server_id]['money'][money_type] = amount
    await writeToPickle(pickle_data)
    await context.message.add_reaction(emoji)

@bot.command(name='addItem', desxription='Add item to party inventory', pass_context=True)
async def addItem(context, name, item_type, desc, weight: int):
    server_id = context.guild.id
    emoji = '\N{THUMBS UP SIGN}'
    pickle_data = await checkPickle(server_id)
    pickle_data[server_id]['items'][name] = {'type':item_type, 'desc':desc, 'weight(lbs)': weight}
    await writeToPickle(pickle_data)
    await context.message.add_reaction(emoji)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=''))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)