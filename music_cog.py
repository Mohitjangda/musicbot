import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio
import random
import os
import json
import asyncio

cookies_file = 'cookies.txt'  # The Netscape format cookies file

ydl_opts = {
    'cookiefile': cookies_file,  # Specify your Netscape cookies file here
    'format': 'bestaudio/best',
    'noplaylist': True,
}

video_url = 'https://www.youtube.com/watch?v=M-P4QBt-FWw'  # Example URL

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False

        # Music queue and options
        self.music_queue = []
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        self.vc = None  # Voice client

        # Loop settings
        self.loop_mode = None  # None, "current", "queue"
        self.current_track = None

        # Playlist directory
        self.playlist_dir = "playlists/"
        if not os.path.exists(self.playlist_dir):
            os.makedirs(self.playlist_dir)  # Create the playlist directory if it doesn't exist

        # Cache for previously searched songs
        self.search_cache = {}

    def search_yt(self, item):
        """Search for a YouTube audio track and return its URL and title using cache."""
        # Check if the result is cached
        if item in self.search_cache:
            print(f"Found {item} in cache.")
            return self.search_cache[item]

        # If not in cache, search YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': '%(id)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
                song = {'source': info['url'], 'title': info['title']}
                # Cache the result for future use
                self.search_cache[item] = song
                print(f"Cached {item}.")
                return song
            except Exception as e:
                print(f"Error searching YouTube: {e}")
                return False
                
    async def play_music(self, ctx):
        """Play music from the queue."""
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.current_track = self.music_queue[0]
            m_url = self.music_queue[0]['source']

            if self.vc is None or not self.vc.is_connected():
                self.vc = await ctx.author.voice.channel.connect()

            self.music_queue.pop(0)
            await ctx.send(f"🎶 **Now playing:** {self.current_track['title']}")
            self.vc.play(FFmpegPCMAudio(m_url, **self.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        else:
            self.is_playing = False

    async def play_next(self, ctx):
        """Play the next song in the queue or handle loop modes."""
        if self.loop_mode == "current" and self.current_track:
            # Replay the current track
            self.music_queue.insert(0, self.current_track)
        elif self.loop_mode == "queue" and self.current_track:
            # Re-enqueue the current track
            self.music_queue.append(self.current_track)

        if len(self.music_queue) > 0:
            self.is_playing = True
            self.current_track = self.music_queue[0]
            m_url = self.music_queue[0]['source']
            self.music_queue.pop(0)
            await ctx.send(f"🎶 **Now playing:** {self.current_track['title']}")
            self.vc.play(FFmpegPCMAudio(m_url, **self.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        else:
            self.is_playing = False
            await ctx.send("❌ The queue is empty. No more songs to play.")

    @commands.command(name="play", aliases=["p"], help="Play a song from YouTube")
    async def play(self, ctx, *, query):
        """Add a song to the queue and play it if nothing is playing."""
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music!")
            return

        song = self.search_yt(query)
        if not song:
            await ctx.send("Could not find the song. Try a different keyword.")
        else:
            await ctx.send(f"🎶 **Added to queue:** {song['title']}")
            self.music_queue.append(song)

            if not self.is_playing:
                await self.play_music(ctx)

    @commands.command(name="skip", help="Skip the current song")
    async def skip(self, ctx):
        """Skip the current song."""
        if self.vc and self.vc.is_playing():
            self.vc.stop()
        else:
            await ctx.send("❌ No song is currently playing.")

    @commands.command(name="pause", help="Pause the current song")
    async def pause(self, ctx):
        """Pause the current song."""
        if self.vc and self.vc.is_playing():
            self.vc.pause()
            self.is_paused = True
            await ctx.send("⏸️ Paused the current song.")
        else:
            await ctx.send("❌ No song is currently playing.")

    @commands.command(name="resume", help="Resume the paused song")
    async def resume(self, ctx):
        """Resume the paused song."""
        if self.vc and self.is_paused:
            self.vc.resume()
            self.is_paused = False
            await ctx.send("▶️ Resumed the song.")
        else:
            await ctx.send("❌ No song is currently paused.")

    @commands.command(name="queue", help="Show the current song queue")
    async def queue(self, ctx):
        """Display the current music queue."""
        if len(self.music_queue) > 0:
            queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(self.music_queue)])
            await ctx.send(f"🎶 **Current Queue:**\n{queue_list}")
        else:
            await ctx.send("❌ The queue is empty.")

    @commands.command(name="clear", help="Clear the song queue")
    async def clear(self, ctx):
        """Clear the music queue."""
        self.music_queue.clear()
        await ctx.send("❌ The queue has been cleared.")

    @commands.command(name="loop", help="Set loop mode ('current', 'queue', or 'off')")
    async def loop(self, ctx, mode: str):
        """Set the loop mode."""
        mode = mode.lower()
        if mode == "current":
            self.loop_mode = "current"
            await ctx.send("🔂 Looping the current track.")
        elif mode == "queue":
            self.loop_mode = "queue"
            await ctx.send("🔁 Looping the entire queue.")
        elif mode == "off":
            self.loop_mode = None
            await ctx.send("❌ Looping disabled.")
        else:
            await ctx.send("❌ Invalid loop mode. Use 'current', 'queue', or 'off'.")

    @commands.command(name="playlist", help="Manage playlists (save/load/delete/list/add)")
    async def playlist(self, ctx, action: str, name: str = None):
        """Manage playlists."""
        if action == "save":
            if not name:
                await ctx.send("❌ Please provide a name for the playlist.")
                return
            playlist_path = os.path.join(self.playlist_dir, f"{name}.json")
            # Save the current queue to the playlist file
            with open(playlist_path, "w") as f:
                json.dump(self.music_queue, f)
            await ctx.send(f"✅ Playlist **{name}** saved.")

        elif action == "load":
            if not name:
                await ctx.send("❌ Please provide the name of the playlist to load.")
                return
            playlist_path = os.path.join(self.playlist_dir, f"{name}.json")
            if not os.path.exists(playlist_path):
                await ctx.send(f"❌ Playlist **{name}** not found.")
                return
            with open(playlist_path, "r") as f:
                loaded_queue = json.load(f)
                # Check if the playlist is valid (it should be a list of songs)
                if isinstance(loaded_queue, list):
                    self.music_queue.extend(loaded_queue)
                    await ctx.send(f"✅ Playlist **{name}** loaded into the queue.")
                    if not self.is_playing:
                        await self.play_music(ctx)  # Start playing the playlist
                else:
                    await ctx.send("❌ The playlist format is incorrect.")

        elif action == "delete":
            if not name:
                await ctx.send("❌ Please provide the name of the playlist to delete.")
                return
            playlist_path = os.path.join(self.playlist_dir, f"{name}.json")
            if not os.path.exists(playlist_path):
                await ctx.send(f"❌ Playlist **{name}** not found.")
                return
            os.remove(playlist_path)
            await ctx.send(f"✅ Playlist **{name}** deleted.")

        elif action == "list":
            playlists = [f[:-5] for f in os.listdir(self.playlist_dir) if f.endswith(".json")]
            if playlists:
                await ctx.send("🎵 **Saved Playlists:**\n" + "\n".join(playlists))
            else:
                await ctx.send("❌ No playlists found.")
        else:
            await ctx.send("❌ Invalid action. Use save, load, delete, or list.")

    @commands.command(name="shuffle", help="Shuffle the queue")
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        if len(self.music_queue) > 1:
            random.shuffle(self.music_queue)
            await ctx.send("🔀 Shuffled the queue.")
        else:
            await ctx.send("❌ Not enough songs in the queue to shuffle.")

    @bot.command()
async def join(ctx):
    # Check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return

    channel = ctx.author.voice.channel

    # Connect to the voice channel
    try:
        # Join the voice channel and establish the connection
        vc = await channel.connect()
        await ctx.send(f"Joined {channel.name} successfully!")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

    @bot.command()
async def leave(ctx):
    # Disconnect from the voice channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")
