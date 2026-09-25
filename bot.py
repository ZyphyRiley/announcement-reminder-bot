# bot.py
import os
from dotenv import load_dotenv
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ReminderBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = ReminderBot()

@bot.tree.command(
    name="reminder",
    description="Create a new reminder event."
)
@app_commands.describe(
    content="What are you reminding about?",
    deadline="Deadline in YYYY-MM-DD HH:MM format",
    before="How long before the deadline will the reminder send?",
    channel="Which channel to send this to?",
    role="Which role to send this reminder to?",
    link="Optional link"
)

async def reminder(
    interaction: discord.Interaction,
    content: str,
    deadline: str,
    before: str,
    channel: discord.TextChannel,
    role: discord.Role,
    link: str | None
):
    #TODO: convert the deadline str into a datetime object
    
    await interaction.response.send_message(
        f"Reminder created!\n"
        f"**{content}**\n"
        f"Deadline: {deadline}\n"
        f"Reminder: {before} before deadline\n"
        f"Channel: {channel}\n"
        f"Role: {role}\n"
        f"Link: {link or 'None'}"
    )

async def send_reminder(
    channel: discord.TextChannel,
    content: str,
    reminder_time: datetime,
    role: discord.Role,
    link: str | None
):
    
    message = f"{role.mention}: {content}"

    if link != None: # attach link if needed
        message = message + f"\n Link: {link}"

    await channel.send(message)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has successfully started")

bot.run(TOKEN)