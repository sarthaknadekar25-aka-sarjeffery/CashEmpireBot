import discord
from discord.ext import commands
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        for cog in ["cogs.economy", "cogs.welcome", "cogs.general", "cogs.shop", "cogs.pet_shop", "cogs.trading", "cogs.leaderboard", "cogs.owner"]:
            await self.load_extension(cog)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})", flush=True)
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash command(s)", flush=True)
        except Exception as e:
            print(f"Failed to sync commands: {e}", flush=True)


bot = MyBot()
bot.run(DISCORD_TOKEN)
