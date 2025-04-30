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

async def currency(endpoint, interaction):
	await interaction.response.defer()
	response = await functions.api_POST(f"api/{endpoint}", None)
	logger.info(f"Currency callback called with endpoint: {endpoint} - {response}")
	# Format the number with thousands separator
	value = float(response["result"])
	# Remove trailing zeros from decimal places
	if value.is_integer():
		parsed_response = f"{value:,.0f} USD"
	else:
		# Remove trailing zeros but keep necessary decimals
		parsed_response = f"{value:,.{len(str(value).split('.')[-1].rstrip('0'))}f} USD"
	await interaction.followup.send(parsed_response)

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