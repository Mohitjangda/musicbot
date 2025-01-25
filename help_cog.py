import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Help message with all available commands
        self.help_message = (
            "```\n"
            "General commands:\n"
            "!play <song> - Plays a song from YouTube\n"
            "!pause - Pauses the current song\n"
            "!resume - Resumes the paused song\n"
            "!skip - Skips the current song\n"
            "!queue - Displays the current song queue\n"
            "!clear - Clears the song queue\n"
            "!leave - Disconnects the bot from the voice channel\n"
            "!loop <mode> - Set loop mode ('current', 'queue', or 'off')\n"
            "!playlist <action> <name> - Manage playlists (save/load/delete/list/add)\n"
            "!shuffle - Shuffle the queue\n"
            "```"
        )

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        """Override the default help command to display custom message."""
        await ctx.send(self.help_message)

    @commands.Cog.listener()
    async def on_ready(self):
        """Listener that sends the help message once the bot is ready."""
        print("Help cog loaded and ready!")

