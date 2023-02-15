import discord
from discord.ext import commands
import os

from help_cog import help_cog
from music_cog import music_cog
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = True
intents.presences = True


bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)




@bot.event
async def on_ready():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))
bot.run(os.environ.get('TOKEN'))
