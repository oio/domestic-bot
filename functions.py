import aiohttp
import logging
import status
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
