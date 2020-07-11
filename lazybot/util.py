""" Utility functions for different parts of discord bot. """

import discord

def all_empty_roles(guild: discord.Guild) -> iter:
  """ Returns an interable containing all discord.Role objects in the guild that
      do not have any members assigned to them.
  """
  return filter(lambda r: len(r.members) == 0, guild.roles)
  
async def say_in_all(bot: discord.ext.commands.Bot, *args, **kwargs):
  """ A helper function that is equivalent to doing
      .. code-block:: python
  
          for channel in <one channel on every server>:
              channel.send(*args, **kwargs)
      Has a preference towards a text channel called 'general',
      where letter case does not matter.
  """
  for guild in bot.guilds:
    general_channel = None
    # look for text channel with name 'general'
    for channel in guild.text_channels:
      if channel.name.lower() == 'general':
        general_channel = channel
        break
    if general_channel is not None:
      await general_channel.send(*args, **kwargs)
    else:
      # if cannot find 'general', send to the first text channel
      for channel in guild.text_channels:
        await channel.send(*args, **kwargs)
        break
