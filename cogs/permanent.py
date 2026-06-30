import discord
from discord.ext import commands
import json
import os
import asyncio

GUIDE_CHANNEL_ID = 1499070331594477798
RULES_CHANNEL_ID = 1515328387294433390
DATA_DIR = "data"
MESSAGES_FILE = os.path.join(DATA_DIR, "permanent_messages.json")

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


def load_message_ids():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    return {"guide": None, "rules": None}


def save_message_ids(ids):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(MESSAGES_FILE, "w") as f:
        json.dump(ids, f, indent=2)


class PermanentMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready = False

    async def post_guide(self):
        channel = self.bot.get_channel(GUIDE_CHANNEL_ID)
        if not channel:
            return None
        return await channel.send(content="\u200b@everyone", embed=GUIDE_EMBED)

    async def post_rules(self):
        channel = self.bot.get_channel(RULES_CHANNEL_ID)
        if not channel:
            return None
        return await channel.send(content="\u200b@everyone", embed=RULES_EMBED)

    async def ensure_messages(self):
        ids = load_message_ids()
        changed = False
        tasks = []

        for key, channel_id, post_fn in [
            ("guide", GUIDE_CHANNEL_ID, self.post_guide),
            ("rules", RULES_CHANNEL_ID, self.post_rules),
        ]:
            msg_id = ids.get(key)
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue
            if msg_id:
                try:
                    msg = await channel.fetch_message(msg_id)
                    if msg:
                        continue
                except:
                    pass
            new_msg = await post_fn()
            if new_msg:
                ids[key] = new_msg.id
                changed = True

        if changed:
            save_message_ids(ids)

    @commands.Cog.listener()
    async def on_ready(self):
        if self.ready:
            return
        self.ready = True
        await asyncio.sleep(5)
        await self.ensure_messages()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        ids = load_message_ids()
        changed = False

        for key in ("guide", "rules"):
            if ids.get(key) == payload.message_id:
                channel = self.bot.get_channel(payload.channel_id)
                if not channel:
                    return
                if key == "guide":
                    new_msg = await self.post_guide()
                else:
                    new_msg = await self.post_rules()
                if new_msg:
                    ids[key] = new_msg.id
                    changed = True

        if changed:
            save_message_ids(ids)


async def setup(bot):
    await bot.add_cog(PermanentMessages(bot))
