from os import listdir
import aiohttp
from os import popen, path
from discord.ext import commands
from asyncio import TimeoutError

__author__ = 'Sentry#4141'

class MissingCog(Exception):
    pass

class DragDrop:
    """Drag a cog into discord and get it running"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def drop(self, ctx):
        """Install cogs by uploading them over Discord"""

        if not ctx.message.attachments:
            await ctx.send('Drop a cog into Discord')
            try:
                msg = await self.bot.wait_for('message',
                                              check=lambda m:
                                              (any(m.attachments) and
                                               m.channel == ctx.message.channel and
                                               m.author == ctx.message.author),
                                              timeout=15)
            except TimeoutError:
                await ctx.send('No cog recieved')
                return


        else:
            msg = ctx.message

        if msg is None:
            await ctx.send('No cog recieved')
        elif msg.attachments[0].filename.endswith('.py'):
            if msg.attachments[0].filename in listdir('cogs'):
                await ctx.send(msg.attachments[0].filename[:-3] +
                               ' is already installed.\nOverwrite it? (yes/no)')
                try:
                    answer = await self.bot.wait_for('message',
                                                     timeout=15,
                                                     check=lambda m: m.author == ctx.message.author)
                except TimeoutError:
                    answer = None

                if answer is None:
                    await ctx.send('Keeping old cog.')
                    return
                elif answer.content.lower().strip() == "no":
                    await ctx.send('Keeping old cog.')
                    return

                # unload code
                try:
                    if path.exists("cogs/{}.py".format(msg.attachments[0].filename[:-3])):
                        self.bot.unload_extension("cogs.{}".format(
                            msg.attachments[0].filename[:-3]))

                    elif path.exists("custom_cogs/{}.py".format(
                            msg.attachments[0].filename[:-3])):

                        self.bot.unload_extension("custom_cogs.{}".format(
                            msg.attachments[0].filename[:-3]))

                except Exception as e:
                    await ctx.send(self.bot.bot_prefix +
                                   'Failed to unload module: `{}.py`'.format(
                                       msg.attachments[0].filename[:-3]))

                    await ctx.send(self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
                    return
                else:
                    await ctx.send(self.bot.bot_prefix +
                                   'Unloaded module: `{}.py`'.format(
                                       msg.attachments[0].filename[:-3]))


            try:
                commithash = popen('git rev-parse --verify HEAD').read()[:7]
            finally:
                if not commithash:
                    commithash = 'e22d220' # Lets just use the latest one

            gateway = msg.attachments[0].url
            payload = {}
            payload['limit'] = 1
            headers = {'user-agent': 'Discord-Selfbot/{}'.format(commithash)}

            session = aiohttp.ClientSession()
            async with session.get(gateway, params=payload, headers=headers) as r:
                cog = await r.read()
                with open('cogs/' + msg.attachments[0].filename, "wb") as f:
                    f.write(cog)
                    await ctx.send(msg.attachments[0].filename[:-3] + ' installed')
            session.close()

            await ctx.send("Load it now? (yes/no)")
            cog = msg.attachments[0].filename[:-3]
            try:
                answer = await self.bot.wait_for('message',
                                                 timeout=15,
                                                 check=lambda m:
                                                 m.author == ctx.message.author)
            except TimeoutError:
                answer = None

            if answer is None:
                await ctx.send("Ok then, you can load it with"
                               " `{}load {}`".format(ctx.prefix,
                                                     msg.attachments[0].filename[:-3]))
            elif answer.content.lower().strip() == "yes":

                # LOad code
                try:
                    if path.exists("custom_cogs/{}.py".format(msg.attachments[0].filename[:-3])):
                        self.bot.load_extension("custom_cogs.{}".format(msg.attachments[0].filename[:-3]))
                    elif path.exists("cogs/{}.py".format(msg.attachments[0].filename[:-3])):
                        self.bot.load_extension("cogs.{}".format(msg.attachments[0].filename[:-3]))
                    else:
                        raise ImportError("No module named '{}'".format(msg.attachments[0].filename[:-3]))
                except Exception as e:
                    await ctx.send(self.bot.bot_prefix + 'Failed to load module: `{}.py`'.format(msg.attachments[0].filename[:-3]))
                    await ctx.send(self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
                else:
                    await ctx.send(self.bot.bot_prefix + 'Loaded module: `{}.py`'.format(msg.attachments[0].filename[:-3]))

            else:
                await ctx.send("Ok then, you can load it with"
                               " `{}load {}`".format(ctx.prefix,
                                                         msg.attachments[0].filename[:-3]))


        else:
            await ctx.sendy(msg.attachments[0].filename + ' is not a valid cog')

def setup(bot):
    try:
        bot.get_cog('Owner')
    except:
        raise MissingCog('Core cog is missing')

    bot.add_cog(DragDrop(bot))
