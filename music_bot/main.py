import discord, os, asyncio
from discord.ext import commands

from cog_help import help_cog
from cog_music import music_cog

from decouple import config

TOKEN = config("TOKEN")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="./", intents=intents)

bot.remove_command("help")


async def load():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))


async def main():
    await load()
    await bot.start(TOKEN)


asyncio.run(main())
