import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
General commands:
!help - display all commands
!p <keyword> - play requested song
!pse - pause current song
!r - resume current song
!s - skips current song
!c - clears entire playlist
!l - force bot to leave vc

```
"""
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for channel in self.text_channel_text:
            await channel.send(msg)

    @commands.command(name='help', aliases=['h', '?'], help="Display available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)
