# ROBY: a multifunction Discord bot
This is the Discord bot side of Roby. It's a FastAPI + Discord.py app whose commands are accessible both in Discord and via REST.

## Set the bot
### Create a Discord app
Register an app on Discord using the [Developer Portal](https://discord.com/developers/docs/quick-start/getting-started).

###  secrets/config.json
Here is the architecture of the config we're using
```python
{
	"token": "token", # Discord app token
	"prefix" : "roby ",
	"arena_token" : "arena_token", # are.na API token
	"arena2discord_url" :  "spreadsheet url",# spreadsheet url
	"guild_ids" : [], # server ids
	"role_ids" : [], #"role ids for each server"
	"oio_channel_id" : 1234, # main channel id
	"test_oio_channel_id" : 2345, # test channel id
	"service_account" : {} # for firebase	  
}
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
