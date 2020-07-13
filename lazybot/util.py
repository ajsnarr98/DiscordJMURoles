""" Utility functions for different parts of discord bot. """

import datetime
from typing import Callable, Union

import discord


def all_empty_roles(guild: discord.Guild) -> iter:
    """ Returns an interable containing all discord.Role objects in the guild that
        do not have any members assigned to them.
    """
    return filter(lambda r: len(r.members) == 0, guild.roles)


async def all_my_messages_since(
    bot: discord.ext.commands.Bot,
    since: Union[discord.abc.Snowflake, datetime.datetime],
):
    """ An asyncronous iterable over all messages from the bot since the given time. """
    for guild in bot.guilds:
        for channel in guild.text_channels:
            async for msg in channel.history(
                limit=None, after=since, oldest_first=False
            ):
                # if author was the bot
                if msg.author == guild.me:
                    yield msg


async def purge_in_all(
    bot: discord.ext.commands.Bot,
    since: Union[discord.abc.Snowflake, datetime.datetime],
    check: Callable[[discord.Message], bool] = None,
):
    """ Purges all messages since the given time that meet the given check.
        
        If no check is given, purge all messages
    """
    for guild in bot.guilds:
        for channel in guild.text_channels:
            await channel.purge(
                limit=None, after=since, oldest_first=False, check=check
            )


async def say_in_all(bot: discord.ext.commands.Bot, *args, **kwargs):
    """ A helper function that is equivalent to doing
        .. code-block:: python
    
            for channel in <one channel on every server>:
                channel.send(*args, **kwargs)
        Has a preference towards a text channel called 'general',
        where letter case does not matter.
        
        returns::
            A list of all sent messages.
    """
    sent_msgs = []
    for guild in bot.guilds:
        general_channel = None
        # look for text channel with name 'general'
        for channel in guild.text_channels:
            if channel.name.lower() == "general":
                general_channel = channel
                break
        if general_channel is not None:
            msg = await general_channel.send(*args, **kwargs)
            sent_msgs.append(msg)
        else:
            # if cannot find 'general', send to the first text channel
            for channel in guild.text_channels:
                msg = await channel.send(*args, **kwargs)
                sent_msgs.append(msg)
                break
    return sent_msgs


def static_vars(**kwargs):
    """ Decorator that allows static variables in a function. """

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate
