import datetime

import discord


WEEK = datetime.timedelta(days=7)
KICK_REASON = "No roles and joined more than a week ago."
MAX_MEMBERS_SHOWN = 20


async def find_kick_candidates(guild):
    """Return non-bot members whose only role is @everyone and who joined more than a week ago."""
    cutoff = discord.utils.utcnow() - WEEK
    candidates = []
    async for member in guild.fetch_members():
        if member.bot or member.guild_permissions.administrator:
            continue
        if member.roles != [guild.default_role]:
            continue
        if member.joined_at is None or member.joined_at >= cutoff:
            continue
        candidates.append(member)
    return candidates


class KickConfirmView(discord.ui.View):
    def __init__(self, invoker, members):
        super().__init__(timeout=60)
        self.invoker = invoker
        self.members = members
        self.preview = None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.invoker.id:
            await interaction.response.send_message(
                "Only the person who ran the command can use these buttons.", ephemeral=True
            )
            return False
        return True

    def _disable_buttons(self):
        for item in self.children:
            item.disabled = True

    async def _finalize(self, text):
        self._disable_buttons()
        self.stop()
        if self.preview:
            try:
                await self.preview.edit(content=text, view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.danger)
    async def proceed(self, interaction, button):
        await interaction.response.defer()
        kicked, skipped = 0, 0
        for member in self.members:
            try:
                await member.kick(reason=KICK_REASON)
                kicked += 1
            except discord.HTTPException:
                skipped += 1
        result = f"Kicked {kicked} member(s)."
        if skipped:
            result += f" Skipped {skipped} member(s) due to errors."
        await self._finalize(result)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button):
        await interaction.response.defer()
        await self._finalize("Kick cancelled. No one was kicked.")

    async def on_timeout(self):
        self._disable_buttons()
        if self.preview:
            try:
                await self.preview.edit(
                    content=f"{self.preview.content}\n\nConfirmation timed out - no one was kicked.",
                    view=self,
                )
            except discord.HTTPException:
                pass


async def handle_kick(message):
    """Handle the !kick command to kick members with no roles who joined more than a week ago."""
    guild = message.guild
    if guild is None:
        await message.reply("This command can only be used in a server.")
        return

    if not guild.me.guild_permissions.kick_members:
        await message.reply("I need the `Kick Members` permission to use this command.")
        return

    candidates = await find_kick_candidates(guild)
    if not candidates:
        await message.reply("No members with no roles joined more than a week ago.")
        return

    lines = [
        f"- {member.mention} ({member.name}) - joined <t:{int(member.joined_at.timestamp())}:R>"
        for member in candidates[:MAX_MEMBERS_SHOWN]
    ]
    if len(candidates) > MAX_MEMBERS_SHOWN:
        lines.append(f"...and {len(candidates) - MAX_MEMBERS_SHOWN} more")

    view = KickConfirmView(message.author, candidates)
    preview = await message.reply(
        f"Found {len(candidates)} member(s) to kick:\n" + "\n".join(lines) + "\n\nProceed with kick?",
        view=view,
    )
    view.preview = preview


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
