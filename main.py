import discord
from discord.ext import commands
from help_cog import help_cog
from music_cog import music_cog
import os
from dotenv import load_dotenv  # Import the dotenv module

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment variable
TOKEN = os.getenv("TOKEN")  # This will get the token from the .env file

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot with the command prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    """Load all cogs dynamically."""
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f"Logged in as {bot.user}")
    print("Bot is ready!")
    # Remove the default help command before loading cogs
    bot.remove_command("help")
    await load_cogs()

@bot.command(name="reload", help="Reload a specific cog.")
@commands.is_owner()  # Restrict to bot owner
async def reload(ctx, cog_name: str):
    """Reload a specific cog by its name."""
    try:
        if cog_name.lower() == "help_cog":
            await bot.remove_cog("help_cog")
            await bot.add_cog(help_cog(bot))
        elif cog_name.lower() == "music_cog":
            await bot.remove_cog("music_cog")
            await bot.add_cog(music_cog(bot))
        else:
            await ctx.send("❌ Invalid cog name. Use 'help_cog' or 'music_cog'.")
            return

        await ctx.send(f"✅ Reloaded **{cog_name}** successfully.")
    except Exception as e:
        await ctx.send(f"❌ Failed to reload **{cog_name}**. Error: {e}")

# Run the bot using the token from the .env file
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: Bot token not found. Please make sure the token is set in the .env file.")
