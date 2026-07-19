import os
from dotenv import load_dotenv

load_dotenv()


def _int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WELCOME_CHANNEL_ID = _int(os.getenv("WELCOME_CHANNEL_ID"), 0)
GUILD_ID = _int(os.getenv("GUILD_ID"), 0)
SHOP_CHANNEL_ID = _int(os.getenv("SHOP_CHANNEL_ID"), 0)
OWNER_ID = _int(os.getenv("OWNER_ID"), 0)
TRADING_CHANNEL_ID = _int(os.getenv("TRADING_CHANNEL_ID"), 0)
LEADERBOARD_CHANNEL_ID = _int(os.getenv("LEADERBOARD_CHANNEL_ID"), 0)
XP_LEADERBOARD_CHANNEL_ID = _int(os.getenv("XP_LEADERBOARD_CHANNEL_ID"), 0)
LEAVE_CHANNEL_ID = _int(os.getenv("LEAVE_CHANNEL_ID"), 0)
VOICE_FARM_CHANNEL_ID = _int(os.getenv("VOICE_FARM_CHANNEL_ID"), 1528407849649311754)
VOICE_FARM_TEXT_CHANNEL_ID = _int(os.getenv("VOICE_FARM_TEXT_CHANNEL_ID"), 0)
BOT_COMMANDS_CHANNEL_ID = _int(os.getenv("BOT_COMMANDS_CHANNEL_ID"), 1499070938367660083)
GAME_SERVER_SUPPORT_CHANNEL_ID = _int(os.getenv("GAME_SERVER_SUPPORT_CHANNEL_ID"), 1520760975995699410)
MAIN_SERVER_FEEDBACK_CHANNEL_ID = _int(os.getenv("MAIN_SERVER_FEEDBACK_CHANNEL_ID"), 1488847189471133827)
