import sys
import os
import discord
import json
import arxiv
import datetime
from discord.ext import tasks
from tools import parse

import logging
logging.basicConfig(level=logging.DEBUG)

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

token = config['token']
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)
arxiv_client = arxiv.Client()


@discord_client.event
async def on_ready():
    loop.start()


@tasks.loop(seconds=60)
async def loop():
    await discord_client.wait_until_ready()
    dt_now = datetime.datetime.now()
    if dt_now.hour != 6 or dt_now.minute != 0:
        return
    since = dt_now - datetime.timedelta(days=2)
    until = dt_now - datetime.timedelta(days=1)
    for guild in discord_client.guilds:
        for channel in guild.text_channels:
            if channel.name[:4] == "auto":
                query = parse(channel.topic)
                append_string = 'submittedDate:[{} TO {}]'.format(
                    datetime.datetime.strftime(since, '%Y%m%d%H%M%S'), datetime.datetime.strftime(until, '%Y%m%d%H%M%S'))
                if len(query.query) == 0:
                    query.query = append_string
                else:
                    query.query += ' AND ' + append_string
                query.max_results = None
                result = arxiv_client.results(query)
                return_list = [""]
                for r in result:
                    next_content = r.title + '\n<' + str(r) + '>\n'
                    if len(return_list[-1]) + len(next_content) > 2000:
                        return_list.append(next_content)
                    else:
                        return_list[-1] += next_content
                sent = False
                for ret in return_list:
                    if len(ret) > 0:
                        await channel.send(ret[:-1])  # remove last \n
                        sent = True
                if sent == False:
                    await channel.send('No results found')


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return
    if discord_client.user not in message.mentions:
        return
    query = parse(message.content)
    result = arxiv_client.results(query)
    return_list = [""]
    for r in result:
        next_content = r.title + '\n<' + str(r) + '>\n'
        if len(return_list[-1]) + len(next_content) > 2000:
            return_list.append(next_content)
        else:
            return_list[-1] += next_content
    sent = False
    for ret in return_list:
        if len(ret) > 0:
            await message.channel.send(ret[:-1])  # remove last \n
            sent = True
    if sent == False:
        await message.channel.send('No results found')

discord_client.run(token)
