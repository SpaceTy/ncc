import discord


async def handle_delete(message):
    """Handle the !delete <count> command to delete messages."""
    parts = message.content.split()
    if len(parts) != 2:
        await message.reply("Usage: `!delete <count>`")
        return

    try:
        count = int(parts[1])
    except ValueError:
        await message.reply("Please provide a valid number.")
        return

    if count < 1 or count > 100:
        await message.reply("Count must be between 1 and 100.")
        return

    deleted = await message.channel.purge(limit=count + 1)
    await message.channel.send(f"Deleted {len(deleted) - 1} message(s).", delete_after=3)
