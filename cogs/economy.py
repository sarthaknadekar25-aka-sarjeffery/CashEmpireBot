import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta
from config import SHOP_CHANNEL_ID
from database import load_data, save_data, get_player, migrate_pets
from checks import check_bot_commands
VIP_DARK = discord.Color.from_rgb(30, 30, 35)
ACCENT = discord.Color.from_rgb(212, 175, 55)


def get_active_multiplier(player):
    now = datetime.utcnow()
    if player.get("multiplier_5x_expires"):
        expires = datetime.fromisoformat(player["multiplier_5x_expires"])
        if now < expires:
            return 5
    if player.get("multiplier_2x_expires"):
        expires = datetime.fromisoformat(player["multiplier_2x_expires"])
        if now < expires:
            return 2
    return 1


def get_active_pet_multiplier(player):
    best = 1.0
    for pet in player.get("pets", []):
        if isinstance(pet, str):
            continue
        if pet.get("active"):
            mult = float(pet.get("multiplier", 1.0))
            if mult > best:
                best = mult
    return best


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await check_bot_commands(interaction)

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = load_data()
        player = get_player(data, member.id)
        booster_mult = get_active_multiplier(player)
        pet_mult = get_active_pet_multiplier(player)
        embed = discord.Embed(title=f"Wallet — {member.display_name}", color=VIP_DARK)
        embed.add_field(name="Coins", value=f"**{player['balance']}**", inline=True)
        embed.add_field(name="Booster", value=f"**{booster_mult}x**", inline=True)
        embed.add_field(name="Pet", value=f"**{pet_mult}x**", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        now = datetime.utcnow()
        if player["last_daily"]:
            last = datetime.fromisoformat(player["last_daily"])
            if now - last < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last)
                hours, rem = divmod(remaining.seconds, 3600)
                minutes = rem // 60
                await interaction.response.send_message(f"You already claimed your daily. Come back in **{hours}h {minutes}m**.")
                return
        base = random.randint(50, 150)
        booster_mult = get_active_multiplier(player)
        pet_mult = get_active_pet_multiplier(player)
        total = int(base * booster_mult * pet_mult)
        player["balance"] += total
        player["last_daily"] = now.isoformat()
        save_data(data)
        embed = discord.Embed(title="Daily Reward", description=f"+ **{total} coins**", color=VIP_DARK)
        embed.add_field(name="Base", value=str(base), inline=True)
        embed.add_field(name="Booster", value=f"{booster_mult}x", inline=True)
        embed.add_field(name="Pet", value=f"{pet_mult}x", inline=True)
        embed.add_field(name="Balance", value=f"**{player['balance']}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn coins")
    async def work(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        base = random.randint(10, 50)
        booster_mult = get_active_multiplier(player)
        pet_mult = get_active_pet_multiplier(player)
        total = int(base * booster_mult * pet_mult)
        player["balance"] += total
        save_data(data)
        jobs = ["Programmer", "Chef", "Farmer", "Miner", "Builder", "Pilot", "Doctor", "Streamer"]
        job = random.choice(jobs)
        embed = discord.Embed(title="Work Complete", description=f"You worked as **{job}**", color=VIP_DARK)
        embed.add_field(name="Earned", value=f"{base} coins", inline=True)
        embed.add_field(name="Booster", value=f"{booster_mult}x", inline=True)
        embed.add_field(name="Pet", value=f"{pet_mult}x", inline=True)
        embed.add_field(name="Total", value=f"**+{total}**", inline=False)
        embed.add_field(name="Balance", value=f"**{player['balance']}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gamble", description="Gamble your coins")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        data = load_data()
        player = get_player(data, interaction.user.id)
        if amount <= 0:
            await interaction.response.send_message("Bet a positive amount.")
            return
        if player["balance"] < amount:
            await interaction.response.send_message("You don't have enough coins.")
            return
        roll = random.randint(1, 100)
        if roll <= 45:
            player["balance"] -= amount
            title, color, text = "You Lost", discord.Color.red(), f"-{amount}"
        elif roll <= 90:
            player["balance"] += amount
            title, color, text = "You Won", discord.Color.green(), f"+{amount}"
        else:
            win = amount * 2
            player["balance"] += win
            title, color, text = "JACKPOT", ACCENT, f"+{win}"
        save_data(data)
        embed = discord.Embed(title=title, description=text, color=color)
        embed.add_field(name="Balance", value=f"**{player['balance']}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="transfer", description="Transfer coins to another player")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = load_data()
        sender = get_player(data, interaction.user.id)
        if amount <= 0:
            await interaction.response.send_message("Transfer a positive amount.")
            return
        if sender["balance"] < amount:
            await interaction.response.send_message("You don't have enough coins.")
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message("You can't transfer to yourself.")
            return
        receiver = get_player(data, member.id)
        sender["balance"] -= amount
        receiver["balance"] += amount
        save_data(data)
        embed = discord.Embed(title="Transfer Complete", description=f"Sent {amount} coins to {member.mention}", color=VIP_DARK)
        embed.add_field(name="Your Balance", value=f"**{sender['balance']}**")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
