import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime
from database import load_data, save_data, get_player, migrate_pets

VIP_DARK = discord.Color.from_rgb(30, 30, 35)
RARITY_COLORS = {
    "Common": discord.Color.from_rgb(150, 150, 150),
    "Uncommon": discord.Color.from_rgb(46, 204, 113),
    "Rare": discord.Color.from_rgb(52, 152, 219),
    "Epic": discord.Color.from_rgb(155, 89, 182),
    "Legendary": discord.Color.from_rgb(255, 215, 0),
    "Gold": discord.Color.from_rgb(255, 215, 0),
}
RARITY_XP = {"Common": 5, "Uncommon": 8, "Rare": 15, "Epic": 30, "Legendary": 50, "Gold": 100}

CRATES = [
    {
        "id": "woodland_crate", "name": "Woodland Crate", "emoji": "📦", "price": 800,
        "pets": [
            {"name": "Forest Spirit", "emoji": "🌿", "rarity": "Common", "mult_min": 1.1, "mult_max": 1.3, "weight": 35},
            {"name": "Water Turtle", "emoji": "🐢", "rarity": "Common", "mult_min": 1.1, "mult_max": 1.35, "weight": 30},
            {"name": "Sly Fox", "emoji": "🦊", "rarity": "Uncommon", "mult_min": 1.3, "mult_max": 1.6, "weight": 20},
            {"name": "Thorn Bear", "emoji": "🐻", "rarity": "Rare", "mult_min": 1.7, "mult_max": 2.2, "weight": 14},
            {"name": "Golden Stag", "emoji": "🦌", "rarity": "Gold", "mult_min": 3.5, "mult_max": 5.0, "weight": 1},
        ]
    },
    {
        "id": "inferno_crate", "name": "Inferno Crate", "emoji": "🔥", "price": 2000,
        "pets": [
            {"name": "Ember Fox", "emoji": "🦊", "rarity": "Uncommon", "mult_min": 1.3, "mult_max": 1.6, "weight": 30},
            {"name": "Flame Wolf", "emoji": "🐺", "rarity": "Rare", "mult_min": 1.7, "mult_max": 2.2, "weight": 28},
            {"name": "Lava Turtle", "emoji": "🐢", "rarity": "Rare", "mult_min": 1.8, "mult_max": 2.3, "weight": 25},
            {"name": "Fire Drake", "emoji": "🐉", "rarity": "Epic", "mult_min": 2.3, "mult_max": 3.0, "weight": 16},
            {"name": "Golden Phoenix", "emoji": "🔥", "rarity": "Gold", "mult_min": 4.0, "mult_max": 6.0, "weight": 1},
        ]
    },
    {
        "id": "celestial_crate", "name": "Celestial Crate", "emoji": "🌌", "price": 5000,
        "pets": [
            {"name": "Star Fox", "emoji": "🦊", "rarity": "Rare", "mult_min": 1.8, "mult_max": 2.3, "weight": 30},
            {"name": "Moon Panther", "emoji": "🐆", "rarity": "Epic", "mult_min": 2.3, "mult_max": 2.8, "weight": 28},
            {"name": "Cosmic Wolf", "emoji": "🐺", "rarity": "Epic", "mult_min": 2.5, "mult_max": 3.2, "weight": 25},
            {"name": "Void Dragon", "emoji": "🐉", "rarity": "Legendary", "mult_min": 3.0, "mult_max": 4.5, "weight": 16},
            {"name": "Golden Seraph", "emoji": "👼", "rarity": "Gold", "mult_min": 5.0, "mult_max": 8.0, "weight": 1},
        ]
    }
]





def open_crate(crate, luck_boost=0):
    pets = crate["pets"]
    gold_pet = next(p for p in pets if p["rarity"] == "Gold")
    gold_chance = gold_pet["weight"] + luck_boost
    normal_pets = [p for p in pets if p["rarity"] != "Gold"]
    normal_total = sum(p["weight"] for p in normal_pets)
    roll = random.uniform(0, normal_total + gold_chance)
    if roll < gold_chance:
        chosen = gold_pet
    else:
        cum = 0
        for p in normal_pets:
            cum += p["weight"]
            if roll < gold_chance + cum:
                chosen = p
                break
        else:
            chosen = normal_pets[-1]
    mult = round(random.uniform(chosen["mult_min"], chosen["mult_max"]), 2)
    return {
        "name": chosen["name"], "emoji": chosen["emoji"],
        "rarity": chosen["rarity"], "multiplier": mult, "active": False,
        "crate": crate["id"]
    }





