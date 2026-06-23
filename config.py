import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("GUILD_ID", 0))
SHOP_CHANNEL_ID = int(os.getenv("SHOP_CHANNEL_ID", 0))
OWNER_ID = int(os.getenv("OWNER_ID", 0))
TRADING_CHANNEL_ID = int(os.getenv("TRADING_CHANNEL_ID", 0))
LEADERBOARD_CHANNEL_ID = int(os.getenv("LEADERBOARD_CHANNEL_ID", 0))
XP_LEADERBOARD_CHANNEL_ID = int(os.getenv("XP_LEADERBOARD_CHANNEL_ID", 0))
