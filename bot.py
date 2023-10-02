import asyncio
import discord
from discord.ext import commands
from decouple import config


async def main():

    """This is the main method for the bot. It creates the bot,
    and loads in the commands and events from the cogs directory."""

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.remove_command("help")

    cogs = ['cogs.bot_events', 'cogs.bot_commands']

    for cog in cogs:
        await bot.load_extension(cog)

    await bot.start(config('BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
