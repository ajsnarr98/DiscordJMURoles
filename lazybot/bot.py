if __name__ == '__main__':
    import dependencies
    dependencies.install() # attempt to install any missing dependencies

import asyncio
import logging
import os
import random
import re
import requests
import sys
import traceback

import discord
from discord.ext import commands

import secret
import self_updater
from commands import CommandColor, CommandGradYear, MiscFun, StraightforwardHelp, UpdateChecker

# set up logger
log_filename = 'discord.log'
working_dir = os.path.dirname(os.path.abspath(__file__))
log_filename = os.path.join(working_dir, log_filename)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=log_filename, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# set up bot
default_command_prefix = '!'

description = ''' A bot to fulfill your wildest dreams. '''
bot = commands.Bot(command_prefix=default_command_prefix,
  description=description, pm_help=False, help_command=StraightforwardHelp())

### Event handlers ###

@bot.event
async def on_connect():
  print('Connected!')
  print('Username: {}'.format(bot.user.name))
  print('ID: {}'.format(bot.user.id))

@bot.event
async def on_command_error(ctx, exception):
  """ Logs and ignores errors in commands, unless that exception was from
      entering an invalid command, in which case this instead tells the
      user that they gave an invalid command.
  """
  if type(exception) == commands.errors.CommandNotFound:
    await ctx.send(str(exception))
  elif type(exception) == commands.errors.MissingRequiredArgument:
    await ctx.send(
      'Missing required argument. Please see \'{}help\'.'.format(default_command_prefix))
  else:
    logger.error('Ignoring exception in command {}'.format(ctx.command))
    print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    
@bot.event
async def on_member_join(member):
  # give a message on join
  await member.send('How goes it <@{id}>?\n\n'.format(id=member.id) +
   'You can use \'!gradyear <year>\' if you would like to set your grad year.' +
   ' Use \'!help\' for more commands')

### Commands ###

bot.add_cog(CommandColor(bot))
bot.add_cog(CommandGradYear(bot))
bot.add_cog(MiscFun(bot))

bot.add_cog(UpdateChecker(bot))

@bot.command(aliases=['restart'])
async def update(ctx):
  """ Checks for updates from git, and restarts bot. """
  self_updater.check_for_updates() # update checker probably already updated, but just make sure
  await ctx.send('restarting...')
  print('update started. stopping event loop...')
  raise KeyboardInterrupt() # kill program (gets caught by discord lib)

if __name__ == '__main__':
  print()
  print('connecting...')
  bot.run(secret.botToken)
    
  # finally, after event loop terminated
  self_updater.restart(logger)
