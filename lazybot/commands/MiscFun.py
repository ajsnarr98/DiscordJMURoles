""" File pertaining to miscellaneous fun commands. """

import random
import requests

from discord.ext import commands


class MiscFun(commands.Cog):
    """ Miscellaneous fun commands. """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["chuck"])
    async def chucknorris(self, ctx):
        """ Want to know some interesting Chuck Norris facts? """
        joke_msg = "{joke}"

        chuckPull = requests.get("http://api.icndb.com/jokes/random")
        if chuckPull and chuckPull.status_code == 200:
            joke = chuckPull.json()["value"]["joke"]
            await ctx.send(joke_msg.format(joke=joke))

    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, message: str):
        """ Usage: '8ball <question>'
        Gives a random 8ball response to the provided question.
    """
        response_emoji_list = [
            ":blush:",
            ":smirk:",
            ":ok_hand:",
            ":thinking_face:",
            ":rolling_eyes:",
        ]
        response_list = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]

        easter_egg = 0

        # easter egg 1 check
        temp_msg = message.lower().replace(",", "")
        if "answer" in temp_msg and "life the universe and everything" in temp_msg:
            easter_egg = 1

        # give either easter egg or random response
        if easter_egg == 1:
            response = "[**8Ball**] 42  :rocket:"
        else:
            response = "[**8Ball**] :crystal_ball: {0} {1}".format(
                random.choice(response_list), random.choice(response_emoji_list)
            )

        await ctx.send(response)
