from discord.ext import commands
import time
import sys
import subprocess
import os


class Restart:
    """Cog to restart the bot without the need of any special tools."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def restart(self, ctx):
        """Attempts to restart Appus Selfbot
        Makes it attempt to start a new instance of red
        and then exit itself."""

        await self.bot.say("Do you really want to restart? (yes/no)")
        answer = await self.bot.wait_for_message(timeout=10,
                                                 author=ctx.message.author)

        if answer == None:
            await self.bot.say("Canceling restart...")

        elif answer.content.lower().strip() == "yes":
            await self.bot.say("Restarting now.")
            print("Restarting Red...")
            time.sleep(1)
            try:
                cd = "{}".format(" ".join(sys.argv))
            except:
                if len(sys.argv) < 2:
                    cd = "{}/{}".format(os.getcwd(), sys.argv[0])
                else:
                    cd = "{}/{} {}".format(os.getcwd(), sys.argv[0], sys.argv[1])
            child = subprocess.Popen(["{} {}".format(sys.executable, cd)],shell=True,stdout=subprocess.PIPE)
            output,error = child.communicate()
            print("Output\n{}\nError\n{}\n".format(output, error))
            sys.exit()

        else:
            await self.bot.say("Canceling restart...")

    def __unload(self):
        if oldrestart:
            print('Restoring old restart command')
            self.bot.add_command(oldrestart)

def setup(bot):

    global oldrestart
    oldrestart = bot.get_command("restart")

    if oldrestart:
        print('Replacing old restart command (restores on unload)')
        bot.remove_command(oldrestart.name)

    bot.add_cog(Restart(bot))
