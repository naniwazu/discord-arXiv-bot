import sys
import os
import discord
import json
import arxiv
from tools import parse

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

token = config['token']
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)
arxiv_client = arxiv.Client()


# @discord_client.event
# async def on_ready():
#     for guild in discord_client.guilds:
#         channel = discord.utils.get(guild.text_channels, name='bot-info')
#         await channel.send('bot ready')


# @discord_client.event
# async def on_connect():
#     for guild in discord_client.guilds:
#         channel = discord.utils.get(guild.text_channels, name='bot-info')
#         await channel.send('bot connected')


# @discord_client.event
# async def on_disconnect():
#     for guild in discord_client.guilds:
#         channel = discord.utils.get(guild.text_channels, name='bot-info')
#         await channel.send('bot disconnected')


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return
    if discord_client.user not in message.mentions:
        return
    query, max_results, since, until = parse(message.content)
    result = arxiv_client.results(query)
    return_list = [""]
    for r in result:
        if since is not None and r.published < since:
            continue
        if until is not None and r.published > until:
            continue
        next_content = r.title + '\n' + r.pdf_url + '\n'
        if len(return_list[-1]) + len(next_content) > 2000:
            return_list.append(next_content)
        else:
            return_list[-1] += next_content
        max_results -= 1
        if max_results <= 0:
            break
    for r in return_list:
        await message.channel.send(r[:-1])  # remove last \n

discord_client.run(token)
