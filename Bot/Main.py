import discord
import jellyfin_apiclient_python
from discord.ext import commands
from discord_slash import SlashCommand

# Set up bot prefix and description
bot_prefix = "!"
bot_description = "A discord bot that can play movies and tv shows from jellyfin in discord vc."

# Create bot instance and slash command instance
intents = discord.Intents.default()
intents.typing = False
bot = commands.Bot(command_prefix=bot_prefix, description=bot_description, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Jellyfin API configuration
jellyfin_base_url = "http(s)://yourjellyfininstance.com"
jellyfin_api_key = "YourJellyfinApiKey"

# Create a Jellyfin API client
jellyfin_client = jellyfin_apiclient_python.JellyfinClient()

# Set configuration values
jellyfin_client.config.app('your_brilliant_app', '0.0.1', 'machine_name', 'unique_id')
jellyfin_client.config.data["auth.ssl"] = True

# Authenticating to a server
jellyfin_client.auth.connect_to_address(jellyfin_base_url)
jellyfin_client.auth.login(jellyfin_base_url, 'Diego', '71011')

# Voice client
voice_clients = {}

# Slash Command: Join voice channel
@slash.slash(name="join-voice", description="Join a voice channel", options=[{"name": "vc_name", "description": "Name of the voice channel", "type": 3, "required": True}])
async def join_voice(ctx, vc_name: str):
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel.")
        return
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name=vc_name)
    if voice_channel is None:
        await ctx.send(f"Voice channel '{vc_name}' not found.")
        return
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(voice_channel)
    else:
        voice_clients[ctx.guild.id] = await voice_channel.connect()
        await ctx.send(f"Joined voice channel '{vc_name}'.")

# Slash Command: Search and play media
@slash.slash(name="search", description="Search and play media", options=[{"name": "keyword", "description": "Keyword to search media", "type": 3, "required": True}])
async def search(ctx, keyword: str):
    await join_voice(ctx, vc_name=ctx.author.voice.channel.name)

    # Search for media in Jellyfin API (case-insensitive)
    search_results = jellyfin_client.search_items(keyword)

    if not search_results:
        await ctx.send("Media not found or an error occurred.")
        return
    
    media_data = search_results[0]
    media_url = f"{jellyfin_base_url}/{media_data['MediaSources'][0]['Path']}"

    # Play media
    voice_client = voice_clients.get(ctx.guild.id)
    if voice_client.is_playing():
        voice_client.stop()
    try:
        voice_client.play(discord.FFmpegPCMAudio(media_url))
        await ctx.send(f"Now playing: {media_data['Name']} in {voice_client.channel.name}")
    except Exception as e:
        await ctx.send(f"An error occurred while playing the media: {e}")

# Run the bot with your token
bot.run("(TOKEN GO HERE)")
