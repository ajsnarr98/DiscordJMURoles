""" File pertaining to the colors command. """

import re

import discord
from discord.ext import commands

from util import all_empty_roles


class CommandColor(commands.Cog):
    """ Supporting code for changing a user's color. """

    color_names = {
        "default": None,
        "aqua": "00C09A",
        "green": "00D166",
        "blue": "0099E1",
        "purple": "A652BB",
        "pink": "FD0061",
        "gold": "F8C300",
        "orange": "E67E22",
        "red": "E74C3C",
        "grey": "91A6A6",
        "light_grey": "969C9F",
        "navy": "34495E",
        "light_navy": "597E8D",
        "dark_aqua": "008369",
        "dark_green": "008E44",
        "dark_blue": "006798",
        "dark_purple": "7A8F2F",
        "dark_pink": "BC0057",
        "dark_gold": "CC7900",
        "dark_orange": "A84300",
        "dark_red": "B91A22",
        "dark_grey": "9936031",
        "dark_navy": "2C3E50",
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def color(self, ctx, color="$help$"):
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
        if color == "$help$":
            await ctx.send(
                "Color argument needed. See '!help color' for available colors."
            )

        # get color hex code
        if color in CommandColor.color_names:
            color = CommandColor.color_names[color]
        elif not (color.startswith("#") and len(color) == 7):
            # invalid hex code
            await ctx.send(
                "Unknown color or invalid hex code. Hex codes must contain a"
                + " '#' followed by 6 characters/numbers."
            )
            return
        else:
            # valid hex code, remove the '#'
            color = color[1:]

        await self.set_color(ctx.author, color, ctx.guild)

        # clear unused color roles
        await self.cleanup_empty_color_roles(ctx.guild)

    ##########################
    #### helper functions ####
    ##########################

    def is_color(self, role: discord.Role) -> bool:
        """ Returns true if it is a color role, else false. """
        return bool(re.match(r"color #......", role.name.lower()))

    def get_color(self, role: discord.Role) -> str:
        """ Returns the hex color if it is a graduation role, else None. """
        if self.is_color(role):
            return re.search(r"#......", role.name)[0][1:]
        else:
            return None

    async def get_color_role(self, guild: discord.Guild, color: str) -> discord.Role:
        """ Retrieve the role matching a given hex color, or create a new role if
            needed.
            
            Specify a color of None for the default color (None).
        """
        if type(color) != str and color is not None:
            raise ValueError("Invalid type passed for color: {}".format(type(color)))

        # if color is None, return None
        if color is None:
            return None

        # create a dict mapping colors (str) to existing roles (discord.Role)
        colors = {}
        for role in guild.roles:
            role_color = self.get_color(role)
            if role_color is not None:
                colors[role_color] = role

        # if role exists, return it
        if color in colors:
            return colors[color]

        # otherwise, create new role
        role_name = "Color #{}".format(color)
        color = discord.Color(int(color, 16))
        return await guild.create_role(
            name=role_name,
            mentionable=False,
            colour=color,
            reason="Created new color role",
        )

    async def cleanup_empty_color_roles(self, guild: discord.Guild):
        """ Clears unused color roles in the given server. """
        to_clear = filter(lambda r: self.is_color(r), all_empty_roles(guild))
        for role in to_clear:
            await role.delete(reason="No users using this color")

    async def set_color(self, member: discord.Member, color: str, guild: discord.Guild):
        """ Add a role to the user for the color. if such a role does
            not yet exist, create a role for the year. If given color is None,
            remove color roles from user to set them to default color.
        """
        if type(color) != str and color is not None:
            raise ValueError("Invalid type passed for color: {}".format(type(color)))

        roles = member.roles
        roles = list(
            filter(lambda r: not self.is_color(r), roles)
        )  # remove old color role

        if color is not None:
            new_role = await self.get_color_role(guild, color)
            roles.append(new_role)  # add new color role

        # set new roles for member
        await member.edit(roles=roles)
