# ROBY: a multifunction Discord bot
This is the Discord bot side of Roby. It's a FastAPI + Discord.py app whose commands are accessible both in Discord and via REST.

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

###  env
You need to add an .env file inside the bot's root folder with the following variables.
```
TOKEN = YOUR_DISCORD_BOT_TOKEN
ROBY_CHANNEL = OPTIONAL,_A_SPECIFIC_CHANNEL_ID_FOR_BOT_OUTPUTS
```

## Run the app
```
uv sync
uv run bot.py
```

## Adding a new command
Think about Roby as a Discord interface to the [Domestic API](https://github.com/oio/domestic-API/). This means that the core functions should be implemented there as API routes and called by Roby. This allows to access them not only from Discord but also via curl by making the code architecture modular. If the command involves complex operations, consider creating an independent tool within [Domestic Tools](https://github.com/oio/domestic-tools). 

Once you have created the functions to call in the appropriate repository, you can implement the command in roby. The first thing is to initialise and register it in bot.py. We recommend to implement it as a slash command. Each command calls a callback from callbacks.py. There, you can implement the reply mechanics. In bot.py keep the code clean

```
# bot.py

# regular slash command
@bot.tree.command(name="my_command", description="🌱 Test command")
async def thanks(interaction: discord.Interaction):
	logger.info(f"test command called")
	await callbacks.basic("api_route_name", interaction) # you can use the basic callback for commands that don't require parameters
```

```
# callbacks.py

```
