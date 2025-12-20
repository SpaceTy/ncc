import random


async def handle_coin_toss(message):
    """Handle the !ct command to flip a coin."""
    result = random.choice(["Heads", "Tails"])
    await message.reply(f"🪙 {result}!")
