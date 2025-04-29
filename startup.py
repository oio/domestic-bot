import aiohttp
import asyncio
import dotenv
import logging
import os
import psutil
import subprocess
import time
from typing import Dict, List, Optional
dotenv.load_dotenv()
logger = logging.getLogger('discord')

# Constants
STARTUP_TIMEOUT = 60
DOMESTIC_AI_PATH = os.environ['DOMESTIC_AI_PATH']
API_HOST = "0.0.0.0"
API_PORT = 8000
API_ENDPOINT = "/api_endpoints"

class Startup:
	"""Class to represent a service (API or tool)"""
	def __init__(self, 
				 name: str, 
				 port: int, 
				 host: str = "localhost", 
				 endpoint: str = "/", 
				 command_path: str = None,
				 startup_timeout: int = STARTUP_TIMEOUT):
		self.name = name
		self.port = port
		self.host = host
		self.url = f"http://{host}:{port}{endpoint}"
		self.command_path = command_path
		self.startup_timeout = startup_timeout

	async def is_running(self, session: aiohttp.ClientSession, timeout: int = 2) -> bool:
		"""Check if the service is running"""
		try:
			async with session.get(self.url, timeout=timeout) as response:
				return response.status == 200
		except (aiohttp.ClientError, asyncio.TimeoutError):
			return False

	async def start(self) -> bool:
		"""Start the service if it's not already running"""
		if not self.command_path:
			logger.warning(f"No command path specified for {self.name}, cannot start")
			return False

		try:
			# Launch the service process in the background
			subprocess.Popen(['bash', self.command_path], 
							stdout=subprocess.DEVNULL,
							stderr=subprocess.DEVNULL,
							start_new_session=True)
			
			logger.info(f"Started {self.name} process with command: {self.command_path}")
			
			# Wait for service to become available
			start_time = time.time()
			while time.time() - start_time < self.startup_timeout:
				async with aiohttp.ClientSession() as session:
					if await self.is_running(session):
						logger.info(f"{self.name} is now running")
						return True
				logger.info(f"Waiting for {self.name} to start...")
				await asyncio.sleep(2)
			
			logger.error(f"{self.name} did not start within {self.startup_timeout} seconds")
			return False
		except Exception as e:
			logger.error(f"Failed to start {self.name}: {e}")
			return False

	async def stop(self) -> bool:
		"""Stop the service if it's running"""
		try:
			# First try to find the process by port
			process = find_process_by_port(self.port)
			if process:
				logger.info(f"Stopping {self.name} (PID: {process.pid})")
				process.terminate()
				try:
					process.wait(timeout=5)
				except psutil.TimeoutExpired:
					logger.warning(f"Process {process.pid} didn't terminate, forcing kill")
					process.kill()
				logger.info(f"Successfully stopped {self.name}")
				return True
			else:
				logger.warning(f"No process found using port {self.port} for {self.name}")
				return False
		except Exception as e:
			logger.error(f"Error stopping {self.name}: {e}")
			return False
async def ensure_service_running(service: Startup, max_attempts: int = 5) -> bool:
	"""Ensure a service is running, attempting to start it if needed"""
	# First check if it's already running
	logger.info(f"Checking if {service.name} is available...")
	
	for attempt in range(max_attempts):
		async with aiohttp.ClientSession() as session:
			if await service.is_running(session):
				logger.info(f"{service.name} is already running")
				return True
		
		if attempt < max_attempts - 1:
			logger.info(f"{service.name} not available (attempt {attempt+1}/{max_attempts}), waiting...")
			await asyncio.sleep(2)
	
	# Service is not running, try to start it
	logger.info(f"{service.name} not available after {max_attempts} attempts, trying to start it")
	return await service.start()

async def ensure_services_running(services: List[Startup]) -> Dict[str, bool]:
	"""Ensure multiple services are running and return their status"""
	results = {}
	for service in services:
		results[service.name] = await ensure_service_running(service)
	return results

def find_process_by_port(port: int) -> Optional[psutil.Process]:
    """Find a process that is listening on the given port"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):  # Remove 'connections' from here
            try:
                # Get connections separately for each process
                connections = proc.connections(kind='inet')
                for conn in connections:
                    if conn.laddr.port == port:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.error(f"Error in find_process_by_port: {e}")
        return None
    return None

async def stop_service(service: Startup) -> bool:
    """Stop a specific service"""
    logger.info(f"Stopping service: {service.name}")
    return await service.stop()

async def stop_services(services: List[Startup]) -> Dict[str, bool]:
    """Stop multiple services and return their status"""
    results = {}
    for service in services:
        results[service.name] = await stop_service(service)
    return results

async def stop_all_services() -> bool:
    """Stop all services (API and tools)"""
    logger.info("Stopping all services...")
    results = await stop_services(services)
    return all(results.values())

# New function to stop specific service types
async def stop_api():
    """Stop just the API"""
    api_service = next(service for service in services if service.name == "API")
    return await stop_service(api_service)

async def stop_tools():
    """Stop just the tools"""
    tool_services = [service for service in services if service.name != "API"]
    results = await stop_services(tool_services)
    return all(results.values())

# Define services
services = [
	Startup(
		name="API", 
		host=API_HOST, 
		port=API_PORT, 
		endpoint=API_ENDPOINT,
		command_path=os.path.join(DOMESTIC_AI_PATH, "domestic-api", "run-api.command")
	),
	Startup(
		name="Rembg Tool", 
		port=8008, 
		endpoint="/",
		command_path=os.path.join(DOMESTIC_AI_PATH, "domestic-tools", "domestic-rembg", "run-rembg.command")
	),
	Startup(
		name="Image Generation Tool", 
		port=8042, 
		endpoint="/queue-status",  # Changed from "/" to a real endpoint
		command_path=os.path.join(DOMESTIC_AI_PATH, "domestic-tools", "domestic-imagen", "run-imagen.command")
	)
]

async def wait_for_api():
	"""Replacement for the original wait_for_api function"""
	api_service = next(service for service in services if service.name == "API")
	return await ensure_service_running(api_service)

async def start_tools():
	"""Replacement for the original start_tools function"""
	tool_services = [service for service in services if service.name != "API"]
	results = await ensure_services_running(tool_services)
	return all(results.values())

# A new unified function that handles both API and tools
async def ensure_all_services():
	"""Ensure all services (API and tools) are running"""
	results = await ensure_services_running(services)
	return all(results.values())