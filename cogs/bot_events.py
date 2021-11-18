import discord
from discord.ext import commands


class BotEvents(commands.Cog):

    """This class holds all things related to bot events."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        """Message the bot sends on startup"""

        print("I am ready to read images!")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        """Handles various errors for user input."""

        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(description="This command does not exist.",
                                  colour=discord.Color.blue())
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description="Missing required arguments. Use the !help command.",
                                  colour=discord.Color.blue())
            await ctx.send(embed=embed)

        else:
            # print(error)  # used for debugbing / testing
            return  # silent failure for anything else.





def setup(bot):
    bot.add_cog(BotEvents(bot))
