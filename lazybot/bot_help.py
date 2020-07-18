import itertools

from discord.ext import commands


class StraightforwardHelp(commands.DefaultHelpCommand):
    """ A version of the default help command that does not show commands
        separated by categories.
    """

    async def send_bot_help(self, mapping):
        # code adapted from the DefaultHelpCommand source.

        ctx = self.context
        bot = ctx.bot

        if bot.description:
            # <description> portion
            self.paginator.add_line(bot.description, empty=True)

        no_category = "\u200b{0.no_category}:".format(self)

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return cog.qualified_name + ":" if cog is not None else no_category

        # sort by cog (not alphabetical)
        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        max_size = self.get_max_size(filtered)
        self.add_indented_commands(
            filtered, heading="\u200bCommands:", max_size=max_size
        )

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()
