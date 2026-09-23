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
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = ReminderBot()

@bot.tree.command(
    name="reminder"
    description="Create a new reminder event."
)
@app_commands.describe(
    content="What are you reminding about?",
    deadline="Deadline in YYYY-MM-DD HH:MM format",
    before="How long before the deadline will the reminder send?",
    role="Which role to send this reminder to?"
    link="Optional link"
)

async def reminder(
    interaction: discord.Interaction,
    content: str,
    deadline: str,
    before: str,
    role: str,
    link: str | None
):
    await interaction.response.send_message(
        f"Reminder created!\n"
        f"**{content}**\n"
        f"Deadline: {deadline}\n"
        f"Reminder: {before} before deadline\n"
        f"Role: {role}\n"
        f"Link: {link or 'None'}"
    )

bot.run(TOKEN)