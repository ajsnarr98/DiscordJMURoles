if __name__ == '__main__':
    import dependencies
    dependencies.install() # attempt to install any missing dependencies

import asyncio
import logging
import os
import traceback

import discord
from discord.ext import commands

import secret
import self_updater

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
  description=description, pm_help=False)

### Utility Functions ###


### Event handlers ###

@bot.event
async def on_connect():
  logger.info('Connected!')
  logger.info('Username: {}'.format(bot.user.name))
  logger.info('ID: {}'.format(bot.user.id))

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
    logger.error('Ignoring exception in command {}'.format(context.command))
    print('Ignoring exception in command {}'.format(context.command), file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

### Commands ###

@bot.command()
async def gradyear(ctx, year):
  """ Set your graduation year. '!gradyear <year>' """
  n_year = 0
  try:
    n_year = int(year)
  except ValueError:
    await ctx.send('\'{}\' is not a number'.format(year))
    return
  
  await ctx.send('hello')
  

if __name__ == '__main__':
  logger.info('connecting...')
  bot.run(secret.botToken)
