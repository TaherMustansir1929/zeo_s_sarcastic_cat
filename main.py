# Importing libraries and modules
import asyncio  # NEW
import logging
import os
import platform  # MOVED FROM play_next_song
from collections import deque  # NEW

import discord
import yt_dlp  # NEW
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from handlers.ai import ai_handler
from handlers.ask import ask_handler
from handlers.channel_restriction import channel_restriction_handler
from handlers.poetry import poetry_handler
from handlers.rate import rate_handler
from handlers.react import react_handler
from handlers.rizz import rizz_handler
from handlers.word_counter import word_counter_handler

# Dictionary to store chat history for each user
chat_histories_google_sdk = {}
chat_histories_ai_google_sdk = {}
chat_histories_poetry = {}

# Configure discord.py logging level to INFO to avoid excessive DEBUG logs
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.WARNING)

# Configure root logger to prevent *any* default console output
root_logger = logging.getLogger()
# Remove existing handlers (like the default StreamHandler to console)
for h in root_logger.handlers[:]:
    root_logger.removeHandler(h)
# Set level high to prevent processing unless specific handlers are added
root_logger.setLevel(logging.CRITICAL)

# The FileHandler below will still work if added to a specific logger or the root logger later.

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

secret_role = "Developer"


@bot.event
async def on_ready():
    await bot.tree.sync()
    if bot.user is not None:
        print(f"we are ready to go in, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


@bot.command(brief="Secret command. Beware.")
async def secret(ctx):
    await ctx.send(
        "Welcome to the club twin! There are no secrets here. Just be yourself and spread positivity. Luv you gng!🥀❤"
    )


@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")


# -------------------------------------------------------------------------------------
# -----------------------------MY CUSTOM COMMANDS--------------------------------------
# -------------------------------------------------------------------------------------


# ---------SARCASTIC AI COMMANDS-------
@bot.command(
    brief="Ask me your stupid questions and Imma reply respectfully 😏🥀",
    help="Ask me your stupid questions and Imma reply respectfully 😏🥀",
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def ask(ctx, *, msg):
    await ask_handler(ctx, msg, chat_histories_google_sdk)


@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(
            f"Please wait {error.retry_after:.2f} seconds before using this command again."
        )
    await ctx.reply(f"Sorry an error occurred -> {error}")


# ---------RIZZ COMMAND-------
@bot.command(
    brief="Spawns a dirty pickup line",
    help="Use this command to generate a dirty sus pickup line",
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def rizz(ctx):
    await rizz_handler(ctx)


@rizz.error
async def rizz_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Please wait {error.retry_after:.2f} seconds before using this command again."
        )
    await ctx.reply(f"Sorry an error occured -> {error}")


# ---------PICKUP LINE RATING COMMAND-------
@bot.command(
    brief="Rates your pickup lines",
    help="Call this command along with your pickup line and it will rate is out of 10",
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def rate(ctx, *, msg):
    await rate_handler(ctx, msg)


@rate.error
async def rate_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Please wait {error.retry_after:.2f} seconds before using this command again."
        )
    await ctx.reply(f"Sorry an error occured -> {error}")


# ------WORD COUNTER FUNC-----------
@bot.event
async def on_message(message):
    await word_counter_handler(bot, message)
    await channel_restriction_handler(bot, message)


# ------------ Ping command -------------------------
@bot.command(
    brief="Checks the bot's latency.",
    help="Responds with 'Pong!' and the current latency in milliseconds.",
)
async def ping(ctx: commands.Context):
    latency = round(bot.latency * 1000 * 10)  # Latency in milliseconds
    await ctx.reply(f"Pong! 🏓 ({latency / 10}ms)")


# ----------Spam Messages-------------
@bot.command(hidden=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def spam_msg(ctx, *, msg):
    for _ in range(10):  # Use _ for unused variable
        await ctx.send(f"{msg}")
        await asyncio.sleep(0.5)  # Use asyncio.sleep in async function


# -----------NORMAL LLM CHAT---------
@bot.command(
    brief="Talk to AI",
    help="Use this command to access an AI chatbot directly into the server.",
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def ai(ctx, *, msg):
    await ai_handler(ctx, msg, chat_histories_ai_google_sdk)


# -----------REACT to the response given by !smart_ask command---------
@bot.command(
    brief="REACT to the response given by !smart_ask command",
    help="Use this command to react to the !smart_ask command with emojis",
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def react(ctx, *, msg):
    await react_handler(ctx, msg, chat_histories_google_sdk)


# -----------URDU POETRY COMMAND(SPECIAL)------------------------------
@bot.command(
    brief="Get a beautiful piece of Urdu shayri",
    help="Use this command to generate a piece of Urdu poetry based on your chosen topic",
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def poetry(ctx, *, msg):
    await poetry_handler(ctx, msg, chat_histories_poetry)


@poetry.error
async def poetry_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Please wait {error.retry_after:.2f} seconds before using this command again."
        )
    await ctx.reply(f"Sorry an error occured -> {error}")


# ------------------------------------------------------------
# ---------------SONG BOT COMMANDS----------------------------
# ------------------------------------------------------------

GUILD_ID = 915624069829918741

SONG_QUEUES = {}


async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))


def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)


@bot.tree.command(name="skip", description="Skips the current playing song")
async def skip(interaction: discord.Interaction):
    if interaction.guild is not None:
        if interaction.guild.voice_client and (
            interaction.guild.voice_client.is_playing()
            or interaction.guild.voice_client.is_paused()
        ):
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped the current song.")
        else:
            await interaction.response.send_message("Not playing anything to skip.")


@bot.tree.command(name="pause", description="Pause the currently playing song.")
async def pause(interaction: discord.Interaction):
    if interaction.guild is not None:
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            return await interaction.response.send_message(
                "I'm not in a voice channel."
            )

        # Check if something is actually playing
        if not voice_client.is_playing():
            return await interaction.response.send_message(
                "Nothing is currently playing."
            )

        # Pause the track
        voice_client.pause()
        await interaction.response.send_message("Playback paused!")


@bot.tree.command(name="resume", description="Resume the currently paused song.")
async def resume(interaction: discord.Interaction):
    if interaction.guild is not None:
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            return await interaction.response.send_message(
                "I'm not in a voice channel."
            )

        # Check if it's actually paused
        if not voice_client.is_paused():
            return await interaction.response.send_message("I’m not paused right now.")

        # Resume playback
        voice_client.resume()
    await interaction.response.send_message("Playback resumed!")


@bot.tree.command(name="stop", description="Stop playback and clear the queue.")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if not voice_client or not voice_client.is_connected():
        return await interaction.response.send_message(
            "I'm not connected to any voice channel."
        )

    # Clear the guild's queue
    guild_id_str = str(interaction.guild_id)
    if guild_id_str in SONG_QUEUES:
        SONG_QUEUES[guild_id_str].clear()

    # If something is playing or paused, stop it
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    # (Optional) Disconnect from the channel
    await voice_client.disconnect()

    await interaction.response.send_message("Stopped playback and disconnected!")


@bot.tree.command(name="play", description="Play a song or add it to the queue.")
@app_commands.describe(song_query="Search query")
async def play(interaction: discord.Interaction, song_query: str):
    # Defer response immediately
    await interaction.response.defer()
    print(
        f"[{interaction.guild.id}] Received /play command for: '{song_query}' by {interaction.user}"
    )  # LOGGING

    # Check user voice state
    if not interaction.user.voice or not interaction.user.voice.channel:
        print(
            f"[{interaction.guild.id}] User {interaction.user} not in a voice channel."
        )  # LOGGING
        await interaction.followup.send(
            "You must be in a voice channel to use this command."
        )
        return
    voice_channel = interaction.user.voice.channel

    # Get or connect voice client
    voice_client = interaction.guild.voice_client
    try:
        if voice_client is None:
            print(
                f"[{interaction.guild.id}] Connecting to voice channel: {voice_channel.name} ({voice_channel.id})"
            )  # LOGGING
            voice_client = await voice_channel.connect(
                timeout=30.0, reconnect=True
            )  # Add timeout
            print(f"[{interaction.guild.id}] Connected successfully.")  # LOGGING
        elif voice_client.channel != voice_channel:
            print(
                f"[{interaction.guild.id}] Moving to voice channel: {voice_channel.name} ({voice_channel.id})"
            )  # LOGGING
            await voice_client.move_to(voice_channel)
            print(f"[{interaction.guild.id}] Moved successfully.")  # LOGGING
        # If already connected to the correct channel, do nothing
        elif not voice_client.is_connected():  # Check if disconnected unexpectedly
            print(
                f"[{interaction.guild.id}] Reconnecting to voice channel: {voice_channel.name} ({voice_channel.id})"
            )  # LOGGING
            voice_client = await voice_channel.connect(timeout=30.0, reconnect=True)
            print(f"[{interaction.guild.id}] Reconnected successfully.")  # LOGGING

    except asyncio.TimeoutError:
        print(
            f"[{interaction.guild.id}] Timeout connecting/moving to voice channel {voice_channel.name}."
        )  # LOGGING
        await interaction.followup.send(
            f"Timed out trying to connect to {voice_channel.name}."
        )
        return
    except Exception as e:
        print(
            f"[{interaction.guild.id}] Error connecting/moving to voice channel {voice_channel.name}: {e}"
        )  # LOGGING
        await interaction.followup.send(
            f"Failed to connect or move to {voice_channel.name}: {type(e).__name__}."
        )
        return

    # --- Search for the song ---
    ydl_options = {
        "format": "bestaudio[abr<=96]/bestaudio/best",  # Added /best fallback
        "noplaylist": True,
        # "youtube_include_dash_manifest": False, # Keep defaults
        # "youtube_include_hls_manifest": False, # Keep defaults
        "default_search": "ytsearch1",
        "quiet": True,  # Suppress yt-dlp console output
        "no_warnings": True,
        # "extract_flat": "discard_in_playlist", # REMOVED
        # "lazy_playlist": True, # REMOVED
        "source_address": "0.0.0.0",  # Added source address binding hint
    }

    print(f"[{interaction.guild.id}] Searching yt-dlp for: '{song_query}'")  # LOGGING
    results = None
    try:
        # Run synchronous blocking IO in executor
        results = await search_ytdlp_async(song_query, ydl_options)
        print(f"[{interaction.guild.id}] yt-dlp search finished.")  # LOGGING
    except yt_dlp.utils.DownloadError as e:
        print(f"[{interaction.guild.id}] yt-dlp DownloadError: {e}")  # LOGGING
        await interaction.followup.send(
            f"Couldn't find anything matching '{song_query}'. Please try different keywords."
        )
        return
    except Exception as e:
        print(
            f"[{interaction.guild.id}] Error during yt-dlp search: {type(e).__name__}: {e}"
        )  # LOGGING
        await interaction.followup.send(
            "An error occurred while searching for the song."
        )
        return  # Stop execution if search fails

    # --- Process search results ---
    if not results or not results.get("entries"):
        print(
            f"[{interaction.guild.id}] No results found for: '{song_query}'"
        )  # LOGGING
        await interaction.followup.send(
            f"Couldn't find anything matching '{song_query}'."
        )
        return

    # Get the first actual video entry
    first_track = None
    for entry in results["entries"]:
        if entry and entry.get("url"):  # Ensure entry exists and has a URL
            first_track = entry
            break

    if not first_track:
        print(
            f"[{interaction.guild.id}] No playable video found in search results for: '{song_query}'"
        )  # LOGGING
        await interaction.followup.send(
            f"Couldn't find a playable video for '{song_query}'."
        )
        return

    audio_url = first_track.get("url")  # Use .get for safety
    title = first_track.get("title", "Untitled")
    # duration = first_track.get("duration")  # Optional: get duration
    # thumbnail = first_track.get("thumbnail")  # Optional: get thumbnail

    # Check if URL was extracted
    if not audio_url:
        print(
            f"[{interaction.guild.id}] Failed to extract URL via yt-dlp for '{title}'."
        )  # LOGGING
        await interaction.followup.send(
            f"Error: Could not extract a playable URL for '{title}'."
        )
        return  # Stop if no URL

    print(
        f"[{interaction.guild.id}] Found track: '{title}'"
    )  # LOGGING (Removed URL from log)

    # --- Add to queue ---
    guild_id = str(interaction.guild.id)  # Use guild ID as string key
    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()
        print(f"[{guild_id}] Created new song queue.")  # LOGGING

    # Store more info if needed (e.g., title, requester)
    song_data = {
        "url": audio_url,
        "title": title,
        "requester": interaction.user.mention,
    }
    SONG_QUEUES[guild_id].append(song_data)
    queue_position = len(SONG_QUEUES[guild_id])
    print(
        f"[{guild_id}] Added '{title}' to queue at position {queue_position}. Queue size: {queue_position}"
    )  # LOGGING

    # --- Respond and start playback if needed ---
    if voice_client.is_playing() or voice_client.is_paused():
        print(
            f"[{guild_id}] Sending 'Added to queue' message for '{title}'."
        )  # LOGGING
        await interaction.followup.send(
            f"✅ Added to queue: **{title}** (Position: {queue_position})"
        )
    else:
        # Don't send a message here, play_next_song will handle it
        print(
            f"[{guild_id}] Calling play_next_song to start playback immediately."
        )  # LOGGING
        # Pass interaction ONLY for the initial followup message capability
        await play_next_song(voice_client, guild_id, interaction.channel, interaction)


# Modified play_next_song to accept optional interaction for initial message
async def play_next_song(
    voice_client, guild_id, channel, interaction: discord.Interaction = None
):
    guild_id = str(guild_id)  # Ensure guild_id is string
    print(
        f"[{guild_id}] play_next_song triggered. Interaction provided: {interaction is not None}"
    )  # LOGGING

    # Check voice client validity
    if not voice_client or not voice_client.is_connected():
        print(
            f"[{guild_id}] play_next_song: Voice client invalid or disconnected. Clearing queue."
        )  # LOGGING
        if guild_id in SONG_QUEUES:
            SONG_QUEUES[guild_id].clear()
        return

    # Check if already playing (shouldn't happen with `after` callback, but safety check)
    if voice_client.is_playing():
        print(f"[{guild_id}] play_next_song: Already playing. Exiting.")  # LOGGING
        return

    # Check queue status
    if guild_id not in SONG_QUEUES or not SONG_QUEUES[guild_id]:
        print(f"[{guild_id}] play_next_song: Queue is empty.")  # LOGGING
        # Optional: Add a delay before disconnecting
        # await asyncio.sleep(60)
        if voice_client.is_connected():
            print(
                f"[{guild_id}] play_next_song: Disconnecting due to empty queue."
            )  # LOGGING
            # await channel.send("🏁 Queue finished. Leaving voice channel.") # Optional message
            await voice_client.disconnect()
        # Clean up queue just in case
        if guild_id in SONG_QUEUES:
            del SONG_QUEUES[guild_id]
        return

    # --- Queue has items, proceed with playback ---
    current_loop = asyncio.get_running_loop()  # Get loop here
    song_data = SONG_QUEUES[guild_id].popleft()
    title = song_data["title"]
    audio_url = song_data["url"]
    requester = song_data["requester"]
    print(
        f"[{guild_id}] play_next_song: Popped '{title}' requested by {requester}. Queue size: {len(SONG_QUEUES.get(guild_id, []))}"
    )  # LOGGING

    # --- Prepare FFmpeg ---
    # Simplify FFmpeg options - remove loudnorm for now
    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
        "options": "-vn -c:a libopus -b:a 96k",  # Simpler options
    }
    # Imports moved to top (platform added, os/asyncio already there)

    executable_path = "ffmpeg"  # Default to system ffmpeg
    bundled_ffmpeg_path = os.path.join("bin", "ffmpeg", "ffmpeg")  # Base path
    if platform.system() == "Windows":
        bundled_ffmpeg_path += ".exe"

    if os.path.exists(bundled_ffmpeg_path):
        executable_path = bundled_ffmpeg_path
        print(
            f"[{guild_id}] play_next_song: Using bundled ffmpeg: {executable_path}"
        )  # LOGGING
    else:
        print(
            f"[{guild_id}] play_next_song: Using system ffmpeg (assuming in PATH)."
        )  # LOGGING

    # --- Create Audio Source ---
    source = None
    # --- Create Audio Source ---
    print(
        f"[{guild_id}] play_next_song: Creating FFmpegOpusAudio source for '{title}'."
    )  # LOGGING (Removed extra logs)
    source = None
    try:
        source = discord.FFmpegOpusAudio(
            source=audio_url, executable=executable_path, **ffmpeg_options
        )
        # Removed success log here
    except Exception as e:
        print(
            f"[{guild_id}] play_next_song: Error creating FFmpeg source for '{title}': {type(e).__name__}: {e}"
        )  # LOGGING
        await channel.send(f"⚠️ Error loading '{title}'. Skipping.")
        # Schedule next song check immediately using create_task
        print(
            f"[{guild_id}] play_next_song: Scheduling next song check after source error."
        )  # LOGGING
        current_loop.create_task(play_next_song(voice_client, guild_id, channel))
        return

    # --- Define After Callback ---
    def after_play_callback(error):
        if error:
            print(
                f"[{guild_id}] play_next_song: Error during playback of '{title}': {error}"
            )  # LOGGING
            # Optionally notify channel about playback error
            # coro = channel.send(f"⚠️ Error playing '{title}': {error}")
            # asyncio.run_coroutine_threadsafe(coro, current_loop)
        else:
            print(
                f"[{guild_id}] play_next_song: Finished playing '{title}'."
            )  # LOGGING
        # Schedule the next song check regardless of error
        print(
            f"[{guild_id}] play_next_song: Scheduling next song check in after_play_callback."
        )  # LOGGING
        # Use run_coroutine_threadsafe as 'after' runs in a separate thread
        asyncio.run_coroutine_threadsafe(
            play_next_song(voice_client, guild_id, channel), current_loop
        )

    # --- Start Playback ---
    # Removed BEFORE log
    try:
        if not voice_client.is_connected():
            print(
                f"[{guild_id}] play_next_song: Voice client disconnected before playback could start. Aborting play."
            )  # LOGGING
            # Don't try to play, let the next check handle it if queue still has items
            if guild_id in SONG_QUEUES:
                SONG_QUEUES[guild_id].appendleft(song_data)  # Put song back
            # Schedule check immediately
            current_loop.create_task(play_next_song(voice_client, guild_id, channel))
            return

        voice_client.play(source, after=after_play_callback)
        # Removed AFTER log

        # Send "Now playing" message - use interaction.followup if available (initial play), else channel.send
        now_playing_message = f"▶️ Now playing: **{title}** (Requested by: {requester})"
        if interaction:
            print(
                f"[{guild_id}] play_next_song: Sending initial followup message for '{title}'."
            )  # LOGGING
            await interaction.followup.send(now_playing_message)
        else:
            print(
                f"[{guild_id}] play_next_song: Sending channel message for '{title}'."
            )  # LOGGING
            await channel.send(now_playing_message)

    except discord.ClientException as e:
        # This exception might occur if already playing, though we check above.
        print(
            f"[{guild_id}] play_next_song: Error starting playback (ClientException) for '{title}': {e}"
        )  # LOGGING
        await channel.send(f"⚠️ Error playing '{title}' (ClientException). Skipping.")
        print(
            f"[{guild_id}] play_next_song: Scheduling next song check after ClientException."
        )  # LOGGING
        current_loop.create_task(play_next_song(voice_client, guild_id, channel))
    except Exception as e:
        print(
            f"[{guild_id}] play_next_song: Generic error starting playback for '{title}': {type(e).__name__}: {e}"
        )  # LOGGING
        await channel.send(
            f"⚠️ An unexpected error occurred while trying to play '{title}'. Skipping."
        )
        print(
            f"[{guild_id}] play_next_song: Scheduling next song check after generic error."
        )  # LOGGING
        current_loop.create_task(play_next_song(voice_client, guild_id, channel))


# Removed redundant queue handling at the end


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
