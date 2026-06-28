import discord
from discord import app_commands
from discord.ext import commands
from config import SHOP_CHANNEL_ID
from database import load_data, get_player, migrate_pets, pet_image_url

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

    @app_commands.command(name="flex", description="Flex your stats in the flex channel")
    async def flex(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(1515320625848123453)
        if not channel:
            await interaction.response.send_message("Flex channel not found.", ephemeral=True)
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
        await interaction.response.send_message("Flex posted! 💪", ephemeral=True)

    @app_commands.command(name="help", description="Show available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ COMMANDS ✦",
            description="All commands use `/` prefix",
            color=VIP_DARK
        )
        embed.add_field(name="💰 Economy", value="`/balance` `/daily` `/work` `/gamble` `/transfer`", inline=False)
        embed.add_field(name="🛒 Shop", value="`/shop` `/petshop`", inline=False)
        embed.add_field(name="🐾 Pets", value="`/mypets` `/activate`", inline=False)
        embed.add_field(name="🤝 Trading", value="`/sell`", inline=False)
        embed.add_field(name="📊 Leaderboard", value="`/lb` `/xplb` `/rank`", inline=False)
        embed.add_field(name="⚙️ Utility", value="`/ping` `/help` `/guide`", inline=False)
        embed.add_field(name="👑 Owner", value="`/addcoins` `/removecoins` `/setbalance` `/resetuser` `/broadcast` `/clear` `/giveaway` `/announcement`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        embed.add_field(name="4️⃣ Pets & XP", value="Activate your best pet with `/activate` — its multiplier boosts all earnings. You also earn **XP** by chatting and using commands!", inline=False)
        embed.add_field(name="5️⃣ Trade Pets", value="Use `/sell` to list pets for sale in the trading channel. Players can **Buy** or **Bargain**!", inline=False)
        embed.add_field(name="6️⃣ Climb the Ranks", value="Check `/lb` (coins) and `/xplb` (XP) to see the top 25 players. Daily leaderboards post automatically!", inline=False)
        embed.set_footer(text="Tip: Lucky Charms from /shop boost your gold pet chance!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(General(bot))
