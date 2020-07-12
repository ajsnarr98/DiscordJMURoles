# LazyBot
A Discord bot for helping change roles in JMU Grad Discord

## Installation Requirements:
1. Python 3.7 or greater
1. Git

### Running
1. Copy secret_example.py and make a new file called secret.py with your discord bot token
1. Run bot.py

## Developers
### Creating Commands
For an example of a set of created commands, see commands in lazybot/commands/MiscFun.py.

To begin to add a command, add a new or edit an existing class (like MiscFun) inheriting from discord.ext.commands.Cog, and put commands inside it. The doc comments for your function (command) are the command's help message, and the name of the your function is by default the name of the command (see docs linked in [Rapptz/discord.py](https://github.com/Rapptz/discord.py) for more info).

To finish adding your command, add a line to lazybot/commands/__init__.py like the others there (if you added a new class), and then in bot.py (if you added a new class), make a call to bot.add_cog() with an instance of your discord.ext.commands.Cog class as the paramenter. Other calls to add_cog() can be found towards the bottom of the file in the commands section.
