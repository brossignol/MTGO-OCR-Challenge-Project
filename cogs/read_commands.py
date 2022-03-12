import discord
from discord.ext import commands
from decouple import config
from cogs.ocr import display_output, run_easyocr, generate_csv
from cogs.sheetapi import load_csv_sheet, clear_sheet


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
                try:
                    results = run_easyocr()
                    generate_csv(results)
                    display_output(results)
                    clear_sheet()
                    load_csv_sheet()
                    await ctx.send("Here is what I found.")
                    await ctx.send(file=discord.File('image-displayed.png'))
                    await ctx.send(file=discord.File('output.csv'))
                    description = (f"Google sheet copy is available here: {config('DOCS_LINK')}" +
                                   "\n\nYou can copy paste this into the data collection sheet." +
                                   "\nNOTE: I am likely missing the highlighted name in the image."
                                   "\nPlease make sure to add that before copying.")
                    embed = discord.Embed(description=description, colour=discord.Color.blue())
                    await ctx.send(embed=embed)
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


def setup(bot):
    bot.add_cog(ReadCommands(bot))
