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


@discord_client.event
async def on_ready():
    print('bot ready')
    guild = discord.utils.get(discord_client.guilds, name='arXiv 取得用')
    channel = discord.utils.get(guild.text_channels, name='arxiv')
    await channel.send('bot ready')


@discord_client.event
async def on_connect():
    print('bot connected')


@discord_client.event
async def on_disconnect():
    print('bot disconnected')
    guild = discord.utils.get(discord_client.guilds, name='arXiv 取得用')
    channel = discord.utils.get(guild.text_channels, name='arxiv')
    await channel.send('bot disconnected')


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return
    query = parse(message.content)
    result = arxiv_client.results(query)
    for r in result:
        await message.channel.send(r.title)
        await message.channel.send(r.pdf_url)

discord_client.run(token)
