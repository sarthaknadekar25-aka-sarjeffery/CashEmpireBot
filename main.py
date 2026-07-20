import sys
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_BASE)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

print(f"[Startup] CWD: {os.getcwd()}", flush=True)
print(f"[Startup] DISCLOUD_* env: {[k for k in os.environ if 'DISCLOUD' in k.upper()]}", flush=True)
print(f"[Startup] DISCORD_TOKEN in os.environ: {'DISCORD_TOKEN' in os.environ}", flush=True)
print(f"[Startup] DATABASE_URL in os.environ: {'DATABASE_URL' in os.environ}", flush=True)

import discord
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID

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


from dotenv import load_dotenv
load_dotenv(os.path.join(_BASE, ".env"))

_token = os.getenv("DISCORD_TOKEN")
if not _token:
    print(f"[Startup] All env keys: {list(os.environ.keys())}", flush=True)
    raise RuntimeError("DISCORD_TOKEN not set in environment or .env file")

bot = MyBot()
bot.run(_token)
