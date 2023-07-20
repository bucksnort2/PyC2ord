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
