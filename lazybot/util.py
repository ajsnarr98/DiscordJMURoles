""" Utility functions for different parts of discord bot. """

import discord

def all_empty_roles(guild: discord.Guild) -> iter:
  """ Returns an interable containing all discord.Role objects in the guild that
      do not have any members assigned to them.
  """
  return filter(lambda r: len(r.members) == 0, guild.roles)
