import discord
from discord.ext import commands, tasks

from self_updater import check_for_updates
from util import say_in_all

class UpdateChecker(commands.Cog):
  """ Handles scheduled checks for updates """
  
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.update_reminder.start()
    self.update_check.start()
    self.has_update = False
    self.sent_msgs = []
    
  def cog_unload(self):
    self.update_reminder.cancel()
    self.update_check.cancel()
  
  async def clear_update_messages(self):
    """ Clears all remembered update messages. """
    for msg in self.sent_msgs:
      try:
        await msg.delete()
      except discord.NotFound:
        pass
    self.sent_msgs = []
  
  async def notify_about_update(self):
    """ Sends a message to all channels about needing to update. """
    await self.clear_update_messages()
    self.sent_msgs += await say_in_all(self.bot, 'Update is available. Run \'!update\' to complete.')
  
  @tasks.loop(seconds=60.0)
  async def update_check(self):
    if check_for_updates() and not self.has_update:
      # if need to update for first time
      self.has_update = True # this should be reset to false during restart
      await self.notify_about_update()
      await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
        name='Update Available'))
      
  @tasks.loop(seconds=3600.0)
  async def update_reminder(self):
    if self.has_update:
      await self.notify_about_update()
  
  @update_check.before_loop
  async def before_update_check(self):
    # don't start until bot is ready
    await self.bot.wait_until_ready()
    
  @update_reminder.before_loop
  async def before_update_reminder(self):
    # don't start until bot is ready
    await self.bot.wait_until_ready()
