import discord
from discord import app_commands
from discord.ext import commands
import random
from database import load_data, save_data, get_player, migrate_pets, pet_image_url
from config import OWNER_ID

PETSHOP_CHANNEL_ID = 1499311029916536883
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
        "id": "woodland_crate", "name": "Woodland Crate", "emoji": "🌲", "price": 800,
        "pets": [
            {"name": "Red Fox", "emoji": "🦊", "rarity": "Common", "mult_min": 1.1, "mult_max": 1.3, "weight": 35},
            {"name": "Roe Deer", "emoji": "🦌", "rarity": "Common", "mult_min": 1.1, "mult_max": 1.35, "weight": 30},
            {"name": "Raccoon", "emoji": "🦝", "rarity": "Uncommon", "mult_min": 1.3, "mult_max": 1.6, "weight": 20},
            {"name": "Gray Wolf", "emoji": "🐺", "rarity": "Rare", "mult_min": 1.7, "mult_max": 2.2, "weight": 14},
            {"name": "Golden Eagle", "emoji": "🦅", "rarity": "Gold", "mult_min": 3.5, "mult_max": 5.0, "weight": 1},
        ]
    },
    {
        "id": "inferno_crate", "name": "Inferno Crate", "emoji": "🔥", "price": 2000,
        "pets": [
            {"name": "Desert Lizard", "emoji": "🦎", "rarity": "Common", "mult_min": 1.1, "mult_max": 1.35, "weight": 30},
            {"name": "Flamingo", "emoji": "🦩", "rarity": "Uncommon", "mult_min": 1.3, "mult_max": 1.6, "weight": 28},
            {"name": "Cheetah", "emoji": "🐆", "rarity": "Rare", "mult_min": 1.7, "mult_max": 2.2, "weight": 25},
            {"name": "Lion", "emoji": "🦁", "rarity": "Epic", "mult_min": 2.3, "mult_max": 3.0, "weight": 16},
            {"name": "Golden Python", "emoji": "🐍", "rarity": "Gold", "mult_min": 4.0, "mult_max": 6.0, "weight": 1},
        ]
    },
    {
        "id": "celestial_crate", "name": "Celestial Crate", "emoji": "🌙", "price": 5000,
        "pets": [
            {"name": "Arctic Hare", "emoji": "🐇", "rarity": "Common", "mult_min": 1.2, "mult_max": 1.4, "weight": 30},
            {"name": "Snowy Owl", "emoji": "🦉", "rarity": "Uncommon", "mult_min": 1.4, "mult_max": 1.7, "weight": 28},
            {"name": "Bengal Tiger", "emoji": "🐅", "rarity": "Rare", "mult_min": 1.8, "mult_max": 2.3, "weight": 25},
            {"name": "Snow Leopard", "emoji": "🐆", "rarity": "Epic", "mult_min": 2.5, "mult_max": 3.2, "weight": 16},
            {"name": "Golden Pheasant", "emoji": "🦚", "rarity": "Gold", "mult_min": 5.0, "mult_max": 8.0, "weight": 1},
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


class CrateButton(discord.ui.Button):
    def __init__(self, crate, user_id):
        self.purchase_crate = crate
        self.target_user = user_id
        super().__init__(label=f"  {crate['name']} — {crate['price']} coins", style=discord.ButtonStyle.secondary, emoji=crate["emoji"])

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        data = load_data()
        player = get_player(data, interaction.user.id)
        if player["balance"] < self.purchase_crate["price"]:
            await interaction.response.send_message(f"You need **{self.purchase_crate['price']} coins**. You have **{player['balance']}**.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        player["balance"] -= self.purchase_crate["price"]
        luck = player.get("luck_boost", 0)
        pet = open_crate(self.purchase_crate, luck)
        xp_gain = RARITY_XP.get(pet["rarity"], 5)
        player.setdefault("xp", 0)
        player["xp"] += xp_gain
        player.setdefault("pets", []).append(pet)
        save_data(data)
        embed = discord.Embed(title="Crate Opened!", description=f"You opened **{self.purchase_crate['emoji']} {self.purchase_crate['name']}**", color=RARITY_COLORS.get(pet["rarity"], VIP_DARK))
        gold_text = " ⭐ **GOLD** ⭐" if pet["rarity"] == "Gold" else ""
        embed.set_thumbnail(url=pet_image_url(pet["name"], pet["rarity"]))
        embed.add_field(name=f"{pet['emoji']} {pet['name']}{gold_text}", value=f"{pet['rarity']} | **{pet['multiplier']}x** | +{xp_gain} XP")
        embed.add_field(name="Balance", value=f"**{player['balance']}** coins")
        await interaction.followup.send(embed=embed, ephemeral=True)
        announce_rarities = {"Rare", "Epic", "Legendary", "Gold"}
        if pet["rarity"] in announce_rarities:
            channel = interaction.channel
            color_code = {"Rare": 0x3498DB, "Epic": 0x9B59B6, "Legendary": 0xFFD700, "Gold": 0xFFD700}
            name_style = {"Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary", "Gold": "🌟 GOLD 🌟"}
            announce = discord.Embed(
                title=f"🎉 {interaction.user.display_name} HAS PULLED {name_style[pet['rarity']]}! 🎉",
                description=f"{interaction.user.mention} got **{pet['emoji']} {pet['name']}** ({pet['multiplier']}x) from **{self.purchase_crate['emoji']} {self.purchase_crate['name']}**!",
                color=color_code.get(pet["rarity"], 0xFFD700)
            )
            announce.set_thumbnail(url=pet_image_url(pet["name"], pet["rarity"]))
            await channel.send(embed=announce)


PET_PER_PAGE = 5


class PetToggleButton(discord.ui.Button):
    def __init__(self, pet_idx, user_id, data_ref, view_ref):
        self.pet_idx = pet_idx
        self.target_user = user_id
        self.data_ref = data_ref
        self.view_ref = view_ref
        super().__init__(
            label=f"#{pet_idx + 1}",
            style=discord.ButtonStyle.primary,
            emoji=data_ref["pets"][pet_idx].get("emoji", "🐾")
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        pet = self.data_ref["pets"][self.pet_idx]
        if pet.get("active"):
            pet["active"] = False
        else:
            for p in self.data_ref["pets"]:
                p["active"] = False
            pet["active"] = True
        save_data(self.view_ref.data_ref)
        self.view_ref.build_page()
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)


class ActivateAllButton(discord.ui.Button):
    def __init__(self, user_id, data_ref, view_ref):
        self.target_user = user_id
        self.data_ref = data_ref
        self.view_ref = view_ref
        super().__init__(label="All Pets", style=discord.ButtonStyle.success, emoji="🌟")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        for p in self.data_ref["pets"]:
            p["active"] = True
        save_data(self.view_ref.data_ref)
        self.view_ref.build_page()
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)


class PrevPageButton(discord.ui.Button):
    def __init__(self, user_id, view_ref):
        self.target_user = user_id
        self.view_ref = view_ref
        super().__init__(emoji="◀️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        self.view_ref.page -= 1
        self.view_ref.build_page()
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)


class NextPageButton(discord.ui.Button):
    def __init__(self, user_id, view_ref):
        self.target_user = user_id
        self.view_ref = view_ref
        super().__init__(emoji="▶️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        self.view_ref.page += 1
        self.view_ref.build_page()
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)


class InventoryView(discord.ui.View):
    def __init__(self, user_id, pets, data_ref):
        super().__init__(timeout=120)
        self.target_user = user_id
        self.pets = pets
        self.data_ref = data_ref
        self.page = 0
        self.max_page = max(0, (len(pets) - 1) // PET_PER_PAGE)
        self.build_page()

    def build_page(self):
        self.clear_items()
        start = self.page * PET_PER_PAGE
        end = min(start + PET_PER_PAGE, len(self.pets))
        for idx in range(start, end):
            self.add_item(PetToggleButton(idx, self.target_user, self.data_ref, self))
        self.add_item(ActivateAllButton(self.target_user, self.data_ref, self))
        if self.page > 0:
            self.add_item(PrevPageButton(self.target_user, self))
        if self.page < self.max_page:
            self.add_item(NextPageButton(self.target_user, self))

    def get_embed(self):
        start = self.page * PET_PER_PAGE
        end = min(start + PET_PER_PAGE, len(self.pets))
        active = next((p for p in self.pets if p.get("active")), None)
        embed = discord.Embed(title=f"Your Pets ({len(self.pets)}) — Page {self.page + 1}/{self.max_page + 1}", color=VIP_DARK)
        if active:
            embed.set_thumbnail(url=pet_image_url(active["name"], active["rarity"]))
        for i in range(start, end):
            pet = self.pets[i]
            status = " ⭐ ACTIVE" if pet.get("active") else " ○ inactive"
            color_emoji = {"Common": "⬜", "Uncommon": "🟢", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡", "Gold": "🌟"}
            ce = color_emoji.get(pet.get("rarity", "Common"), "⬜")
            embed.add_field(name=f"[{i+1}] {pet.get('emoji', '🐾')} {pet['name']}{status}", value=f"{ce} {pet.get('rarity', 'Common')} | **{pet['multiplier']}x**", inline=False)
        embed.set_footer(text="Click a pet button to toggle | 🌟 All Pets activates every pet")
        return embed


class PetShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="petshop", description="Buy and open crates to get pets")
    async def petshop(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID and interaction.channel_id != PETSHOP_CHANNEL_ID:
            await interaction.response.send_message(f"This command can only be used in <#{PETSHOP_CHANNEL_ID}>.", ephemeral=True)
            return
        embed = discord.Embed(title="✦ CRATE SHOP ✦", color=VIP_DARK)
        for c in CRATES:
            gold = next(p for p in c["pets"] if p["rarity"] == "Gold")
            embed.add_field(name=f"{c['emoji']} {c['name']} — {c['price']} coins", value=f"└ Includes **{gold['name']}** ({gold['mult_min']}x-{gold['mult_max']}x) at 1% chance", inline=False)
        view = discord.ui.View()
        for c in CRATES:
            view.add_item(CrateButton(c, interaction.user.id))
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="mypets", description="View your pet inventory")
    async def mypets(self, interaction: discord.Interaction):
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        pets = player.get("pets", [])
        if not pets:
            await interaction.response.send_message("You have no pets. Open crates in `/petshop`!")
            return
        view = InventoryView(interaction.user.id, pets, data)
        await interaction.response.send_message(embed=view.get_embed(), view=view)


async def setup(bot):
    await bot.add_cog(PetShop(bot))
