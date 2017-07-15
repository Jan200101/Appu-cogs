import discord
from discord.ext import commands
from random import randint, choice

class Channelinfo:
    """Shows Channel infos."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def channelinfo(self, ctx, *, channel: discord.Channel=None):
        """Shows channel informations"""

        if not channel:
            channel = ctx.message.channel

        userlist = [r.display_name for r in channel.voice_members]
        if not userlist:
            userlist = "None"
        else:
            userlist = "\n".join(userlist)

        created_at = ("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (ctx.message.timestamp - channel.created_at).days))

        emptyrand = u"\u2063" * randint(1, 10)

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(description="Channel ID: " + channel.id, colour=discord.Colour(value=colour))
        if "{}".format(channel.is_default) == "True":
            data.add_field(name="Default Channel", value="Yes")
        else:
            data.add_field(name="Default Channel", value="No")

        data.add_field(name="Type", value=channel.type)
        data.add_field(name="Position", value=channel.position)

        if '{}'.format(channel.type) == "voice":
            if channel.user_limit != 0:
                data.add_field(
                    name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(
                    len(channel.voice_members)))

            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)

        elif "{}".format(channel.type) == "text":
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)

        data.set_footer(text=created_at)
        data.set_author(name=channel.name)

        try:
            await self.bot.say(emptyrand, embed=data)
        except:
            await self.bot.say("I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(Channelinfo(bot))
