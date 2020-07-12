""" File pertaining to the gradyear command. """

import re

import discord
from discord.ext import commands

from util import all_empty_roles

class CommandGradYear(commands.Cog):
  """ Supporting code for setting/changing a user's graduation year. """
  
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(aliases=['graduate', 'grad'])
  async def gradyear(self, ctx, year):
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
    
    await self.set_grad_year(ctx.author, n_year, ctx.guild)
    
    # clear unused graduation year roles
    await self.cleanup_empty_grad_year_roles(ctx.guild)

  ##########################
  #### helper functions ####
  ##########################
    
  def is_grad_year(self, role: discord.Role) -> bool:
    """ Returns true if it is a graduation role, else false. """
    return bool(re.match(r"(\d+) graduate", role.name.lower()))

  def get_grad_year(self, role: discord.Role) -> int:
    """ Returns the year if it is a graduation role, else None. """
    if self.is_grad_year(role):
      return int(re.search(r"\d+", role.name)[0])
    else:
      return -1

  async def get_grad_year_role(self, guild: discord.Guild, year: int) -> discord.Role:
    """ Retrieve the role matching a given year, or create a new role if needed.
    """
    if year <= 0:
      raise ValueError('Year cannot be <= 0')
    
    # create a dict mapping years (int) to existing roles (discord.Role)
    years = {}
    for role in guild.roles:
      role_year = self.get_grad_year(role)
      if role_year is not None:
        years[role_year] = role
    
    # if role exists, return it
    if year in years:
      return years[year]
    
    # otherwise, create new role
    role_name = '{} Graduate'.format(year)
    return await guild.create_role(name=role_name, mentionable=True, hoist=True,
      reason='Created new role for graduation year')
      
  async def cleanup_empty_grad_year_roles(self, guild: discord.Guild):
    """ Clears unused grad year roles in the given server. """
    to_clear = filter(lambda r: self.is_grad_year(r), all_empty_roles(guild))
    for role in to_clear:
      await role.delete(reason='No users marked as this graduation year')
    
  async def set_grad_year(self, member: discord.Member, year: int, guild: discord.Guild):
    """ Add a role to the user for the graduation year. if such a role does
        not yet exist, create a role for the year.
    """
    if year <= 0: 
      raise ValueError('Year cannot be <= 0')
    
    roles = member.roles
    roles = list(filter(lambda r: not self.is_grad_year(r), roles)) # remove old grad year role
    new_role = await self.get_grad_year_role(guild, year)
    roles.append(new_role) # add new grad year role
    
    # set new roles for member
    await member.edit(roles=roles)
