#!/usr/bin/python3

#bot.py

import os
import subprocess
import discord

intents = discord.Intents.all()

TOKEN = "YOUR TOKEN HERE"
GUILD = "YOUR SERVER HERE"

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    command = message.content.split()
    if not command:
        return

    try:
        if os.name == 'nt':
            # Windows-specific handling
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error_output = process.communicate()
            output = output.decode("utf-8")
            error_output = error_output.decode("utf-8")
        else:
            # Linux handling
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = process.stdout.decode("utf-8")
            error_output = process.stderr.decode("utf-8")

        if output:
            await message.channel.send(output)
        if error_output:
            await message.channel.send(error_output)
    except subprocess.CalledProcessError as error:
        await message.channel.send(error.output.decode("utf-8"))

client.run(TOKEN)
