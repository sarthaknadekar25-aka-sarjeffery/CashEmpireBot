from config import BOT_COMMANDS_CHANNEL_ID, OWNER_ID


async def check_bot_commands(interaction):
    if interaction.user.id == OWNER_ID:
        return True
    if interaction.channel_id == BOT_COMMANDS_CHANNEL_ID:
        return True
    await interaction.response.send_message(f"This command can only be used in <#{BOT_COMMANDS_CHANNEL_ID}>.", ephemeral=True)
    return False
