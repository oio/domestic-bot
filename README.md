# ROBY: a multifunction Discord bot
This is the Discord bot side of [Domestic AI](https://github.com/oio/domestic-ai). It's a Discord.py interface to the [Domestic API](https://github.com/oio/domestic-api) that can be used to interact with the Domestic AI system through Discord.

## Set the bot
### Create a Discord app
Register a Discord Application using the [Developer Portal](https://discord.com/developers/docs/quick-start/getting-started). Go into the Application's panel set the needed settings.
#### Under the Bot panel
Set to true all the Privileged Gateway Intents (Presence Intent
, Server Members Intent, Message Content Intent).
####  Under the Installation panel
1. Only select Guild install. 
To be fully implementable the bot will require the following scopes and permissions to be enabled:
Scopes
1. application.commands
1. bot
Permissions
1. Administrator
1. Manage Channels
1. Manage Server
1. Manage Messages
1. Manage Roles
1. Send Messages
1. View Channels

*Note: these permissions are more than the minimum required to make the bot work but might be needed if you want to implement more complex features.*


###  Create an .env file
You need to add an .env file inside the bot's root folder and define the following variables.
```
TOKEN = YOUR_DISCORD_BOT_TOKEN
```

## Run the app
```
uv sync
uv run bot.py
```

## Adding a new command
Think about Roby as a Discord interface to the [Domestic API](https://github.com/oio/domestic-API/): the core functions should be implemented there as API routes and just after being called by Roby. This allows to access them not only from Discord but also via curl, and by consequence this makes the code more modular. 

Go to the [Domestic API repository](https://github.com/oio/domestic-API/) and implement the new functionality there. Also, keep in mind that if it involves complex operations, you can consider creating an independent tool within [Domestic Tools](https://github.com/oio/domestic-tools) and call it from the API.

Once you have created the function in the API, you can implement the command within this bot. The first thing is to initialise and register it in `bot.py`. We recommend to implement it as a slash command. Each command calls a callback from `callbacks.py`. There, you can implement the reply mechanics while keeping `bot.py` as clean as possible.

### Implementing a simple slash command
Most of the commands can be handled via the basic callback that is already implemented in `callbacks.py`.
```
# bot.py

# regular slash command
@bot.tree.command(name="my_command", description="🌱 Test command")
async def thanks(interaction: discord.Interaction):
	logger.info(f"test command called")
	await callbacks.basic("api_route_name", interaction) # you can use the basic callback for commands that don't require parameters
```

### Implementing a slash command with parameters
More complex commands might require input parameters or result manipulation. In this case you can implement a custom callback.

```
# bot.py
@bot.tree.command(name="my_command", description="🌱 Test command")
async def thanks(interaction: discord.Interaction):
	logger.info(f"test command called")
	await callbacks.custom_callback_name("api_route_name", interaction) # your implementation of the callback
```

```
# callbacks.py
async def custom_callback_name(endpoint, interaction):
	await interaction.response.defer() # always defer the interaction to have time to elaborate the output
	response = await functions.api_POST(f"api/{endpoint}", None)
	value = response["result"][:2]
	# do something with the result if needed
	await interaction.followup.send(value)
```
