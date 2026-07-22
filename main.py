import sys
import os
import json

_BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_BASE)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BASE, ".env"))

_secrets = {}
_secrets_path = os.path.join(_BASE, "secrets.json")
if os.path.exists(_secrets_path):
    with open(_secrets_path) as f:
        _secrets = json.load(f)

for key in ("DISCORD_TOKEN", "DATABASE_URL", "NEON_DB_URL"):
    val = os.getenv(key) or _secrets.get(key) or os.environ.get(key)
    if val:
        os.environ[key] = val

if not os.getenv("DISCORD_TOKEN"):
    raise RuntimeError("DISCORD_TOKEN not set. Put it in secrets.json, .env, or environment variables.")

import discord
from discord.ext import commands
from config import GUILD_ID

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    async def setup_hook(self):
        import cogs.economy
        import cogs.welcome
        import cogs.general
        import cogs.shop
        import cogs.pet_shop
        import cogs.trading
        import cogs.leaderboard
        import cogs.owner
        import cogs.support
        import cogs.voice_farm
        for mod in [cogs.economy, cogs.welcome, cogs.general, cogs.shop, cogs.pet_shop, cogs.trading, cogs.leaderboard, cogs.owner, cogs.support, cogs.voice_farm]:
            await mod.setup(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})", flush=True)
        try:
            synced = await self.tree.sync()
            names = [c.name for c in synced]
            print(f"Synced {len(synced)} global command(s): {names}", flush=True)
        except Exception as e:
            print(f"Failed to sync global commands: {e}", flush=True)
        if GUILD_ID:
            try:
                guild_obj = discord.Object(id=GUILD_ID)
                synced = await self.tree.sync(guild=guild_obj)
                names = [c.name for c in synced]
                print(f"Synced {len(synced)} guild command(s): {names}", flush=True)
            except Exception as e:
                print(f"Failed to sync guild commands: {e}", flush=True)


from keep_alive import keep_alive
keep_alive()

bot = MyBot()
bot.run(os.environ["DISCORD_TOKEN"])
