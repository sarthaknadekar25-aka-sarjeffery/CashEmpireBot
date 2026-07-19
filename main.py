import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import discord
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    async def setup_hook(self):
        for cog in ["cogs.economy", "cogs.welcome", "cogs.general", "cogs.shop", "cogs.pet_shop", "cogs.trading", "cogs.leaderboard", "cogs.owner", "cogs.support", "cogs.voice_farm"]:
            await self.load_extension(cog)

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


bot = MyBot()
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in .env or Railway Variables")
bot.run(DISCORD_TOKEN)
