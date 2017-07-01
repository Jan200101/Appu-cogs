import discord
from discord.ext import commands
from random import choice, randint

class EmbedSay:
    """Make announcements in embeds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, pass_context=True, no_pm=True)
    async def embedsay(self, ctx, *, text: str):
        """The good old embedsay from Sentry-Cogs brought into embednotification.
        This Version has all features from embedsayadmin for normal and selfbots
        and it does not face the same restrictions as embednotifications."""

        colour = ''.join([choice('0123456789ABCDEF') for x in range(5)])
        colour = int(colour, 16)
		


        await self.bot.delete_message(ctx.message)
				

        normaltext = u"\u2063" * randint(1, 10) # Generating a random number for a empty embed

        data = discord.Embed(description=str(text), colour=discord.Colour(value=color))

        try:
            await self.bot.say(normaltext, embed=data)
        except:
            await self.bot.send_message(ctx.message.author, "I need the `Embed links` permission on `{}` to embed your message".format(ctx.message.server))

def setup(bot):
    bot.add_cog(EmbedSay(bot))
