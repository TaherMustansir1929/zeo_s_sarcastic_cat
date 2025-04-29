import time
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from handlers.channel_restriction import channel_restriction_handler
from handlers.rate import rate_handler
from handlers.react import react_handler
from handlers.rizz import rizz_handler
from handlers.smart_ai import smart_ai_handler
from handlers.smart_ask import smart_ask_handler
from handlers.word_counter import word_counter_handler
from handlers.ask import ask_handler
from handlers.ai import ai_handler

# Dictionary to store chat history for each user
chat_histories_ai = {}
chat_histories_ask = {}

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

secret_role = "Developer"

@bot.event
async def on_ready():
    print(f"we are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.command(
    brief="Secret command. Beware."
)
async def secret(ctx):
    await ctx.send(f"Welcome to the club twin! There are no secrets here. Just be yourself and spread positivity. Luv you gng!🥀❤")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

# -------------------------------------------------------------------------------------
# -----------------------------MY CUSTOM COMMANDS--------------------------------------
# -------------------------------------------------------------------------------------

#---------AI CHATBOT COMMANDS-------
@bot.command(
    brief="Ask me any questions. Will reply respectfully",
    help="Ask me your stupid questions and Imma reply respectfully 😏🥀"
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def ask(ctx, *, msg):
    await ask_handler(ctx, msg)

@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
    await ctx.reply(f"Sorry an error occurred -> {error}")


@bot.command(
    brief="Spawns a dirty pickup line",
    help="Use this command to generate a dirty sus pickup line"
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def rizz(ctx):
    await rizz_handler(ctx)

@rizz.error
async def rizz_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
    await ctx.reply(f"Sorry an error occured -> {error}")

@bot.command(
    brief="Rates your pickup lines",
    help="Call this command along with your pickup line and it will rate is out of 10"
)
@commands.cooldown(1, 15, commands.BucketType.user)
async def rate(ctx, *, msg):
    await rate_handler(ctx, msg)

@rate.error
async def rate_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
    await ctx.reply(f"Sorry an error occured -> {error}")

#------WORD COUNTER FUNC-----------
@bot.event
async def on_message(message):
    await word_counter_handler(bot, message)
    await channel_restriction_handler(bot, message)

# ------------ Ping command -------------------------
@bot.command(
    brief="Checks the bot's latency.",
    help="Responds with 'Pong!' and the current latency in milliseconds."
)
async def ping(ctx: commands.Context):
    latency = round(bot.latency * 1000 * 10) # Latency in milliseconds
    await ctx.reply(f"Pong! 🏓 ({latency/10}ms)")

#----------Spam Messages-------------
@bot.command(
    hidden=True
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def spam_msg(ctx, *, msg):
    for i in range(10):
        await ctx.send(f"{msg}")
        time.sleep(0.5)

#-----------NORMAL LLM CHAT---------
@bot.command(
    brief="Talk to AI",
    help="Use this command to access an AI chatbot directly into the server."
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def ai(ctx, *, msg):
    await ai_handler(ctx, msg)

#-----------Smarter LLM CHAT with CHAT HISTORY---------
@bot.command(
    brief="Talk to a smarter AI with web search and chat history",
    help="Use this command to utilize !ai command with additional features like tooling, searching and chat history."
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def smart_ai(ctx, *, msg):
    await smart_ai_handler(ctx, msg, chat_histories_ai)

#-----------Smarter !ask command with CHAT HISTORY and SEARCH API---------
@bot.command(
    brief="Smarter implementation of !ask command",
    help="Use this command to access !ask command with additional features like tooling, searching and chat history."
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def smart_ask(ctx, *, msg):
    await smart_ask_handler(ctx, msg, chat_histories_ask)

#-----------REACT to the response given by !smart_ask command---------
@bot.command(
    brief="REACT to the response given by !smart_ask command",
    help="Use this command to react to the !smart_ask command with emojis"
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def react(ctx, *, msg):
    await react_handler(ctx, msg, chat_histories_ask)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
