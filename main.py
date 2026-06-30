import discord
from discord.ext import commands
import json
import os
import asyncio
from config import DISCORD_TOKEN, GUILD_ID

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

GUIDE_CHANNEL_ID = 1499070331594477798
RULES_CHANNEL_ID = 1515328387294433390
PERM_FILE = "data/permanent_messages.json"

GUIDE_TEXT = (
    "# ✦ HOW TO PLAY ✦\n"
    "Welcome to **CashEmpire** — earn coins, collect pets, climb to the top!\n\n"
    "## 💰 Earning\n"
    "`/daily` — daily reward\n"
    "`/work` — earn coins\n"
    "`/gamble` — risk it all\n"
    "`/shop` — buy 2x/5x boosters\n\n"
    "## 🐾 Pets\n"
    "`/petshop` — buy crates (1% gold pet!)\n"
    "`/mypets` — toggle active pet for multiplier\n\n"
    "## 📈 Progress\n"
    "`/rank` — your stats\n"
    "`/lb` — coin leaderboard\n"
    "`/xplb` — XP leaderboard\n\n"
    "## 🔄 Trading\n"
    "`/sell` — list pets for sale\n"
    "Trade in <#1518911361554321510>\n\n"
    "## 📋 All Commands\n"
    "`balance` `daily` `work` `gamble` `transfer` `shop` `petshop` `mypets` `sell` `lb` `xplb` `rank` `flex` `guide` `supportpanel`\n\n"
    "*Tip: having an active pet boosts ALL your earnings!*"
)

RULES_TEXT = (
    "# 📜 RULES\n\n"
    "**1.** Be respectful — no harassment, hate speech, or bullying.\n"
    "**2.** No spamming, flooding, or excessive emojis.\n"
    "**3.** No exploiting, cheating, or bug abuse.\n"
    "**4.** No alternate accounts for unfair rewards.\n"
    "**5.** No begging for money, pets, or roles.\n"
    "**6.** Keep chats in correct channels.\n"
    "**7.** No advertising without staff permission.\n"
    "**8.** Do not impersonate staff or members.\n"
    "**9.** Follow staff instructions.\n"
    "**10.** Have fun and play fair!\n\n"
    "*Violations may result in warnings, mutes, or bans.*"
)


def load_ids():
    try:
        if not os.path.exists("data"):
            os.makedirs("data", exist_ok=True)
        if os.path.exists(PERM_FILE):
            with open(PERM_FILE) as f:
                return json.load(f)
    except Exception as e:
        print(f"[Perm] load error: {e}", flush=True)
    return {"guide": None, "rules": None}


def save_ids(ids):
    try:
        if not os.path.exists("data"):
            os.makedirs("data", exist_ok=True)
        with open(PERM_FILE, "w") as f:
            json.dump(ids, f)
    except Exception as e:
        print(f"[Perm] save error: {e}", flush=True)


async def ensure_permanent_message(bot, channel_id, text, key):
    channel = await bot.fetch_channel(channel_id)
    ids = load_ids()
    msg_id = ids.get(key)

    if msg_id:
        try:
            existing = await channel.fetch_message(msg_id)
            if existing:
                await existing.delete()
                print(f"[Perm] Deleted old {key} (ID: {msg_id})", flush=True)
        except:
            print(f"[Perm] Old {key} not found, posting fresh", flush=True)

    try:
        msg = await channel.send(content=f"@everyone\n\n{text}")
        ids[key] = msg.id
        save_ids(ids)
        print(f"[Perm] {key} posted (ID: {msg.id})", flush=True)
    except Exception as e:
        print(f"[Perm] Failed to send {key}: {e}", flush=True)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True))

    async def setup_hook(self):
        for cog in ["cogs.economy", "cogs.welcome", "cogs.general", "cogs.shop", "cogs.pet_shop", "cogs.trading", "cogs.leaderboard", "cogs.owner", "cogs.support"]:
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

        await asyncio.sleep(5)
        print("[Perm] Posting permanent messages...", flush=True)
        try:
            await ensure_permanent_message(self, GUIDE_CHANNEL_ID, GUIDE_TEXT, "guide")
        except Exception as e:
            print(f"[Perm] Guide error: {e}", flush=True)
        try:
            await ensure_permanent_message(self, RULES_CHANNEL_ID, RULES_TEXT, "rules")
        except Exception as e:
            print(f"[Perm] Rules error: {e}", flush=True)

    async def on_raw_message_delete(self, payload):
        ids = load_ids()
        changed = False
        for key in ("guide", "rules"):
            if ids.get(key) == payload.message_id:
                try:
                    channel = await self.fetch_channel(payload.channel_id)
                    if key == "guide":
                        msg = await channel.send(content=f"@everyone\n\n{GUIDE_TEXT}")
                    else:
                        msg = await channel.send(content=f"@everyone\n\n{RULES_TEXT}")
                    ids[key] = msg.id
                    changed = True
                    print(f"[Perm] Re-posted {key} after delete", flush=True)
                except Exception as e:
                    print(f"[Perm] Failed to re-post {key}: {e}", flush=True)
        if changed:
            save_ids(ids)


bot = MyBot()
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in .env or Railway Variables")
bot.run(DISCORD_TOKEN)
