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

def all_empty_roles(guild: discord.Guild) -> iter:
  """ Returns an interable containing all discord.Role objects in the guild that
      do not have any members assigned to them.
  """
  return filter(lambda r: len(r.members) == 0, guild.roles)
  
def is_color(role: discord.Role) -> bool:
  """ Returns true if it is a color role, else false. """
  return bool(re.match(r"color #......", role.name.lower()))
  
def get_color(role: discord.Role) -> str:
  """ Returns the hex color if it is a graduation role, else None. """
  if is_color(role):
    return re.search(r"#......", role.name)[0][1:]
  else:
    return None

async def get_color_role(guild: discord.Guild, color: str) -> discord.Role:
  """ Retrieve the role matching a given hex color, or create a new role if
      needed.
      
      Specify a color of None for the default color (None).
  """
  if type(color) != str and color is not None:
    raise ValueError('Invalid type passed for color: {}'.format(type(color)))
  
  # if color is None, return None
  if color is None:
    return None
  
  # create a dict mapping colors (str) to existing roles (discord.Role)
  colors = {}
  for role in guild.roles:
    role_color = get_color(role)
    if role_color is not None:
      colors[role_color] = role
  
  # if role exists, return it
  if color in colors:
    return colors[color]
  
  # otherwise, create new role
  role_name = 'Color #{}'.format(color)
  color = discord.Color(int(color, 16))
  return await guild.create_role(name=role_name, mentionable=False, colour=color,
    reason='Created new color role')

async def cleanup_empty_color_roles(guild: discord.Guild):
  """ Clears unused color roles in the given server. """
  to_clear = filter(lambda r: is_color(r), all_empty_roles(guild))
  for role in to_clear:
    await role.delete(reason='No users using this color')
    
async def set_color(member: discord.Member, color: str, guild: discord.Guild):
  """ Add a role to the user for the color. if such a role does
      not yet exist, create a role for the year. If given color is None,
      remove color roles from user to set them to default color.
  """
  if type(color) != str and color is not None:
    raise ValueError('Invalid type passed for color: {}'.format(type(color)))
  
  roles = member.roles
  roles = list(filter(lambda r: not is_color(r), roles)) # remove old color role
  
  if color is not None:
    new_role = await get_color_role(guild, color)
    roles.append(new_role) # add new color role
  
  # set new roles for member
  await member.edit(roles=roles)

def is_grad_year(role: discord.Role) -> bool:
  """ Returns true if it is a graduation role, else false. """
  return bool(re.match(r"(\d+) graduate", role.name.lower()))

def get_grad_year(role: discord.Role) -> int:
  """ Returns the year if it is a graduation role, else None. """
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
    if role_year is not None:
      years[role_year] = role
  
  # if role exists, return it
  if year in years:
    return years[year]
  
  # otherwise, create new role
  role_name = '{} Graduate'.format(year)
  return await guild.create_role(name=role_name, mentionable=True, hoist=True,
    reason='Created new role for graduation year')
    
async def cleanup_empty_grad_year_roles(guild: discord.Guild):
  """ Clears unused grad year roles in the given server. """
  to_clear = filter(lambda r: is_grad_year(r), all_empty_roles(guild))
  for role in to_clear:
    await role.delete(reason='No users marked as this graduation year')
  
async def set_grad_year(member: discord.Member, year: int, guild: discord.Guild):
  """ Add a role to the user for the graduation year. if such a role does
      not yet exist, create a role for the year.
  """
  if year <= 0: 
    raise ValueError('Year cannot be <= 0')
  
  roles = member.roles
  roles = list(filter(lambda r: not is_grad_year(r), roles)) # remove old grad year role
  new_role = await get_grad_year_role(guild, year)
  roles.append(new_role) # add new grad year role
  
  # set new roles for member
  await member.edit(roles=roles)

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
async def color(ctx, color='$help$'):
  """ Usage examples: '!color red' or '!color #32A852'. See !help color for all options.
  
      '!color <color>'
      You can specify either any of the named colors below, or, if you wish,
      give a specific hexadecimal color code.
      
      Use 'default' to switch back to default color.
  
      All named colors:
        default
        aqua
        green
        blue
        purple
        pink
        gold
        orange
        red
        grey
        light_grey
        navy
        light_navy
        dark_aqua
        dark_green
        dark_blue
        dark_purple
        dark_pink
        dark_gold
        dark_orange
        dark_red
        dark_grey
        dark_navy
  """
  
  # if no argument given
  if color == '$help$':
    await ctx.send('Color argument needed. See \'!help color\' for available colors.')
  
  color_names = {
    'default': None,
    'aqua': '00C09A',
    'green': '00D166',
    'blue': '0099E1',
    'purple': 'A652BB',
    'pink': 'FD0061',
    'gold': 'F8C300',
    'orange': 'E67E22',
    'red': 'E74C3C',
    'grey': '91A6A6',
    'light_grey': '969C9F',
    'navy': '34495E',
    'light_navy': '597E8D',
    'dark_aqua': '008369',
    'dark_green': '008E44',
    'dark_blue': '006798',
    'dark_purple': '7A8F2F',
    'dark_pink': 'BC0057',
    'dark_gold': 'CC7900',
    'dark_orange': 'A84300',
    'dark_red': 'B91A22',
    'dark_grey': '9936031',
    'dark_navy': '2C3E50'
  }
    
  # get color hex code
  if color in color_names:
    color = color_names[color]
  elif not (color.startswith('#') and len(color) == 7):
    # invalid hex code
    ctx.send('Unknown color or invalid hex code. Hex codes must contain a' +
      ' \'#\' followed by 6 numbers.')
    return
    
  await set_color(ctx.author, color, ctx.guild)
  
  # clear unused color roles
  await cleanup_empty_color_roles(ctx.guild)
    

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
  
  # clear unused graduation year roles
  await cleanup_empty_grad_year_roles(ctx.guild)
  

if __name__ == '__main__':
  print()
  print('connecting...')
  bot.run(secret.botToken)
