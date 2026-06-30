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

VIP_DARK = discord.Color.from_rgb(30, 30, 35)

GUIDE_EMBED = discord.Embed(
    title="✦ HOW TO PLAY — CashEmpire ✦",
    description="Earn coins, collect pets, climb the leaderboard!",
    color=VIP_DARK
)
GUIDE_EMBED.add_field(name="1️⃣ Start Playing", value="Use `/daily` and `/work` to earn coins. You start with **100 coins**!", inline=False)
GUIDE_EMBED.add_field(name="2️⃣ Buy Boosters", value="Use `/shop` to buy 2x/5x boosters that multiply your earnings for 24h.", inline=False)
GUIDE_EMBED.add_field(name="3️⃣ Open Crates", value="Use `/petshop` to buy crates. Each crate has 5 pets with **1% chance** for a rare **Gold pet**!", inline=False)
GUIDE_EMBED.add_field(name="4️⃣ Pets & XP", value="Use `/mypets` to toggle your best pet ON — its multiplier boosts all earnings. You also earn **XP** by chatting and using commands!", inline=False)
GUIDE_EMBED.add_field(name="5️⃣ Buy & Sell Pets", value="Buy pets from `/petshop` crates. Sell unwanted pets using `/sell` in the trading channel — set a price or let players bargain!", inline=False)
GUIDE_EMBED.add_field(name="6️⃣ Climb the Ranks", value="Check `/lb` (coins) and `/xplb` (XP) to see the top 25 players. Daily leaderboards post automatically!", inline=False)
GUIDE_EMBED.add_field(name="7️⃣ Useful Commands", value="`/balance` `/daily` `/work` `/gamble` `/transfer` `/shop` `/petshop` `/mypets` `/sell` `/lb` `/xplb` `/rank` `/flex` `/guide` `/supportpanel`", inline=False)
GUIDE_EMBED.set_footer(text="Tip: Lucky Charms from /shop boost your gold pet chance!")

RULES_LIST = [
    "Be respectful to all members — no harassment, hate speech, or bullying.",
    "No spamming, flooding, or excessive use of emojis.",
    "Do not exploit, cheat, or abuse bugs. Report bugs instead.",
    "Do not use alternate accounts to gain unfair rewards.",
    "No begging for money, pets, or roles.",
    "Keep chats in the correct channels.",
    "No advertising or self-promotion without staff permission.",
    "Do not impersonate staff, developers, or other members.",
    "Follow all staff instructions. If you have an issue, open a support ticket.",
    "Have fun, play fair, and help make the community enjoyable for everyone.",
]
RULES_EMBED = discord.Embed(
    title="📜 CASH EMPIRE RULES",
    description="Please read and follow all rules to keep the community enjoyable.",
    color=VIP_DARK
)
for i, rule in enumerate(RULES_LIST, 1):
    RULES_EMBED.add_field(name=f"Rule {i}", value=rule, inline=False)
RULES_EMBED.set_footer(text="Violating rules may result in warnings, mutes, or bans.")


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


async def ensure_permanent_message(bot, channel_id, embed, key):
    channel = await bot.fetch_channel(channel_id)
    ids = load_ids()
    msg_id = ids.get(key)

    if msg_id:
        try:
            existing = await channel.fetch_message(msg_id)
            if existing:
                print(f"[Perm] {key} already exists (ID: {msg_id})", flush=True)
                return
        except:
            print(f"[Perm] {key} message deleted, re-posting", flush=True)

    try:
        msg = await channel.send(embed=embed)
        ids[key] = msg.id
        save_ids(ids)
        print(f"[Perm] {key} posted (ID: {msg.id})", flush=True)
    except Exception as e:
        print(f"[Perm] Failed to send {key}: {e}", flush=True)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

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
            await ensure_permanent_message(self, GUIDE_CHANNEL_ID, GUIDE_EMBED, "guide")
        except Exception as e:
            print(f"[Perm] Guide error: {e}", flush=True)
        try:
            await ensure_permanent_message(self, RULES_CHANNEL_ID, RULES_EMBED, "rules")
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
                        msg = await channel.send(embed=GUIDE_EMBED)
                    else:
                        msg = await channel.send(embed=RULES_EMBED)
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
