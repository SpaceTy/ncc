import discord
import config
from features import coordinates, fun, snc, coin

# --- Bot Setup ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user.name}")
    print(f"Listening on channel ID: {config.TARGET_CHANNEL_ID}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != config.TARGET_CHANNEL_ID:
        return

    content_lower = message.content.lower()

    # Coordinate Conversion (!ncc, !occ)
    if "!ncc" in content_lower or "!occ" in content_lower:
        await coordinates.handle_coordinate_conversion(message)
    
    # Crazy Text Generator (!c)
    elif content_lower.startswith("!c "):
        await fun.handle_crazy_text(message)

    # Stack Number Converter (!snc, !nsc)
    elif content_lower.startswith("!snc"):
        await snc.handle_snc_command(message)
    elif content_lower.startswith("!nsc"):
        await snc.handle_nsc_command(message)

    # Coin Toss (!ct)
    elif content_lower.startswith("!ct"):
        await coin.handle_coin_toss(message)

if __name__ == "__main__":
    if not config.DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set.")
    else:
        try:
            client.run(config.DISCORD_BOT_TOKEN)
        except discord.errors.LoginFailure:
            print("Error: Invalid Discord Bot Token. Please check your token.")
        except Exception as e:
            print(f"An error occurred while starting the bot: {e}")
