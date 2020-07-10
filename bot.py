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


class DiscordBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_command_prefix = kwargs.get('default_command_prefix', None)

    async def on_ready(self):
        logger.info('Connected!')
        logger.info('Username: {}'.format(self.user.name))
        logger.info('ID: {}'.format(self.user.id))
        
        # self.load_extension('extensions.core')

    async def on_command_error(self, exception, context):
        """ Logs and ignores errors in commands, unless that exception was from
            entering an invalid command, in which case this instead tells the
            user that they gave an invalid command.
        """
        if type(exception) == commands.errors.CommandNotFound:
            await self.send_message(context.message.channel, str(exception))
        elif type(exception) == commands.errors.MissingRequiredArgument:
            await self.send_message(context.message.channel,
                'Missing required argument. Please see \'{}help\'.'.format(self.default_command_prefix))
        else:
            logger.error('Ignoring exception in command {}'.format(context.command))
            print('Ignoring exception in command {}'.format(context.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

default_command_prefix = '!'

if __name__ == '__main__':
    description = ''' A bot to fulfill your wildest dreams. '''
    logger.info('connecting...')
    bot = DiscordBot(command_prefix=default_command_prefix, description=description, pm_help=False)
    bot.run(secret.botToken)
