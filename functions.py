from arena import Arena
import aiohttp
import datetime
from datetime import datetime, timezone
import logging
import os
import status
import pandas as pd
api_url = status.get_state("API-url")
logger = logging.getLogger(__name__)
# API FUNCTIONS

async def api_GET(endpoint, params=None):
	"""
	Send a GET request to the API.
	"""
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{api_url}{endpoint}", params=params) as response:
			logger.info(f"response status: {response.status}")
			return await response.json()

async def api_POST(endpoint, params=None):
	"""
	Send a POST request to the API.
	"""
	async with aiohttp.ClientSession() as session:
		async with session.post(f"{api_url}{endpoint}", json=params) as response:
			logger.info(f"response status: {response.status}")
			return await response.json()

# SETUP FUNCTIONS

async def get_endpoints():
	"""
	Get the endpoints from the API.
	"""
	api_endpoints = await api_GET("endpoints")
	return api_endpoints

# BOT FUNCTIONS
async def get_arena_board(board_slug):
	url = f"https://api.are.na/v2/channels/{board_slug}/contents?per={5}&sort=created_at&direction=desc"
	headers = {
		'Authorization': f'Bearer {os.getenv("arena_token")}',
	}

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers) as response:
			res =  await response.json()
			return res.get("contents")

async def arena_updates(delta_seconds=55):
	boards = status.get_state("arena_boards")
	logger.info(f"Arena boards: {boards}")
	df = pd.DataFrame(boards)
	logger.info(f"Board slugs: {df.head()}")
	board_slugs = df['arena-channel-slug'].values
	try:
		new_blocks = []
		current_timestamp = datetime.now(timezone.utc)
		for board_slug in board_slugs:
			items = await get_arena_board(board_slug)
			for item in items:
				updated_at_str = item.get("created_at")
				item_timestamp = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
				time_diff = (current_timestamp - item_timestamp).total_seconds()
				if time_diff < delta_seconds:
					item['board'] = df.loc[df['arena-channel-slug'] == board_slug, 'nickname'].values[0]
					new_blocks.append(item)
		logger.info(f"Found {len(new_blocks)} new arena blocks")
		return new_blocks
	except Exception as e:
		logger.error(f"Error checking arena updates: {e}")
		return []

