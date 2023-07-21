# PyC2ord
Python Bot to use Discord as a C2 for Red Team

# Initial Setup
Before you can use this bot, you need to create a bot user on Discord and add it to a server. I recommend creating a new private server for you and your bot. There are many tutorials online on how to create and invite a bot user to your Discord server. Once you have these, save your bot token (keep it secret, keep it safe). Without this, you cannot communicate with your bot.

# bot.py
This is the first iteration of the bot I built. On the victim machine, you will need to download the discord.py library before running this bot.
It can run many CLI commands on Windows and Linux. The return value must be under 2000 characters, otherwise, Discord will not show it.

# client.py and server.py
First, you need to create a Discord bot user. There are many tutorials online, and if I find a good one, I'll link it here. Once you have a bot user ready, download server.py onto a machine you control and can be connected to by your target machines. You will need to install Python if you haven't already, and on your server machine, you need to install the discord.py library.

```python3 -m pip install discord```

Once installed, configure server.py with the port it is listening on, and an optional host to listen on. Leave host blank to listen on all network connections.

For your victim machines, edit client.py to point to your server. If you're on the local network, you can use a private IP address, and if you are attacking across the internet, your public IP address and the port-forwarded/opened port, and run it on your victim machine.

Go to your Discord server that has the bot user. You should see it as an active user. Use !h for a list of commands, !list to list all the connected clients, !target <index> to target a machine (index is in the list), and !execute <command> to run a command on the client machine.

Because of Discord's limits, any message longer than 2000 characters will not go through.

# TODO
server.py
 - There are some bugs I can sort out
 - Add a !name command to change the name of the different targets to be easier to remember.

Feel free to contact me with suggestions.

Discord @bucksnort2

Twitter @bucksnort21

Threads @bucksnort2

Email bucksnort2cyber@gmail.com



# Disclaimer: PyC2ord - A Discord C2 Bot for Red Teams

PyC2ord is an open-source project developed by Bucksnort2 for educational and research purposes. It is designed to be used as a tool by Red Teams for testing and assessing the security of their own systems. 

By accessing, downloading, or using PyC2ord, you agree that:

1. PyC2ord is provided "as-is" and without any warranties. The author makes no representations or warranties regarding the accuracy, functionality, or suitability of the tool. You use PyC2ord at your own risk.

2. The author of PyC2ord is not responsible for any illegal or malicious use of this tool. It is your responsibility to use PyC2ord in compliance with all applicable laws and regulations.

3. The author will not be liable for any damages, losses, or legal implications arising from the use of PyC2ord.

4. As an open-source project, users are free to modify, adapt, and distribute PyC2ord. However, any modifications or distributions should also include this disclaimer and attribute the author.

Please note that unauthorized access to computer systems, networks, or data is illegal and unethical. Ensure you have explicit permission from the owners of systems before testing or using PyC2ord.

Always use ethical hacking practices and respect the rights and privacy of others when conducting security assessments or tests.

Bucksnort2 reserves the right to change or update this disclaimer without prior notice.

Use PyC2ord responsibly and for legitimate purposes only.

Bucksnort2

bucksnort2cyber@gmail.com

2023-07-20

Remember: Only hack what you own, and hack it with permission. Stay ethical, stay responsible.
