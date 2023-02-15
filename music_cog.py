import discord
from discord.ext import commands
import os
from youtube_dl import YoutubeDL



class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None
        self.m_url = ""

    def search_yt(self, item):
        with YoutubeDL(self. YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info('ytsearch:%s' % 
                                        item, download=False)['entries'][0]
            except Exception:
                    return False
            return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(self.m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.m_url = self.music_queue[0][0]['source']
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Could not connect to voice channel")
                    return
                else:
                    await self.vc.move_to(self.music_queue[0][1])
                self.music_queue.pop(0)
                self.vc.play(discord.FFmpegPCMAudio(self.m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            else:
                self.is_playing == False

    @commands.command(name='play', aliases=['p', 'find', 'f'], help='play song from yt')
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send('Please connect to a vc')
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not locate song, Incorrect format, try a different 'keyword'")
            else:
                await ctx.send('Song added to queue')
                self.music_queue.append([song, voice_channel])

            if self.is_playing == False:
                await self.play_music(ctx)

    @commands.command(name='pause', aliases=['pse', 'stop', 'wait'], help='Pauses current song')
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing == False
            self.is_paused == True
            self.vc.pause()
        else:
            await ctx.send('Music is already paused')

    @commands.command(name='resume', aliases=['res', 'r', 'cont', 'continue'], help='Resume current song')
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing == True
            self.is_paused == False
            self.vc.resume()
        elif len(self.music_queue) == 0:
            await ctx.send('Playlist is currently empty')

    @commands.command(name='skip', aliases=['s', 'kill', 'k', 'end'], help='Skip current song')
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)
        elif len(self.music_queue) == 0:
            await ctx.send('Playlist is currently empty')

    @commands.command(name='queue', aliases=['q', "que", 'playlist', 'list'], help='Show current playlist')
    async def queue(self, ctx, *args):
        return_val = ""

        for i in range(len(self.music_queue)):
            if i > 4:
                break
            return_val += self.music_queue[i][0]['title'] + '\n'

        if return_val != "":
            await ctx.send(return_val)
        else:
            await ctx.send('Playlist is currently empty')

    @commands.command(name='clear', aliases=['c', 'cl', 'killall', 'empty', 'e'], help='Clear existing playlist')
    async def clear(self, ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
            self.music_queue = []
            await ctx.send('Playlist cleared')
        else:
            await ctx.send('Playlist is currently empty')

    @commands.command(name='leave', aliases=['l', 'exit', 'disconnect', 'd'], help='Kick bot from vc')
    async def leave(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
        await ctx.send('See you later!')
