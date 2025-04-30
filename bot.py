import aiohttp
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import dotenv
import callbacks
import logging
import os
import startup
import status
import subprocess
import sys
import time
import traceback
from typing import Optional

dotenv.load_dotenv()

logger = logging.getLogger('discord')

# API info
API_HOST = "0.0.0.0"  
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"
STARTUP_TIMEOUT = 60

# Bot settings
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=status.get_state("prefix"), intents=intents)

async def ping_port(port):
	"""Ping a port to check if it's available"""
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get(f"http://localhost:{port}", timeout=2) as response:
				return True
	except (aiohttp.ClientError, asyncio.TimeoutError):
		return False

async def wait_for_api():
    """Wait for the API to be ready"""
    return await startup.wait_for_api()

async def start_tools():
    """Start the tools"""
    return await startup.start_tools()
# Remove default help command
bot.remove_command('help')

#beep
@bot.tree.command(name="beep", description="🤖 Beep")
async def beep(interaction: discord.Interaction):
	logger.info(f"Beep command called")
	await callbacks.basic("beep", interaction)

#bop
@bot.tree.command(name="bop", description="🤖 Bop")
async def bop(interaction: discord.Interaction):
	logger.info(f"Bop command called")
	await callbacks.basic("bop", interaction)

#btc
@bot.tree.command(name="btc", description="💰 Bitcoin value in USD")
async def btc(interaction: discord.Interaction):
	logger.info(f"Btc command called")
	#await callbacks.basic("btc", interaction)
	await callbacks.currency("btc", interaction)
#eth
@bot.tree.command(name="eth", description="💰 Ethereum value in USD")
async def eth(interaction: discord.Interaction):
	logger.info(f"Eth command called")
	#await callbacks.basic("eth", interaction)
	await callbacks.currency("eth", interaction)

#flip
@bot.tree.command(name="flip", description="🪙 Flip a coin")
async def flip(interaction: discord.Interaction):
	logger.info(f"Flip command called")
	await callbacks.basic("flip", interaction)

#haiku
@bot.tree.command(name="haiku", description="🍶 Generate a haiku")
@app_commands.describe(about="The topic of the haiku")
async def haiku(interaction: discord.Interaction, about: str):
	logger.info(f"Haiku command called with about: {about}")
	await callbacks.haiku(interaction, about)

#help
@bot.tree.command(name="help", description="🛟 All commands")
async def help(interaction: discord.Interaction):
	logger.info(f"Help command called")
	await interaction.response.defer()

	# Get all registered commands
	commands = bot.tree.get_commands()
	
	# Sort commands alphabetically by name
	commands.sort(key=lambda x: x.name)

	# Create embed
	embed = discord.Embed(title="Available Commands", color=0x00ff00)
	
	# Add each command to embed
	for cmd in commands:
		name = cmd.name
		desc = cmd.description if cmd.description else "No description available"
		embed.add_field(name=f"/{name}", value=desc, inline=False)

	await interaction.followup.send(embed=embed)

#image
@bot.tree.command(name="image", description="🎨 Generate an image")
@app_commands.describe(prompt="The prompt for the image")
async def image(interaction: discord.Interaction, prompt: str):
	logger.info(f"Image command called with prompt: {prompt}")
	await callbacks.image(interaction, prompt)

#joke
@bot.tree.command(name="joke", description="🤡 Tell me a joke")
async def joke(interaction: discord.Interaction):
	logger.info(f"Joke command called")
	await callbacks.joke(interaction)

#ping
@bot.tree.command(name="ping", description="🏓 Ping")
async def ping(interaction: discord.Interaction):
	logger.info(f"Ping command called")
	await callbacks.basic("ping", interaction)

#remove_bg
@bot.tree.command(name="rembg", description="🖼️ Remove background from image")
@app_commands.describe(image_url="URL of the image (optional if image is attached)")
async def rembg(interaction: discord.Interaction, image_url: Optional[str] = None, attachment: Optional[discord.Attachment] = None):
	logger.info(f"Remove background command called")
	await callbacks.rembg(interaction, image_url=image_url, attachment=attachment)

