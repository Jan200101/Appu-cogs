from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from random import randint
from re import sub
from sys import argv
from os.path import exists, abspath, dirname, splitext
from os import makedirs, devnull, getcwd, chdir, listdir, replace, popen as ospopen
from asyncio import sleep
from getpass import getuser
from platform import uname, python_version
from json import decoder, dump, load

try:
    from subprocess import DEVNULL # Python 3
except ImportError:
    DEVNULL = open(devnull, 'r+b', 0)

from discord.ext import commands

__author__ = 'Sentry#4141'

class DataIO():

    def save_json(self, filename, data):
        """Atomically save a JSON file given a filename and a dictionary."""
        path, ext = splitext(filename)
        tmp_file = "{}.{}.tmp".format(path, randint(1000, 9999))
        with open(tmp_file, 'w', encoding='utf-8') as f:
            dump(data, f, indent=4,sort_keys=True,separators=(',',' : '))
        try:
            with open(tmp_file, 'r', encoding='utf-8') as f:
                data = load(f)
        except decoder.JSONDecodeError:
            print("Attempted to write file {} but JSON "
                  "integrity check on tmp file has failed. "
                  "The original file is unaltered."
                  "".format(filename))
            return False
        except Exception as e:
            print('A issue has occured saving ' + filename + '.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(str(e), e.args))
            return False

        replace(tmp_file, filename)
        return True

    def load_json(self, filename):
        """Load a JSON file and return a dictionary."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = load(f)
            return data
        except Exception as e:
            print('A issue has occured loading ' + filename + '.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(str(e), e.args))
            return {}

    def is_valid_json(self, filename):
        """Verify that a JSON file exists and is readable.
           Take in a filename and return a boolean."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = load(f)
            return True
        except (FileNotFoundError, decoder.JSONDecodeError):
            return False
        except Exception as e:
            print('A issue has occured validating ' + filename + '.\n'
                  'Traceback:\n'
                  '{0} {1}'.format(str(e), e.args))
            return False

dataIO = DataIO()

class Terminal:
    """Repl like Terminal in discord"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(abspath(dirname(argv[0])) +
                                         '/settings/terminal/settings.json')
        self.prefix = self.settings['prefix']

        self.alias = self.settings['alias']
        self.os = self.settings['os']
        self.cos = self.settings['cos']
        self.enabled = self.settings['enabled']
        self.sessions = {}


    @commands.command(pass_context=True, hidden=True)
    async def cmddebug(self, ctx):
        """This command is for debugging only"""
        try:
            commithash = ospopen('git rev-parse --verify HEAD').read()[:7]
        finally:
            if not commithash:
                commithash = 'None'

        text = str('```'
                   'Bot Information\n\n'
                   'Bot name:           {}\n'
                   'Bot displayname:    {}\n'
                   'Bot directory        {}\n\n'
                   'Operating System:   {}\n'
                   'OS Version:         {}\n'
                   'Architecture:       {}\n\n'
                   'Python Version:     {}\n'
                   'Commit              {}\n'
                   '```'.format(ctx.author.name,
                                ctx.author.display_name,
                                abspath(dirname(argv[0])), uname()[0],
                                uname()[3], uname()[4], python_version(),
                                commithash))

        result = []
        in_text = text
        shorten_by = 12
        page_length = 2000
        num_mentions = text.count("@here") + text.count("@everyone")
        shorten_by += num_mentions
        page_length -= shorten_by
        while len(in_text) > page_length:
            closest_delim = max([in_text.rfind(d, 0, page_length)
                                 for d in ["\n"]])
            closest_delim = closest_delim if closest_delim != -1 else page_length
            to_send = in_text[:closest_delim].replace(
                "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
            result.append(to_send)
            in_text = in_text[closest_delim:]

        result.append(in_text.replace(
            "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))

        for page in result:
            await ctx.send(page)

    @commands.group(pass_context=True, hidden=True)
    async def system(self, ctx):
        """Returns system infromation"""
        await ctx.send('{} is running on {} {} using {}'
                       ''.format(ctx.message.guild.me.display_name,
                                 uname()[0], uname()[2], python_version()))

    @commands.command(pass_context=True)
    async def cmd(self, ctx):
        """Starts up the prompt"""
        if ctx.message.channel.id in self.sessions:
            await ctx.send('Already running a Terminal session '
                           'in this channel. Exit it with `exit()` or `quit`')
            return

        # Rereading the values that were already read in __init__ to ensure its always up to date
        try:
            self.settings = dataIO.load_json(abspath(dirname(argv[0])) +
                                             '/settings/terminal/settings.json')
        except Exception:
            # Pretend its the worst case and reset the settings
            check_folder()
            check_file()
            self.settings = dataIO.load_json(abspath(dirname(argv[0])) +
                                             '/settings/terminal/settings.json')

        self.prefix = self.settings['prefix']
        self.alias = self.settings['alias']
        self.os = self.settings['os']

        self.sessions.update({ctx.message.channel.id:getcwd()})
        await ctx.send('Enter commands after {} to execute them.'
                       ' `exit()` or `quit` to exit.'.format(self.prefix.replace("`", "\\`")))

    @commands.group(pass_context=True)
    async def cmdsettings(self, ctx):
        """Settings for BetterTerminal"""
        if ctx.invoked_subcommand is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.message.channel.send(page)

    @cmdsettings.group(name="alias", pass_context=True)
    async def _alias(self, ctx):
        """Custom aliases for BetterTerminal"""
        await ctx.send('This feature is still being worked on.\n'
                       'Currently you can add aliases via the config file')
        """
        if ctx.invoked_subcommand is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.message.channel.send(page)
                """

    @cmdsettings.command(name="os", pass_context=True)
    async def _os(self, ctx, os: str = None):
        """Set the prompt type of BetterTerminal to emulate another Operatingsystem.
        these 'emulations' arent 100% accurate on other Operating systems"""

        if os is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.message.channel.send(page)
            if self.cos == 'default':
                await ctx.send('```\nCurrent prompt type: {}[{}] ```\n'
                               ''.format(self.cos, uname()[0].lower()))
            else:
                await ctx.send('```\nCurrent prompt type: {} ```\n'.format(self.cos))
            return

        if not os.lower() in self.os and os != 'default':
            await ctx.send('Invalid prompt type.\nThe following once are valid:\n\n{}'
                           ''.format(", ".join(self.os)))
            return

        os = os.lower()

        self.cos = os
        self.settings['cos'] = os
        dataIO.save_json(abspath(dirname(argv[0])) +
                         '/settings/terminal/settings.json', self.settings)
        await ctx.send('Changed prompt type to {} '.format(self.cos.replace("`", "\\`")))

    @cmdsettings.command(name="prefix", pass_context=True)
    async def _prefix(self, ctx, prefix: str = None):
        """Set the prefix for the Terminal"""

        if prefix is None:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.message.channel.send(page)
            await ctx.send('```\nCurrent prefix: {} ```\n'.format(self.prefix))
            return

        self.prefix = prefix
        self.settings['prefix'] = prefix
        dataIO.save_json(abspath(dirname(argv[0])) +
                         '/settings/terminal/settings.json', self.settings)

        await ctx.send('Changed prefix to {} '.format(self.prefix.replace("`", "\\`")))

    async def on_message(self, message): # This is where the magic starts

        if (message.channel.id in self.sessions and self.enabled and message.author.id == self.bot.user.id): # DO NOT DELETE

            #TODO:
            #  Whitelist & Blacklists that cant be modified by the bot

            if not dataIO.is_valid_json(abspath(dirname(argv[0])) +
                                        '/settings/terminal/settings.json'):
                check_folder()
                check_file()
                self.settings = dataIO.load_json(abspath(dirname(argv[0])) +
                                                 '/settings/terminal/settings.json')
                self.prefix = self.settings['prefix']
                self.alias = self.settings['alias']
                self.os = self.settings['os']
                self.cos = self.settings['cos']
                self.enabled = self.settings['enabled']

            if (message.content.startswith(self.prefix) or
                    message.content.startswith('debugprefixcmd')):

                if message.content.startswith(self.prefix):
                    command = message.content[len(self.prefix):]
                else:
                    command = message.content[len('debugprefixcmd'):]
                # check if the message starts with the command prefix

                if message.attachments:
                    command += ' ' + message.attachments[0]['url']

                if not command: # if you have entered nothing it will just ignore
                    return

                if command in self.alias:
                    if self.alias[command][uname()[0].lower()]:
                        command = self.alias[command][uname()[0].lower()]
                    else:
                        command = self.alias[command]['linux']

                if (command == 'exit()' or
                        command == 'quit'):  # commands used for quiting cmd, same as for repl

                    await message.channel.send('Exiting.')
                    self.sessions.pop(message.channel.id)
                    return

                if command.startswith('cd ') and command.split('cd ')[1]:
                    path = command.split('cd ')[1]
                    try:
                        oldpath = abspath(dirname(argv[0]))
                        chdir(self.sessions[message.channel.id])
                        chdir(path)
                        self.sessions.update({message.channel.id:getcwd()})
                        chdir(oldpath)
                        return
                    except FileNotFoundError:
                        shell = 'cd: {}: Permission denied'.format(path)
                    except PermissionError:
                        shell = 'cd: {}: No such file or directory'.format(path)
                else:
                    try:
                        output = Popen(command, cwd=self.sessions[message.channel.id],
                                       shell=True, stdout=PIPE,
                                       stderr=STDOUT, stdin=DEVNULL).communicate()[0]
                        error = False
                    except CalledProcessError as err:
                        output = err.output
                        error = True

                    shell = output.decode('utf_8')

                if shell == "" and not error:
                    return

                shell = sub('/bin/sh: .: ', '', shell)

                if "\n" in shell[:-2]:
                    shell = '\n' + shell

                if self.cos == 'default':
                    cos = uname()[0].lower()
                else:
                    cos = self.cos

                path = self.sessions[message.channel.id]
                username = getuser()
                system = uname()[1]
                if cos in self.os:
                    user = self.os[cos].format(
                        user=username, system=system, path=path)
                else:
                    user = self.os['linux'].format(user=username, system=system, path=path)

                result = []
                in_text = text = user + shell
                shorten_by = 12
                page_length = 2000
                num_mentions = text.count("@here") + text.count("@everyone")
                shorten_by += num_mentions
                page_length -= shorten_by
                while len(in_text) > page_length:
                    closest_delim = max([in_text.rfind(d, 0, page_length)
                                         for d in ["\n"]])
                    closest_delim = closest_delim if closest_delim != -1 else page_length
                    to_send = in_text[:closest_delim].replace(
                        "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
                    result.append(to_send)
                    in_text = in_text[closest_delim:]

                result.append(in_text.replace(
                    "@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))

                #result = list(pagify(user + shell, shorten_by=12))

                for num, output in enumerate(result):
                    if num % 1 == 0 and num != 0:

                        note = await message.channel.send('There are still {} pages left.\n'
                                                          'Type `more` to continue.'
                                                          ''.format(len(result) - (num+1)))

                        msg = await self.bot.wait_for('message',
                                                      check=lambda m:
                                                      m.channel == message.channel and
                                                      m.author == message.author and
                                                      m.content == 'more',
                                                      timeout=10)
                        try:
                            await note.delete()
                        except Exception:
                            pass

                        if msg is None:
                            return
                        else:
                            if output:
                                await message.channel.send('```Bash\n{}```'.format(output))
                    else:
                        if output:
                            await message.channel.send('```Bash\n{}```'.format(output))



def check_folder():
    if not exists(abspath(dirname(argv[0])) + '/settings/terminal'):
        print("[Terminal]Creating settings/terminal folder...")
        makedirs(abspath(dirname(argv[0])) + '/settings/terminal')

def check_file():
    jdict = {
        "prefix":">",
        "alias":{'alias example' : {'linux':'printf "Hello.\n'
                                            'This is a alias made using the magic of python."',
                                    'windows':'echo Hello. '
                                              'This is alias made using the magic of python.'}
                },
        "os":{
            'windows':'{path}>',
            'linux':'{user}@{system}:{path} $ '
            },
        "cos":"default",
        "enabled":True
        }

    if not dataIO.is_valid_json(abspath(dirname(argv[0])) + '/settings/terminal/settings.json') or  'cc' in dataIO.load_json(abspath(dirname(argv[0])) + '/settings/terminal/settings.json'):
        print("[Terminal]Creating default settings.json...")
        dataIO.save_json(abspath(dirname(argv[0])) + '/settings/terminal/settings.json', jdict)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Terminal(bot))
