import discord
from discord import app_commands
from discord.ext import commands
from config import TRADING_CHANNEL_ID
from database import load_data, save_data, get_player, migrate_pets, pet_image_url

VIP_DARK = discord.Color.from_rgb(30, 30, 35)
RARITY_COLORS = {
    "Common": discord.Color.from_rgb(150, 150, 150),
    "Uncommon": discord.Color.from_rgb(46, 204, 113),
    "Rare": discord.Color.from_rgb(52, 152, 219),
    "Epic": discord.Color.from_rgb(155, 89, 182),
    "Legendary": discord.Color.from_rgb(255, 215, 0),
    "Gold": discord.Color.from_rgb(255, 215, 0),
}





class SellPetSelect(discord.ui.Select):
    def __init__(self, user_id, pets):
        self.target_user = user_id
        options = []
        for i, pet in enumerate(pets):
            active = "⭐ " if pet.get("active") else ""
            options.append(discord.SelectOption(
                label=f"{active}{pet['name']} ({pet['rarity']})",
                description=f"{pet['multiplier']}x | #{i+1}",
                value=str(i),
                emoji=pet.get("emoji", "🐾")
            ))
        super().__init__(placeholder="Select a pet to sell...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        pet_idx = int(self.values[0])
        await interaction.response.send_modal(SellPriceModal(pet_idx))


class SellPriceModal(discord.ui.Modal, title="List Your Pet"):
    price = discord.ui.TextInput(label="Price in coins", placeholder="e.g. 500", min_length=1)

    def __init__(self, pet_idx):
        super().__init__()
        self.pet_idx = pet_idx

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price.value)
        except ValueError:
            await interaction.response.send_message("Enter a valid number.", ephemeral=True)
            return
        if price <= 0:
            await interaction.response.send_message("Price must be positive.", ephemeral=True)
            return
        channel = interaction.client.get_channel(TRADING_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Trading channel not configured.", ephemeral=True)
            return
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        pets = player.get("pets", [])
        if self.pet_idx >= len(pets):
            await interaction.response.send_message("Pet not found.", ephemeral=True)
            return
        pet = pets[self.pet_idx]
        sold = pets.pop(self.pet_idx)
        if sold.get("active") and pets:
            pets[0]["active"] = True
        save_data(data)
        rarity_colors = {"Common": 0x969696, "Uncommon": 0x2ECC71, "Rare": 0x3498DB, "Epic": 0x9B59B6, "Legendary": 0xFFD700, "Gold": 0xFFD700}
        embed = discord.Embed(
            title="🐾 PET LISTING",
            color=rarity_colors.get(sold["rarity"], 0x1E1E23)
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=pet_image_url(sold["name"], sold["rarity"]))
        embed.add_field(name="Pet", value=f"{sold.get('emoji', '🐾')} **{sold['name']}**", inline=True)
        embed.add_field(name="Rarity", value=sold["rarity"], inline=True)
        embed.add_field(name="Multiplier", value=f"**{sold['multiplier']}x**", inline=True)
        embed.add_field(name="Price", value=f"**{price}** coins", inline=False)
        embed.set_footer(text="Click Buy to purchase | Bargain to negotiate")
        view = TradeView(interaction.user.id, sold, price)
        msg = await channel.send(embed=embed, view=view)
        view.message = msg
        await interaction.response.send_message(f"✅ Listed **{sold['name']}** in {channel.mention} for **{price} coins**.", ephemeral=True)


class BargainModal(discord.ui.Modal, title="Make an Offer"):
    offer = discord.ui.TextInput(label="Your offer (coins)", placeholder="e.g. 300", min_length=1)

    def __init__(self, seller_id, pet_info, original_listing_id):
        super().__init__()
        self.seller_id = seller_id
        self.pet_info = pet_info
        self.original_listing_id = original_listing_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            offer = int(self.offer.value)
        except ValueError:
            await interaction.response.send_message("Enter a valid number.", ephemeral=True)
            return
        if offer <= 0:
            await interaction.response.send_message("Offer must be positive.", ephemeral=True)
            return
        data = load_data()
        buyer = get_player(data, interaction.user.id)
        if buyer["balance"] < offer:
            await interaction.response.send_message(f"You only have **{buyer['balance']} coins**.", ephemeral=True)
            return
        channel = interaction.client.get_channel(TRADING_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Trading channel error.", ephemeral=True)
            return
        embed = discord.Embed(
            title="💰 BARGAIN OFFER",
            description=f"{interaction.user.mention} offered **{offer} coins** for **{self.pet_info['emoji']} {self.pet_info['name']}**",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=pet_image_url(self.pet_info["name"], self.pet_info["rarity"]))
        embed.add_field(name="Pet", value=f"{self.pet_info['emoji']} {self.pet_info['name']}")
        embed.add_field(name="Rarity", value=self.pet_info["rarity"])
        embed.add_field(name="Multiplier", value=f"{self.pet_info['multiplier']}x")
        embed.set_footer(text=f"Buyer ID: {interaction.user.id}")
        view = BargainResponseView(self.seller_id, interaction.user.id, self.pet_info, offer, self.original_listing_id)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Offer of **{offer} coins** sent to the seller!", ephemeral=True)


class BargainResponseView(discord.ui.View):
    def __init__(self, seller_id, buyer_id, pet_info, offer, original_listing_id):
        super().__init__(timeout=300)
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.pet_info = pet_info
        self.offer = offer
        self.original_listing_id = original_listing_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.seller_id:
            await interaction.response.send_message("Only the seller can accept.", ephemeral=True)
            return
        data = load_data()
        seller = get_player(data, self.seller_id)
        buyer = get_player(data, self.buyer_id)
        if buyer["balance"] < self.offer:
            await interaction.response.send_message("Buyer doesn't have enough coins anymore.", ephemeral=True)
            self.disable_all()
            return
        seller["balance"] += self.offer
        buyer["balance"] -= self.offer
        pet = self.pet_info.copy()
        pet["active"] = False
        pet["crate"] = "traded"
        buyer.setdefault("pets", []).append(pet)
        save_data(data)
        embed = discord.Embed(title="✅ Offer Accepted", description=f"**{self.pet_info['emoji']} {self.pet_info['name']}** sold for **{self.offer} coins**", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            channel = interaction.guild.get_channel(TRADING_CHANNEL_ID)
            if channel and self.original_listing_id and self.original_listing_id != 0:
                try:
                    m = await channel.fetch_message(self.original_listing_id)
                    await m.edit(view=None)
                except Exception:
                    pass
        except Exception:
            pass
        self.disable_all()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.seller_id:
            await interaction.response.send_message("Only the seller can decline.", ephemeral=True)
            return
        await interaction.response.send_message("Offer declined.", ephemeral=True)
        self.disable_all()

    def disable_all(self):
        for child in self.children:
            child.disabled = True


class TradeView(discord.ui.View):
    def __init__(self, seller_id, pet_info, price):
        super().__init__(timeout=None)
        self.seller_id = seller_id
        self.pet_info = pet_info
        self.price = price

    def get_listing_id(self):
        return self.message.id if self.message else 0

    @discord.ui.button(label="Buy Now", style=discord.ButtonStyle.success, emoji="🛒")
    async def buy_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id == self.seller_id:
            await interaction.response.send_message("You can't buy your own listing.", ephemeral=True)
            return
        data = load_data()
        buyer = get_player(data, interaction.user.id)
        if buyer["balance"] < self.price:
            await interaction.response.send_message(f"You need **{self.price} coins**. You have **{buyer['balance']}**.", ephemeral=True)
            return
        seller = get_player(data, self.seller_id)
        seller["balance"] += self.price
        buyer["balance"] -= self.price
        pet = self.pet_info.copy()
        pet["active"] = False
        pet["crate"] = "traded"
        buyer.setdefault("pets", []).append(pet)
        save_data(data)
        embed = discord.Embed(title="✅ Purchase Complete", description=f"You bought **{self.pet_info['emoji']} {self.pet_info['name']}** for **{self.price} coins**", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            channel = interaction.guild.get_channel(TRADING_CHANNEL_ID)
            if channel and self.message:
                await self.message.edit(view=None)
        except Exception:
            pass

    @discord.ui.button(label="Bargain", style=discord.ButtonStyle.secondary, emoji="💬")
    async def bargain_button(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id == self.seller_id:
            await interaction.response.send_message("You can't bargain on your own listing.", ephemeral=True)
            return
        listing_id = self.get_listing_id()
        await interaction.response.send_modal(BargainModal(self.seller_id, self.pet_info, listing_id))


class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sell", description="List a pet for sale")
    async def sell(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(TRADING_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Trading channel not configured.", ephemeral=True)
            return
        data = load_data()
        player = get_player(data, interaction.user.id)
        migrate_pets(player)
        pets = player.get("pets", [])
        if not pets:
            await interaction.response.send_message("You have no pets to sell.", ephemeral=True)
            return
        non_active = [p for p in pets if not p.get("active")]
        if not non_active:
            await interaction.response.send_message("All your pets are active. Deactivate one first.", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(SellPetSelect(interaction.user.id, pets))
        await interaction.response.send_message("Select a pet to sell:", view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Trading(bot))