# roby
@bot.tree.command(name="roby", description="🤖 Chat with Roby")
@app_commands.describe(prompt="The prompt for Roby")
async def roby(interaction: discord.Interaction, prompt: str):
	logger.info(f"Roby command called")
	await callbacks.roby(interaction, prompt)

#thanks TODO
@bot.tree.command(name="thanks", description="🙏 Thanks")
async def thanks(interaction: discord.Interaction):
	logger.info(f"Thanks command called")
	await callbacks.basic("thanks", interaction)

#throw
@bot.tree.command(name="throw", description="🎲 Roll a dice")
@app_commands.describe(faces="The number of faces")
async def throw(interaction: discord.Interaction, faces: int):
	logger.info(f"Throw command called with {faces} faces")
	await callbacks.throw(interaction, faces)
	
#wdyt
@bot.tree.command(name="wdyt", description="🤔 What do you think?")
async def wdyt(interaction: discord.Interaction):
	logger.info(f"Wdyt command called")
	await callbacks.basic("wdyt", interaction)

#wisdom
@bot.tree.command(name="wisdom", description="🧙 Ask roby for wisdom")
async def wisdom(interaction: discord.Interaction):
	logger.info(f"Wisdom command called")
	await callbacks.basic("wisdom", interaction)

@bot.event
async def on_command_error(ctx, error):
	"""Handle command errors"""
	if isinstance(error, commands.CommandNotFound):
		cmd = ctx.message.content.split()[0][len(bot.command_prefix):]
		logger.warning(f"Command not found: {cmd}")
	else:
		logger.error(f"Command error in {ctx.command}: {error}")
		logger.error(traceback.format_exc())
		await ctx.send(f"Error: {str(error)}")

# Command to check what commands are registered (for debugging)
@bot.command(name="listcommands")
async def list_commands(ctx):
	command_list = sorted([cmd.name for cmd in bot.commands])
	await ctx.send(f"Available commands ({len(command_list)}): {', '.join(command_list)}")

@tasks.loop(seconds=55)
async def routine_function():
	"""
	Example routine function.
	Runs every 55 seconds.
	"""
	logger.info("I'm alive")
	
@routine_function.before_loop
async def before_routine_function():
	"""Wait for bot to be ready before starting routine_function loop."""
	await bot.wait_until_ready()

@bot.event
async def on_ready():
	"""api_ready = await wait_for_api()
	tools_ready = await start_tools()
	if not api_ready:
		logger.error("Failed to ensure API is running. Bot functionality may be limited.")
		return"""
	
	all_services_running = await startup.ensure_all_services()
	if not all_services_running:
		logger.error("Failed to ensure all services are running. Bot functionality may be limited.")
		return

	logger.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")

	try:
		synced = await bot.tree.sync()
		logger.info(f"Synced {len(synced)} command(s)")
	except Exception as e:
		logger.error(f"Failed to sync commands: {e}")

	routine_function.start()
	#logger.info(f"Connected to {len(bot.guilds)} guilds")

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	
	await bot.process_commands(message)

if __name__ == "__main__":
	logger.info("Starting bot...")
	try:
		bot.run(os.environ['TOKEN'])
	except KeyboardInterrupt:
		# This is caught by the signal handler
		logger.info("Received keyboard interrupt, shutting down...")
		pass
	except Exception as e:
		logger.critical(f"Failed to start bot: {e}")
	finally:
		# Make sure we attempt to stop services if the bot crashes
		try:
			# Try to get the existing event loop or create a new one
			try:
				loop = asyncio.get_event_loop()
			except RuntimeError:
				# If no event loop exists, create a new one
				loop = asyncio.new_event_loop()
				asyncio.set_event_loop(loop)
			
			# Run the cleanup function in the loop
			if loop.is_running():
				loop.create_task(startup.stop_all_services())
			else:
				loop.run_until_complete(startup.stop_all_services())
		except Exception as e:
			logger.error(f"Error during shutdown: {e}")
		finally:
			logger.info("Bot process terminated")