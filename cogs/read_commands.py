import discord
from discord.ext import commands

from cogs.utils import cleanup
from cogs.easyocr import generate_csv, read_image, display_easyOCR


class ReadCommands(commands.Cog):

    """This class holds the logic for reading images."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Read'])
    async def read(self, ctx, mtgo=None):

        if mtgo == 'mtgo':
            mtgo_data = True
        else:
            mtgo_data = False
        
        """Takes in an image, reads it, and then spits out the csv."""
        try:
            image_url = ctx.message.attachments[0].url
            if image_url[0:26] == 'https://cdn.discordapp.com' and image_url.endswith(('.jpg','.png','.jpeg')):
                await ctx.send(embed=discord.Embed(
                    title=f"Success",
                    description="Your image will be read. Please wait.",
                    colour=discord.Color.blue()
                ))
                await ctx.message.attachments[0].save('image.png')
                read_image(mtgo_data)
                await ctx.send("I will now return your results.")
                await ctx.send(file=discord.File('image-displayed.png'))
                with open("output.csv", "rb") as file:
                    await ctx.send("Here is your CSV file.", file=discord.File(file, "output.csv"))
            else:
                await ctx.send(discord.Embed(
                    title=f"Error",
                    description="The attachment provided was not an image.",
                    colour=discord.Color.blue()
                ))
        except IndexError:
            await ctx.send(embed = discord.Embed(
                title=f"Error",
                description="No image attached.",
                colour=discord.Color.blue()
            ))


def setup(bot):
    bot.add_cog(ReadCommands(bot))