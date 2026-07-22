import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from config import SHOP_CHANNEL_ID
from database import load_data, get_player, migrate_pets, pet_image_url
from checks import check_bot_commands

VIP_DARK = discord.Color.from_rgb(30, 30, 35)


def _remaining(player, key):
    expires = player.get(key)
    if not expires:
        return None
    try:
        t = datetime.fromisoformat(expires)
        delta = t - datetime.utcnow()
        if delta.total_seconds() <= 0:
            return None
        h, r = divmod(int(delta.total_seconds()), 3600)
        m = r // 60
        return f"{h}h {m}m"
    except:
        return None


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await check_bot_commands(interaction)

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 200 else discord.Color.orange() if latency < 500 else discord.Color.red()
        embed = discord.Embed(title="Pong!", description=f"**{latency}ms**", color=color)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="flex", description="Flex your stats in the flex channel")
    async def flex(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(1515320625848123453)
        if not channel:
            await interaction.response.send_message("Flex channel not found.")
            return
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        active_pet = None
        for p in player.get("pets", []):
            if p.get("active"):
                active_pet = p
                break
        embed = discord.Embed(title=f"⚡ {interaction.user.display_name}'s Profile", color=discord.Color.from_rgb(30, 30, 35))
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Coins", value=f"**{player.get('balance', 0)}**", inline=True)
        embed.add_field(name="⭐ XP", value=f"**{player.get('xp', 0)}**", inline=True)
        embed.add_field(name="🐾 Pets", value=f"**{len(player.get('pets', []))}**", inline=True)
        if active_pet:
            embed.set_image(url=pet_image_url(active_pet["name"], active_pet["rarity"]))
            embed.add_field(name="Active Pet", value=f"{active_pet.get('emoji', '🐾')} **{active_pet['name']}** ({active_pet.get('rarity', 'Common')}) — **{active_pet['multiplier']}x**", inline=False)
        else:
            embed.set_image(url=pet_image_url("DefaultPet", "Common"))
        embed.add_field(name="📨 Messages", value=f"**{player.get('messages', 0)}**", inline=True)
        embed.add_field(name="⚙️ Commands", value=f"**{player.get('commands', 0)}**", inline=True)
        await channel.send(embed=embed)
        await interaction.response.send_message("Flex posted! 💪")

    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ COMMANDS ✦",
            description="All commands use `/` prefix",
            color=VIP_DARK
        )
        embed.add_field(name="💰 Economy", value="`/balance` `/daily` `/work` `/gamble` `/transfer`", inline=False)
        embed.add_field(name="🛒 Shop", value="`/shop`", inline=False)
        embed.add_field(name="🐾 Pets", value="`/mypets` `/petshop`", inline=False)
        embed.add_field(name="🤝 Trading", value="`/sell`", inline=False)
        embed.add_field(name="📊 Leaderboard", value="`/lb` `/xplb` `/rank`", inline=False)
        embed.add_field(name="⚡ Boosts", value="`/boost`", inline=False)
        embed.add_field(name="⚙️ Utility", value="`/ping` `/help` `/guide` `/supportpanel`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="guide", description="How to play CashEmpire")
    async def guide(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ HOW TO PLAY — CashEmpire ✦",
            description="Earn coins, collect pets, climb the leaderboard!",
            color=VIP_DARK
        )
        embed.add_field(name="1️⃣ Start Playing", value="Use `/daily` and `/work` to earn coins. You start with **100 coins**!", inline=False)
        embed.add_field(name="2️⃣ Buy Boosters", value="Use `/shop` to buy 2x/5x boosters that multiply your earnings for 24h.", inline=False)
        embed.add_field(name="3️⃣ Open Crates", value="Use `/petshop` to buy crates. Each crate has 5 pets with **1% chance** for a rare **Gold pet**!", inline=False)
        embed.add_field(name="4️⃣ Pets & XP", value="Use `/mypets` to toggle your best pet ON — its multiplier boosts all earnings. You also earn **XP** by chatting and using commands!", inline=False)
        embed.add_field(name="5️⃣ Trade Pets", value="Use `/sell` to list pets for sale in the trading channel. Players can **Buy** or **Bargain**!", inline=False)
        embed.add_field(name="6️⃣ Climb the Ranks", value="Check `/lb` (coins) and `/xplb` (XP) to see the top 25 players. Daily leaderboards post automatically!", inline=False)
        embed.set_footer(text="Tip: Lucky Charms from /shop boost your gold pet chance!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="boost", description="Check your active boosters and remaining time")
    async def boost(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        r2 = _remaining(player, "multiplier_2x_expires")
        r5 = _remaining(player, "multiplier_5x_expires")
        embed = discord.Embed(title=f"⚡ Boosts — {interaction.user.display_name}", color=VIP_DARK)
        if r5:
            embed.add_field(name="💎 5x Booster", value=f"Remaining: **{r5}**", inline=False)
        elif r2:
            embed.add_field(name="🚀 2x Booster", value=f"Remaining: **{r2}**", inline=False)
        else:
            embed.add_field(name="No Active Boosters", value="Buy one from `/shop`!", inline=False)
        pet_mult = 1.0
        active_names = []
        for pet in player.get("pets", []):
            if isinstance(pet, dict) and pet.get("active"):
                m = float(pet.get("multiplier", 1.0))
                if m > pet_mult:
                    pet_mult = m
                active_names.append(pet["name"])
        if pet_mult > 1.0:
            slots = player.get("equip_slots", 1)
            embed.add_field(name="🐾 Active Pet", value=f"**{', '.join(active_names)}** — {pet_mult}x | Slots: {slots}", inline=False)
        embed.set_footer(text="Boosters last 24 hours from purchase")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
