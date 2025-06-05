import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Constants
IDEAS_CHANNEL_ID = 1362133312780632225
APPROVED_CHANNEL_ID = 1369097390153531422
JOEY_ID = 138094077584343040
MICHAH_ID = 377247197428842508
JACOB_ID = 248600684126011412

GREEN_SQUARE = "🟩"
GREEN_CHECK = "✅"

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store messages pending Joey's approval
pending_approval = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Ignore reactions from the bot itself
    if payload.user_id == bot.user.id:
        return

    # Only monitor reactions in the ideas channel
    if payload.channel_id != IDEAS_CHANNEL_ID:
        return

    emoji = str(payload.emoji)
    message_id = payload.message_id
    reactor_id = payload.user_id

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(message_id)

    # Step 1: Micah or Jacob adds a 🟩
    if emoji == GREEN_SQUARE and reactor_id in [MICHAH_ID, JACOB_ID]:
        if message_id not in pending_approval:
            pending_approval[message_id] = message
            joey = await bot.fetch_user(JOEY_ID)
            await joey.send(f"🟩 Headline for review:\n\"{message.content}\"")
            print(f"Sent message to Joey for review: {message.content}")

    # Step 2: Joey adds ✅
    elif emoji == GREEN_CHECK and reactor_id == JOEY_ID:
        if message_id in pending_approval:
            approved_channel = bot.get_channel(APPROVED_CHANNEL_ID)
            original_message = pending_approval.pop(message_id)
            await approved_channel.send(f"✅ **APPROVED HEADLINE:**\n{original_message.content}")
            author = await bot.fetch_user(original_message.author.id)
            await author.send("✅ Your headline has been approved! Time to write it up.")
            print(f"Headline approved and forwarded: {original_message.content}")

bot.run(TOKEN)
