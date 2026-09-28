# bot.py
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import random

import discord
from discord import app_commands
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient

from helper import parse_duration

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

cluster = MongoClient(MONGO_URI)
db = cluster["announcement-reminders"]
collection = db["reminders"]

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
    print("Trying reminder")

    try:
        deadline_dt = datetime.strptime( # TODO: check that deadline isn't before current time
            deadline,
            "%Y-%m-%d %H:%M"
        )
        print(deadline_dt)

        time_before_reminder = parse_duration(before)
        print(time_before_reminder)

        reminder_time = deadline_dt - time_before_reminder
        print(reminder_time)

    except ValueError:
        await interaction.response.send_message(
            "Invalid deadline or time before reminder format.",
            ephemeral=True
        )
        return

    result = {
        "_id": random.random(),
        "content": content,
        "send_time": reminder_time,
        "channel": str(channel), # gets rid of the hashtag before
        "role": str(role), # keeps the @ sign
        "sent": False
    }

    if link:
        result["link"] = link

    collection.insert_one(result)
    
    await interaction.response.send_message(
        f"Reminder created!\n"
        f"*{content}*\n"
        f"Deadline: {deadline}\n"
        f"Reminder: {before} before deadline\n"
        f"Channel: {channel}\n"
        f"Role: {role}\n"
        f"Link: {link or 'None'}",
        ephemeral=True
    )

async def send_reminder(reminder):

    #channel: discord.TextChannel,
        # content: str,
        # reminder_time: datetime,
        # role: discord.Role,
        # link: str | None

    channel: discord.TextChannel = reminder['channel']
    
    message = f"{reminder['role']}: {reminder['content']}"

    if reminder.get('link'):
        message += f"\nLink: {reminder['link']}"

    await channel.send(message)

    await collection.update_one(
        {"_id": reminder["_id"]},
        {"$set": {"sent": True}}
    )

@tasks.loop(seconds=10)
async def reminder_scheduler():
    now = datetime.now(timezone.utc)

    cursor = collection.find({
        "reminder_time": {"$lte": now},
        "sent": False
    })

    async for reminder in cursor:
        try:
            await send_reminder(reminder)

        except Exception as e:
            print("Failed to send reminder: {e}")

@bot.event
async def on_ready():
    if not reminder_scheduler.is_running():
        reminder_scheduler.start()
    print(f"{bot.user.name} has successfully started")

bot.run(TOKEN)