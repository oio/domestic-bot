"""
The set of statuses used by the bot.
"""

state = {
	"prefix" : "roby ", 
	"API-url" : "http://0.0.0.0:8000/", 
}

def get_state(key):
	return state[key]

def set_state(key, value):
	state[key] = value