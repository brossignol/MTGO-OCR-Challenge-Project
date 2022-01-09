import discord
from discord.ext import commands
from cogs.easyocr import run_easyocr


class ReadCommands(commands.Cog):

    """This class holds the logic for reading images."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Read', 'read'])
    async def read_standings(self, ctx):

        """This takes in the image for mtgo standings,
        and generates the csv for it."""
        try:
            image_url = ctx.message.attachments[0].url
            if (image_url[0:26] == 'https://cdn.discordapp.com' and
               image_url.endswith(('.jpg', '.png', '.jpeg'))):

                await ctx.send(embed=discord.Embed(
                    title="Success",
                    description="Your image will be read. Please wait.",
                    colour=discord.Color.blue()
                ))

                await ctx.message.attachments[0].save('image.png')
                await ctx.send("I will now return your results.")
                try:
                    results = await run_easyocr()
                    await ctx.send(results)
                except Exception as e:
                    await ctx.send("failed", str(e))
            else:
                await ctx.send(discord.Embed(
                    title="Error",
                    description="The attachment provided was not an image.",
                    colour=discord.Color.blue()
                ))
        except IndexError:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description="No image attached.",
                colour=discord.Color.blue()
            ))

    @commands.command(aliases=['Hello'])
    async def hello(self, ctx):

        """This takes in the image for mtgo standings,
        and generates the csv for it."""
        await ctx.send("hello")


def setup(bot):
    bot.add_cog(ReadCommands(bot))
