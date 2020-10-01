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
if not os.path.isfile('discord.pkl'):
    open('discord.pkl', 'a').close()

THUMBS_UP = '\N{THUMBS UP SIGN}'
THUMBS_DOWN = '\N{THUMBS DOWN SIGN}'

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
    await listMoney(context)
    await listItems(context)

@bot.command(name='Money', description='List all under money-index', pass_context=True)
async def listMoney(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    msg = "Money:\n"
    for key, value in pickle_data[server_id]['money'].items():
        msg += f"\t{key}: {value}\n"
    await context.send(msg)

@bot.command(name='Items', description='List all under item-index', pass_context=True)
async def listItems(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    msg = ""
    for item, data in pickle_data[server_id]['items'].items():
        msg += f"{item}:\n"
        for key, val in data.items():
            msg += f"\t{key}: {val}\n"
    await context.send(msg)

@bot.command(name='Weight', description='Get total weight of inventory items', pass_context=True)
async def getWeight(context):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    total_weight = 0
    for item, data in pickle_data[server_id]['items'].items():
        total_weight += (next((val for key, val in data.items() if 'weight' in key), None))
    msg = f"Total weight: {total_weight} lbs"
    await context.send(msg)

@bot.command(name='addMoney', description='Add money/valuables to party treasury', pass_context=True)
async def addMoney(context, amount: int, money_type):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    if money_type in pickle_data[server_id]['money']:
        pickle_data[server_id]['money'][money_type] += amount
    else:
        pickle_data[server_id]['money'][money_type] = amount
    await writeToPickle(pickle_data)
    await context.message.add_reaction(THUMBS_UP)

@bot.command(name='addItem', desxription='Add item to party inventory', pass_context=True)
async def addItem(context, name, item_type, desc, weight: float):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    pickle_data[server_id]['items'][name] = {'type':item_type, 'desc':desc, 'weight(lbs)': weight}
    await writeToPickle(pickle_data)
    await context.message.add_reaction(THUMBS_UP)

@bot.command(name='removeMoney', description='Remove money/valuables from party treasury', pass_context=True)
async def removeMoney(context, amount: int, money_type):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    if money_type in pickle_data[server_id]['money']:
        pickle_data[server_id]['money'][money_type] -= amount
        if pickle_data[server_id]['money'][money_type] < 0:
            pickle_data[server_id]['money'][money_type] = 0
        await context.message.add_reaction(THUMBS_UP)
    else:
        await context.message.add_reaction(THUMBS_DOWN)

@bot.command(name='removeItem', description='Remove item from party inventory', pass_context=True)
async def removeItem(context, name):
    server_id = context.guild.id
    pickle_data = await checkPickle(server_id)
    if name in pickle_data[server_id]['items']:
        del pickle_data[server_id]['items'][name]
        await context.message.add_reaction(THUMBS_UP)
    else:
        await context.message.add_reaction(THUMBS_DOWN)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=''))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)