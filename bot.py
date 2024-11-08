import discord
import openai
import asyncio
import time
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

cooldown_time = 10
user_last_request = {}

async def send_to_openai(prompt):
    try:
        response = openai.chat_completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = message.author.id
    current_time = time.time()

    if user_id in user_last_request:
        last_request_time = user_last_request[user_id]
        time_diff = current_time - last_request_time
        if time_diff < cooldown_time:
            remaining_time = cooldown_time - time_diff
            await message.channel.send(f"Please wait {int(remaining_time)} seconds before using the bot again.")
            return

    user_last_request[user_id] = current_time

    prompt = message.content
    response = await send_to_openai(prompt)
    await message.channel.send(response)

client.run(DISCORD_TOKEN)
