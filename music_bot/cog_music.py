import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)[
                    "entries"
                ][0]
            except Exception:
                return False
        return {"source": info["formats"][0]["url"], "title": info["title"]}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            self.music_queue.pop(0)

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]["source"]

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
        else:
            self.is_playing = False

    @commands.command(
        name="play", aliases=["p", "playing"], help="Plays a selected song from youtube"
    )
    async def play(self, ctx, *args):
        query = " ".join(args)
        print(query, self, args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Could not download the song. Incorrect format, try another keyword"
                )
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song from youtube")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc_pause()
        elif self.is_paused:
            self.vc.resume()

    @commands.command(name="resume", help="Resumes the current song from youtube")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", help="Skips the current song from youtube")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="clear", help="Clears the current song from youtube")
    async def clear(self, ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Queue cleared")

    @commands.command(name="leave", help="Leaves the current song from youtube")
    async def leave(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="test", help="Leaves the current song from youtube")
    async def test(self, ctx):
        await ctx.send(self.bot.get_user)
        await ctx.send(self)

    @commands.command(name="queue", help="Skips the current song from youtube")
    async def queue(self, ctx, *args):
        retval = ""

        for i in range(0, len(self.music_queue)):
            if i > 4:
                break
            retval += self.music_queue[i][0]["title"] + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")
