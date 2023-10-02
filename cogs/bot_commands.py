import discord
from discord.ext import commands
from decouple import config
from cogs.ocr import display_output, run_async_easyocr, generate_csv
from cogs.sheetapi import load_csv_sheet, clear_sheet
from .fix_standings import fix_standings
from .ocr_multicolumn import run_easyocr_multi
from .utils import image_input_validation


class BotCommands(commands.Cog):

    """This class holds all of the current bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Read', 'read', 'R', 'r'])
    async def read_standings(self, ctx):
        """This takes in the image for mtgo standings,
        and generates the csv for it."""

        valid_input = await image_input_validation(ctx)
        if valid_input:
            await ctx.send(embed=discord.Embed(title='Success',
                                               description='Your image will be read. Please wait.',
                                               colour=discord.Color.blue()))
            results = await run_async_easyocr()
            generate_csv(results)
            display_output(results)
            clear_sheet()
            load_csv_sheet()
            await ctx.send("Here is what I found.")
            await ctx.send(file=discord.File('image-displayed.png'))
            await ctx.send(file=discord.File('output.csv'))
            embed = discord.Embed(
                title='Google Sheets Results',
                description=(f"Google sheet copy is available here: {config('DOCS_LINK')}" +
                             "\n\nYou can copy paste this into the data collection sheet." +
                             "\nNOTE: This google sheet will be overrided on the next call." +
                             "\nReview and copy the sheet before the next call, or use the csv."),
                colour=discord.Color.blue())
            file = discord.File("assets/google-sheets-logo.png")
            embed.set_thumbnail(url='attachment://google-sheets-logo.png')
            await ctx.send(embed=embed, file=file)

    @commands.command(aliases=['ReadFull', 'readfull'])
    async def read_full_standings(self, ctx):
        """This takes in the image for mtgo standings,
        and generates the csv for it."""
        valid_input = await image_input_validation(ctx)
        if valid_input:
            await ctx.send(embed=discord.Embed(
                title="Success",
                description="Your image will be read. Please wait.",
                colour=discord.Color.blue()
            ))
            await ctx.message.attachments[0].save('image.png')
            try:
                run_easyocr_multi()
                clear_sheet()
                load_csv_sheet()
                await ctx.send("Here is what I found.")
                await ctx.send(file=discord.File('image-displayed.png'))
                await ctx.send(file=discord.File('output.csv'))
                description = (f"Google sheet copy is available here: {config('DOCS_LINK')}" +
                               "\n\nYou can copy paste this into the data collection sheet." +
                               "\nNOTE: I may have missed the highlighted name in the image."
                               "\nPlease review before copying.")
                embed = discord.Embed(description=description, colour=discord.Color.blue())
                file = discord.File("assets/google-sheets-logo.png")
                embed.set_thumbnail(url='attachment://google-sheets-logo.png')
                await ctx.send(embed=embed, file=file)
            except Exception as e:
                await ctx.send("failed", str(e))

    @commands.command(aliases=['fix'])
    async def fix_full_standings(self, ctx):
        """This takes a link to the sheet wih standings, fix them and generates the csv for it."""
        url = ctx.message.content.strip().split(' ')[-1]
        if url[:39] == 'https://docs.google.com/spreadsheets/d/':
            await ctx.send(embed=discord.Embed(
                title="Success",
                description="Standings will be fixed. Please wait.",
                colour=discord.Color.blue()
            ))
            try:
                s = url.split('/')
                url = '/'.join(s[:-1]) + '/edit?usp=sharing'
                _, message = fix_standings(url)
                load_csv_sheet()
                if len(message) > 2000:
                    message = message[:2000 - 4] + '\n...'
                await ctx.send(message)
                await ctx.send(file=discord.File('output.csv'))
                description = (f"Google sheet copy is available here: {config('DOCS_LINK')}" +
                               "\n\nYou can copy paste this into the data collection sheet.")
                embed = discord.Embed(description=description, colour=discord.Color.blue())
                file = discord.File("assets/google-sheets-logo.png")
                embed.set_thumbnail(url='attachment://google-sheets-logo.png')
                await ctx.send(embed=embed, file=file)
            except Exception as e:
                await ctx.send("failed", str(e))
        else:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description="The link is not valid",
                colour=discord.Color.blue()
            ))

    @commands.command(aliases=['help', 'Help'])
    async def help_command(self, ctx, command: str = "default"):

        """displays how to use each command for the bot.
        By default the value is the default help command"""

        try:
            fileName = f"{command.lower()}.txt"
            with open(f"helpCommands/{fileName}", "r") as f:
                help_message = ''.join(f.readlines())
        except FileNotFoundError:
            help_message = "No command found."

        # use embed discord styling for nicer display
        embed = discord.Embed(
            title=f"How to use: {command}" if command != "default" else "How to use me",
            description=help_message,
            colour=discord.Color.blue())

        if command.lower() == 'read':
            file = discord.File("assets/example-image.png")
            embed.set_thumbnail(url='attachment://example-image.png')
            await ctx.author.send(embed=embed, file=file)
        else:
            await ctx.author.send(embed=embed)

    @commands.command(aliases=['Code'])
    async def code(self, ctx):
        embed = discord.Embed(
            title='My Source Code!',
            description=('You can find my source code here:' +
                         'https://github.com/Raptor56MTG/MTGO-OCR-Challenge-Project'),
            colour=discord.Color.blue()
        )
        file = discord.File("assets/github-logo.png")
        embed.set_thumbnail(url='attachment://github-logo.png')
        await ctx.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(BotCommands(bot))
