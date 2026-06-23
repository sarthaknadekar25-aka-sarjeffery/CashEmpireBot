import discord
from discord import app_commands
from discord.ext import commands
from config import SHOP_CHANNEL_ID

VIP_DARK = discord.Color.from_rgb(30, 30, 35)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if SHOP_CHANNEL_ID and interaction.channel_id == SHOP_CHANNEL_ID:
            await interaction.response.send_message("This command can't be used in the shop channel.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 200 else discord.Color.orange() if latency < 500 else discord.Color.red()
        embed = discord.Embed(title="Pong!", description=f"**{latency}ms**", color=color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ COMMANDS ✦",
            description="All commands use `/` prefix",
            color=VIP_DARK
        )
        embed.add_field(name="💰 Economy", value="`/balance` `/daily` `/work` `/gamble` `/transfer`", inline=False)
        embed.add_field(name="🛒 Shop", value="`/shop` `/pets`", inline=False)
        embed.add_field(name="🏆 Leaderboard", value="`/leaderboard`", inline=False)
        embed.add_field(name="⚙️ Utility", value="`/ping` `/help`", inline=False)
        embed.add_field(name="👑 Owner", value="`/addcoins` `/removecoins` `/setbalance` `/resetuser` `/broadcast`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(General(bot))
