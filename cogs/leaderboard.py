import discord
from discord import app_commands
from discord.ext import commands, tasks
from config import LEADERBOARD_CHANNEL_ID, XP_LEADERBOARD_CHANNEL_ID
from database import load_data, save_data, get_player
from datetime import datetime, timezone, timedelta
import discord.utils
VIP_DARK = discord.Color.from_rgb(30, 30, 35)
GOLD = discord.Color.from_rgb(255, 215, 0)
SILVER = discord.Color.from_rgb(192, 192, 192)
BRONZE = discord.Color.from_rgb(205, 127, 50)

REWARD_AMOUNTS = {1: 1000, 2: 500, 3: 250}


def build_leaderboard_embed(data, bot, title, sort_key, top_n=25):
    players = [(uid, info) for uid, info in data.items()]
    players.sort(key=lambda x: sort_key(x[1]), reverse=True)
    players = players[:top_n]
    if not players:
        return discord.Embed(title=title, description="No data yet.", color=VIP_DARK)
    embed = discord.Embed(title=title, color=VIP_DARK)
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, (uid, info) in enumerate(players, 1):
        user = bot.get_user(int(uid))
        name = user.display_name if user else "Unknown"
        value = sort_key(info)
        prefix = medals.get(i, f"`#{i}`")
        if i == 1:
            embed.description = f"**👑 {name}** — {value}\n"
            embed.set_thumbnail(url=user.display_avatar.url if user else None)
        embed.add_field(name=f"{prefix} {name}", value=str(value), inline=True)
    embed.set_footer(text="Updated daily")
    return embed


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_leaderboard.start()

    def cog_unload(self):
        self.daily_leaderboard.cancel()

    async def post_leaderboards(self):
        data = load_data()
        coin_channel = self.bot.get_channel(LEADERBOARD_CHANNEL_ID)
        if coin_channel:
            top = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:3]
            for rank, (uid, info) in enumerate(top, 1):
                reward = REWARD_AMOUNTS.get(rank, 0)
                if reward:
                    get_player(data, int(uid))["balance"] += reward
            save_data(data)
            embed = build_leaderboard_embed(data, self.bot, "✦ COIN LEADERBOARD ✦", lambda p: p.get("balance", 0))
            msg = "🏆 **Daily rewards:** 🥇 1,000 | 🥈 500 | 🥉 250 coins"
            await coin_channel.send(msg, embed=embed)
        xp_channel = self.bot.get_channel(XP_LEADERBOARD_CHANNEL_ID)
        if xp_channel:
            embed = build_leaderboard_embed(data, self.bot, "✦ XP LEADERBOARD ✦", lambda p: p.get("xp", 0))
            await xp_channel.send(embed=embed)

    @tasks.loop(hours=24)
    async def daily_leaderboard(self):
        await self.post_leaderboards()

    @daily_leaderboard.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)
        next_run = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        await discord.utils.sleep_until(next_run)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        data = load_data()
        player = get_player(data, message.author.id)
        pet_mult = 1.0
        for pet in player.get("pets", []):
            if isinstance(pet, dict) and pet.get("active"):
                pet_mult = float(pet.get("multiplier", 1.0))
                break
        xp_gain = int(1 * pet_mult)
        player["xp"] = player.get("xp", 0) + xp_gain
        player["messages"] = player.get("messages", 0) + 1
        save_data(data)

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command):
        data = load_data()
        player = get_player(data, interaction.user.id)
        player["commands"] = player.get("commands", 0) + 1
        save_data(data)

    @app_commands.command(name="lb", description="Show coin leaderboard")
    async def lb(self, interaction: discord.Interaction):
        data = load_data()
        embed = build_leaderboard_embed(data, self.bot, "✦ COIN LEADERBOARD ✦", lambda p: p.get("balance", 0))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="xplb", description="Show XP leaderboard")
    async def xplb(self, interaction: discord.Interaction):
        data = load_data()
        embed = build_leaderboard_embed(data, self.bot, "✦ XP LEADERBOARD ✦", lambda p: p.get("xp", 0))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="rank", description="Check your XP rank")
    async def rank(self, interaction: discord.Interaction):
        data = load_data()
        players = [(uid, info) for uid, info in data.items()]
        players.sort(key=lambda x: x[1].get("xp", 0), reverse=True)
        rank = 1
        for uid, info in players:
            if int(uid) == interaction.user.id:
                break
            rank += 1
        player = get_player(data, interaction.user.id)
        embed = discord.Embed(title=f"Rank — {interaction.user.display_name}", color=VIP_DARK)
        embed.add_field(name="XP", value=f"**{player.get('xp', 0)}**")
        embed.add_field(name="Rank", value=f"**#{rank}**")
        embed.add_field(name="Messages", value=f"**{player.get('messages', 0)}**")
        embed.add_field(name="Commands", value=f"**{player.get('commands', 0)}**")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
