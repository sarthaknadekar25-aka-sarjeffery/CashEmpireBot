import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os
import random

DATA_FILE = "data/economy.json"
VIP_DARK = discord.Color.from_rgb(30, 30, 35)


def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_player(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "balance": 100,
            "last_daily": None,
            "multiplier_2x_expires": None,
            "multiplier_5x_expires": None,
            "pets": [],
            "inventory": {},
            "luck_boost": 0
        }
    return data[uid]


SHOP_ITEMS = [
    {"id": "2x_booster", "name": "2x Booster", "emoji": "🚀", "price": 500, "description": "Double earnings for 24h"},
    {"id": "5x_booster", "name": "5x Booster", "emoji": "💎", "price": 2000, "description": "5x earnings for 24h"},
    {"id": "mystery_box", "name": "Mystery Box", "emoji": "🎁", "price": 250, "description": "Open for 50-500 random coins"},
    {"id": "lucky_charm", "name": "Lucky Charm", "emoji": "🍀", "price": 1000, "description": "+0.5% gold pet luck (stacks)"},
    {"id": "hourglass", "name": "Hourglass", "emoji": "⏳", "price": 1500, "description": "Reset your daily cooldown"},
]


class ShopView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id
        for item in SHOP_ITEMS:
            btn = discord.ui.Button(
                label=f"{item['emoji']} {item['name']} — {item['price']} coins",
                style=discord.ButtonStyle.secondary,
                custom_id=f"buy_{item['id']}"
            )
            async def callback(interaction: discord.Interaction, item=item):
                if interaction.user.id != self.user_id:
                    await interaction.response.send_message("This isn't your shop menu.", ephemeral=True)
                    return
                data = load_data()
                player = get_player(data, interaction.user.id)
                if player["balance"] < item["price"]:
                    await interaction.response.send_message(f"You need **{item['price']} coins**. You have **{player['balance']}**.", ephemeral=True)
                    return
                player["balance"] -= item["price"]
                now = datetime.utcnow()
                embed = discord.Embed(title="Purchase Successful", color=discord.Color.green())
                if item["id"] == "2x_booster":
                    player["multiplier_2x_expires"] = (now + timedelta(hours=24)).isoformat()
                    embed.description = f"You bought **{item['emoji']} {item['name']}**"
                elif item["id"] == "5x_booster":
                    player["multiplier_5x_expires"] = (now + timedelta(hours=24)).isoformat()
                    embed.description = f"You bought **{item['emoji']} {item['name']}**"
                elif item["id"] == "mystery_box":
                    coins = random.randint(50, 500)
                    player["balance"] += coins
                    embed.description = f"You opened **{item['emoji']} Mystery Box** and got **{coins} coins**!"
                elif item["id"] == "lucky_charm":
                    player["luck_boost"] = player.get("luck_boost", 0) + 0.5
                    embed.description = f"You bought **{item['emoji']} Lucky Charm**! (+0.5% gold luck, total: {player['luck_boost']}%)"
                elif item["id"] == "hourglass":
                    player["last_daily"] = None
                    embed.description = f"You used **{item['emoji']} Hourglass**! Daily cooldown reset."
                embed.add_field(name="Balance", value=f"**{player['balance']} coins**")
                save_data(data)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            btn.callback = callback
            self.add_item(btn)


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Browse the shop")
    async def shop(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        embed = discord.Embed(title="✦ SHOP ✦", description=f"**Balance:** {player['balance']} coins\n─────────────", color=VIP_DARK)
        embed.set_footer(text="Click a button below to purchase")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        for item in SHOP_ITEMS:
            embed.add_field(name=f"{item['emoji']} {item['name']}", value=f"└ **{item['price']}** coins — {item['description']}", inline=False)
        embed.add_field(name="📦 Crates", value="Want pets? Use `/petshop` to open crates!", inline=False)
        view = ShopView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Shop(bot))