class CrateSelect(discord.ui.Select):
    def __init__(self, user_id, bot):
        self.target_user = user_id
        self.bot = bot
        options = []
        for c in CRATES:
            options.append(discord.SelectOption(
                label=f"{c['name']} — {c['price']} coins",
                description=f"5 pets, 1% gold chance",
                value=c["id"],
                emoji=c["emoji"]
            ))
        super().__init__(placeholder="Choose a crate to open...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("This isn't your menu.", ephemeral=True)
            return
        crate_id = self.values[0]
        crate = next(c for c in CRATES if c["id"] == crate_id)
        data = load_data()
        player = get_player(data, interaction.user.id)
        if player["balance"] < crate["price"]:
            await interaction.response.send_message(f"You need **{crate['price']} coins**. You have **{player['balance']}**.", ephemeral=True)
            return
        player["balance"] -= crate["price"]
        luck = player.get("luck_boost", 0)
        pet = open_crate(crate, luck)
        xp_gain = RARITY_XP.get(pet["rarity"], 5)
        player.setdefault("xp", 0)
        player["xp"] += xp_gain
        player.setdefault("pets", []).append(pet)
        save_data(data)
        embed = discord.Embed(title="Crate Opened!", description=f"You opened **{crate['emoji']} {crate['name']}**", color=RARITY_COLORS.get(pet["rarity"], VIP_DARK))
        gold_text = " ⭐ **GOLD** ⭐" if pet["rarity"] == "Gold" else ""
        embed.add_field(name=f"{pet['emoji']} {pet['name']}{gold_text}", value=f"{pet['rarity']} | **{pet['multiplier']}x** | +{xp_gain} XP")
        embed.add_field(name="Balance", value=f"**{player['balance']}** coins")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        announce_rarities = {"Rare", "Epic", "Legendary", "Gold"}
        if pet["rarity"] in announce_rarities:
            channel = interaction.channel
            color_code = {"Rare": 0x3498DB, "Epic": 0x9B59B6, "Legendary": 0xFFD700, "Gold": 0xFFD700}
            name_style = {"Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary", "Gold": "🌟 GOLD 🌟"}
            announce = discord.Embed(
                title=f"🎉 {interaction.user.display_name} HAS PULLED {name_style[pet['rarity']]}! 🎉",
                description=f"{interaction.user.mention} got **{pet['emoji']} {pet['name']}** ({pet['multiplier']}x) from **{crate['emoji']} {crate['name']}**!",
                color=color_code.get(pet["rarity"], 0xFFD700)
            )
            announce.set_thumbnail(url=interaction.user.display_avatar.url)
            await channel.send(embed=announce)


class PetShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="petshop", description="Open crates to get pets")
    async def petshop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="✦ CRATE SHOP ✦", color=VIP_DARK)
        for c in CRATES:
            gold = next(p for p in c["pets"] if p["rarity"] == "Gold")
            embed.add_field(name=f"{c['emoji']} {c['name']} — {c['price']} coins", value=f"└ Includes **{gold['name']}** ({gold['mult_min']}x-{gold['mult_max']}x) at 1% chance", inline=False)
        view = discord.ui.View()
        view.add_item(CrateSelect(interaction.user.id, self.bot))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="mypets", description="View all your pets")
    async def mypets(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        pets = player.get("pets", [])
        if not pets:
            await interaction.response.send_message("You have no pets. Open crates in `/petshop`!", ephemeral=True)
            return
        embed = discord.Embed(title=f"Your Pets ({len(pets)})", color=VIP_DARK)
        for i, pet in enumerate(pets):
            active = " ⭐" if pet.get("active") else ""
            color_emoji = {"Common": "⬜", "Uncommon": "🟢", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡", "Gold": "🌟"}
            ce = color_emoji.get(pet.get("rarity", "Common"), "⬜")
            embed.add_field(name=f"[{i+1}] {pet.get('emoji', '🐾')} {pet['name']}{active}", value=f"{ce} {pet.get('rarity', 'Common')} | **{pet['multiplier']}x**", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="activate", description="Set your active pet")
    @app_commands.describe(number="Pet number from /mypets")
    async def activate(self, interaction: discord.Interaction, number: int):
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        pets = player.get("pets", [])
        if not pets:
            await interaction.response.send_message("You have no pets.", ephemeral=True)
            return
        if number < 1 or number > len(pets):
            await interaction.response.send_message(f"Choose 1-{len(pets)}.", ephemeral=True)
            return
        for i, pet in enumerate(pets):
            pet["active"] = (i == number - 1)
        save_data(data)
        pet = pets[number - 1]
        await interaction.response.send_message(f"**{pet['emoji']} {pet['name']}** is now active! (**{pet['multiplier']}x**)", ephemeral=True)


async def setup(bot):
    await bot.add_cog(PetShop(bot))
