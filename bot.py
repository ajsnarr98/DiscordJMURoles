if __name__ == '__main__':
    import dependencies
    dependencies.install() # attempt to install any missing dependencies

import asyncio
import logging
import os
import re
import sys
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

def is_grad_year(role: discord.Role) -> bool:
  """ Returns true if it is a graduation role, else false. """
  return re.match(r"(\d+) graduate", role.name.lower())

def get_grad_year(role: discord.Role) -> int:
  """ Returns the year if it is a graduation role, else -1. """
  if is_grad_year(role):
    return int(re.search(r"\d+", role.name)[0])
  else:
    return -1

async def get_grad_year_role(guild: discord.Guild, year: int) -> discord.Role:
  """ Retrieve the role matching a given year, or create a new role if needed.
  """
  if year <= 0:
    raise ValueError('Year cannot be <= 0')
  
  # create a dict mapping years (int) to existing roles (discord.Role)
  years = {}
  for role in guild.roles:
    role_year = get_grad_year(role)
    if role_year > 0:
      years[role_year] = role
  
  # if role exists, return it
  if year in years:
    return years[year]
  
  # otherwise, create new role
  role_name = '{} Graduate'.format(year)
  return await guild.create_role(name=role_name, mentionable=True, hoist=True,
    reason='Created new role for graduation year')
  
async def set_grad_year(member: discord.Member, year: int, guild: discord.Guild):
  """ Add a role to the user for the graduation year. if such a role does
      not yet exist, create a role for the year. Finally, clear unused graduation
      year roles.
  """
  if year <= 0: 
    raise ValueError('Year cannot be <= 0')
  
  roles = member.roles
  roles = list(filter(lambda r: not is_grad_year(r), roles)) # remove old grad year role
  new_role = await get_grad_year_role(guild, year)
  roles.append(new_role) # add new grad year role
  
  # set new roles for member
  await member.edit(roles=roles)
  
  # TODO - clear unused graduation year roles

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

### Commands ###

@bot.command()
async def gradyear(ctx, year):
  """ Usage: '!gradyear <year>'. Set your graduation year. """
  n_year = 0
  try:
    n_year = int(year)
  except ValueError:
    await ctx.send('\'{}\' is not a number'.format(year))
    return
    
  if n_year <= 0:
    await ctx.send('Invalid year')
    return
  
  await set_grad_year(ctx.author, n_year, ctx.guild)
  

if __name__ == '__main__':
  print()
  print('connecting...')
  bot.run(secret.botToken)
