# PyC2ord
Python Bot to use Discord as a C2 for Red Team

# bot.py
This is the first iteration of the bot I built. On the victim machine, you will need to download the discord.py library before running this bot.
It can run many CLI commands on Windows and Linux. The return value must be under 2000 characters, otherwise, Discord will not show it.

# client.py and server.py
These are currently in-progress. You can run server.py on a machine you host and deploy client.py on your victim machines. Run server.py first, then start client.py. The client machines will establish a connection and the server will display the connection.

# TODO
server.py
 - Create a !help command to list all the Discord commands you can run
 - Other things as I see fit

client.py
 - Allow incoming connections from the server to execute commands
 - Other things as I see fit

Feel free to contact me with suggestions.

Discord @bucksnort2 Twitter @bucksnort21 Threads @bucksnort2

