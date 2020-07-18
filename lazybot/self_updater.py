import os
import sys
import time

import discord
import git
from discord.ext import commands, tasks

from util import say_in_all


def check_for_updates() -> bool:
    """ Pulls master branch of repo from git
        
        NOTE: Expects git to be initialized and
              current working dir to be in a cloned
              git repo.
              
        Return (bool):
            Whether or not updates were found.
    """

    no_changes = "Already up to date."

    working_dir = os.path.dirname(os.path.abspath(__file__))

    git_cmd = git.cmd.Git(working_dir=working_dir)
    info = git_cmd.pull()

    return str(info) != no_changes


def restart(logger, seconds_before_restart=5):
    """ Waits a determined amount of time and then restarts
        this program.
    """
    pre_wait_message = "event loop has stopped... restarting in {sec}"
    restarting_message = "restarting bot..."

    print()
    while seconds_before_restart > 0:
        print(pre_wait_message.format(sec=seconds_before_restart), end="\r")
        time.sleep(1)
        seconds_before_restart -= 1
    print()

    logger.debug(restarting_message)
    time.sleep(
        0.5
    )  # just small delay because print/log statements may now be part of a race condition

    python = sys.executable
    os.execl(python, python, *sys.argv)


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
        self.sent_msgs += await say_in_all(
            self.bot, "Update is available. Run '!update' to complete."
        )

    @tasks.loop(seconds=60.0)
    async def update_check(self):
        if check_for_updates() and not self.has_update:
            # if need to update for first time
            self.has_update = True  # this should be reset to false during restart
            await self.notify_about_update()
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name="Update Available"
                )
            )

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
