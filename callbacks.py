import base64
import discord
from discord.ui import View
import functions
import io
import logging
import re

logger = logging.getLogger(__name__)

async def basic(endpoint, interaction):
	await interaction.response.defer()
	response = await functions.api_POST(f"api/{endpoint}", None)
	logger.info(f"Basic callback called with endpoint: {endpoint} - {response}")
	await interaction.followup.send(response["result"])

async def arena_save(interaction, board):
	await interaction.response.defer()
	if not interaction.message:
		await interaction.followup.send("Error: This command must be used as a reply to a message")
		return
	
	message_id = interaction.message.id
	message = await interaction.channel.fetch_message(message_id)

	url = None

	# check url in content 
	content_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
	if content_urls:
		url = content_urls[0]
	
	# check embeds
	if not url and message.embeds:
		for embed in message.embeds:
			if embed.url:
				url = embed.url
				break
	
	# check for attachments (pictures)
	if not url and message.attachments:
		for attachment in message.attachments:
			if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
				url = attachment.url
				break

	if not url:
		await interaction.followup.send("Error: No URL found in the message")
		return

	response = await functions.api_POST(f"api/arena_save", {"board": board, "url": url})
	logger.info(f"Arena save callback called with board: {board} - {response}")
	await interaction.followup.send(response["result"])

async def haiku(interaction, about):
	await interaction.response.defer()
	# Get the 'about' parameter from the interaction options
	if about:
		response = await functions.api_POST('api/haiku', {"about": about})
	else:
		response = await functions.api_POST('api/haiku', None)
	await interaction.followup.send(response["result"])

async def joke(interaction):
    await interaction.response.defer()
    response = await functions.api_POST('api/joke', None)
    logger.info(f"Joke callback called - {response}")
    
    label = response['result']['question']
    callback_message = response['result']['answer']
    
    class CustomView(View):
        def __init__(self):
            super().__init__()
            
        @discord.ui.button(label=label, style=discord.ButtonStyle.primary)
        async def button_callback(self, button_interaction, button):
            await button_interaction.response.send_message(callback_message)
            
    # Send a message with the view (include some content to avoid the empty message error)
    await interaction.followup.send(content="Here's a joke for you:", view=CustomView())

async def image(interaction, prompt):
	await interaction.response.defer()
	response = await functions.api_POST('api/image', {"prompt": prompt})
	b64_image = response['result']['b64']
	generation_time = response['result']['generation_time']
	total_energy_nespresso = response['result']['total_energy_nespresso']
	image_data = base64.b64decode(b64_image)
	logger.info(f"Image callback called - {response}")
	file = discord.File(io.BytesIO(image_data), filename="image.png")
	embed = discord.Embed()
	embed.set_image(url="attachment://image.png")
	embed.set_footer(text=f"✏️ prompt: {prompt}\n⌛ Generated on a MacMini in {int(generation_time)} seconds\n☕️ This generation used the energy of {total_energy_nespresso} espresso")
	await interaction.followup.send(embed=embed, file=file)

async def pokemon(interaction):
	await interaction.response.defer()
	response = await functions.api_POST('api/pokemon', None)
	message = response['result']['message']
	is_shiny = response['result']['is_shiny']
	image = response['result']['image']
	#logger.info(f"Pokemon callback called - {response}")
	if is_shiny == "True":
		embed = discord.Embed(description=f"{message}", color=0xf2ad39)
	else:
		embed = discord.Embed(description=f"{message}", color=0x74b354)
	embed.set_image(url=f"{image}")
	await interaction.followup.send(embed=embed)

async def rembg(interaction, image_url=None, attachment=None):
	await interaction.response.defer()
	if attachment:
		image_url = attachment.url
	# If no attachment but image_url is provided, use that
	elif image_url:
		pass
	# If neither, check message attachments (for context menu commands)
	elif hasattr(interaction, 'message') and interaction.message and interaction.message.attachments:
		image_url = interaction.message.attachments[0].url
	else:
		return await interaction.followup.send("Please provide an image or attach one to your message.")
	
	response = await functions.api_POST('api/rembg', {"image_url": image_url})
	try:
		image_data = base64.b64decode(response["result"])
		file = discord.File(io.BytesIO(image_data), filename="no_bg.png")
		await interaction.followup.send("", file=file)
	except Exception as e:
		logger.error(f"Error removing background - {e}")
		await interaction.followup.send(f'Error removing background - {e}')
	logger.info(f"Remove background callback called - {response}")

async def roby(interaction, prompt):
	await interaction.response.defer()
	response = await functions.api_POST('api/roby', {"prompt": prompt})
	logger.info(f"Roby callback called - {response}")
	embed = discord.Embed(description=response["result"])
	embed.set_author(name=f"💬 {prompt[:250] + ('…' if len(prompt) > 250 else '')}", icon_url=interaction.user.avatar.url)
	embed.color = 0xAEF39B
	await interaction.followup.send(embed=embed)

async def throw(interaction, faces):
	await interaction.response.defer()
	response = await functions.api_POST('api/throw', {"faces": faces})
	logger.info(f"Throw callback called with faces: {faces} - {response}")
	await interaction.followup.send(response["result"])

async def who_starts(interaction):
	await interaction.response.defer()
	# TODO get oios
	response = await functions.api_POST('api/who_starts', None)
	logger.info(f"Who starts callback called - {response}")
	await interaction.followup.send(response["result"])