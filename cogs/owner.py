import discord
from discord import app_commands
from discord.ext import commands
from config import OWNER_ID, TRADING_CHANNEL_ID
import random
from database import load_data, save_data, get_player
VIP_DARK = discord.Color.from_rgb(30, 30, 35)





def owner_check():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Owner only.", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)


class GiveawayModal(discord.ui.Modal, title="Create Giveaway"):
    prize = discord.ui.TextInput(label="Prize (coins, pet name, or 'random')", placeholder="500")
    winners = discord.ui.TextInput(label="Number of winners", placeholder="1", default="1")
    duration = discord.ui.TextInput(label="Duration in minutes", placeholder="60", default="60")
    requirement = discord.ui.TextInput(label="Requirement (optional)", placeholder="e.g. Must have a pet", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            winner_count = int(self.winners.value)
            duration_min = int(self.duration.value)
        except ValueError:
            await interaction.response.send_message("Invalid numbers.", ephemeral=True)
            return
        prize_text = self.prize.value
        req_text = self.requirement.value or "None"
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize_text}\n**Winners:** {winner_count}\n**Duration:** {duration_min} min\n**Requirement:** {req_text}",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Click the button to enter!")
        view = GiveawayView(prize_text, winner_count, duration_min, req_text, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)


class GiveawayView(discord.ui.View):
    def __init__(self, prize, winner_count, duration_min, requirement, host_id):
        super().__init__(timeout=duration_min * 60)
        self.prize = prize
        self.winner_count = winner_count
        self.requirement = requirement
        self.host_id = host_id
        self.entrants = set()

    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, emoji="🎉")
    async def enter(self, interaction: discord.Interaction, btn: discord.ui.Button):
        self.entrants.add(interaction.user.id)
        await interaction.response.send_message("You entered the giveaway!", ephemeral=True)

    async def on_timeout(self):
        channel_id = None
        for c in self.children:
            if isinstance(c, discord.ui.Button):
                c.disabled = True
        if not self.entrants:
            return
        winners = random.sample(list(self.entrants), min(self.winner_count, len(self.entrants)))
        msg = f"🎉 **Giveaway over!** Winners: {', '.join(f'<@{w}>' for w in winners)} won **{self.prize}**"
        for guild in self.bot.guilds if hasattr(self, 'bot') else []:
            for channel in guild.text_channels:
                if channel.id:
                    try:
                        await channel.send(msg)
                    except Exception:
                        pass


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Owner only.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="addcoins", description="[Owner] Add coins to a player")
    async def addcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = load_data()
        player = get_player(data, member.id)
        player["balance"] += amount
        save_data(data)
        await interaction.response.send_message(f"Added **{amount} coins** to {member.mention}. Balance: **{player['balance']}**", ephemeral=True)

    @app_commands.command(name="removecoins", description="[Owner] Remove coins from a player")
    async def removecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = load_data()
        player = get_player(data, member.id)
        player["balance"] = max(0, player["balance"] - amount)
        save_data(data)
        await interaction.response.send_message(f"Removed **{amount} coins** from {member.mention}. Balance: **{player['balance']}**", ephemeral=True)

    @app_commands.command(name="setbalance", description="[Owner] Set a player's balance")
    async def setbalance(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = load_data()
        player = get_player(data, member.id)
        player["balance"] = max(0, amount)
        save_data(data)
        await interaction.response.send_message(f"Set {member.mention}'s balance to **{player['balance']} coins**", ephemeral=True)

    @app_commands.command(name="resetuser", description="[Owner] Reset a player's data")
    async def resetuser(self, interaction: discord.Interaction, member: discord.Member):
        data = load_data()
        uid = str(member.id)
        if uid in data:
            del data[uid]
            save_data(data)
        await interaction.response.send_message(f"Reset all data for {member.mention}.", ephemeral=True)

    @app_commands.command(name="broadcast", description="[Owner] Send a message to all channels")
    async def broadcast(self, interaction: discord.Interaction, message: str):
        sent = 0
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(f"📢 **Announcement:** {message}")
                        sent += 1
                except Exception:
                    pass
        await interaction.response.send_message(f"Sent to **{sent}** channels.", ephemeral=True)

    @app_commands.command(name="clear", description="[Owner] Clear messages in a channel")
    @app_commands.describe(amount="Number of messages to delete (max 200)")
    async def clear(self, interaction: discord.Interaction, amount: int = 200):
        amount = min(max(1, amount), 200)
        deleted = await interaction.channel.purge(limit=amount + 1)
        await interaction.response.send_message(f"Deleted **{len(deleted)-1}** messages.", ephemeral=True)

    @app_commands.command(name="giveaway", description="[Owner] Start a giveaway")
    async def giveaway(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GiveawayModal())

    @app_commands.command(name="announcement", description="[Owner] Send an announcement embed")
    @app_commands.describe(message="The announcement message")
    async def announcement(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(
            title="📢 ANNOUNCEMENT",
            description=message,
            color=discord.Color.from_rgb(212, 175, 55)
        )
        embed.set_footer(text=f"Posted by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="postguide", description="[Owner] Post the How to Play guide")
    async def postguide(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(1499070331594477798)
        if not channel:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return
        content = "\u200b@everyone"
        embed = discord.Embed(
            title="✦ HOW TO PLAY — CashEmpire ✦",
            description="Earn coins, collect pets, climb the leaderboard!",
            color=discord.Color.from_rgb(30, 30, 35)
        )
        embed.add_field(name="1️⃣ Start Playing", value="Use `/daily` and `/work` to earn coins. You start with **100 coins**!", inline=False)
        embed.add_field(name="2️⃣ Buy Boosters", value="Use `/shop` to buy 2x/5x boosters that multiply your earnings for 24h.", inline=False)
        embed.add_field(name="3️⃣ Open Crates", value="Use `/petshop` to buy crates. Each crate has 5 pets with **1% chance** for a rare **Gold pet**!", inline=False)
        embed.add_field(name="4️⃣ Pets & XP", value="Use `/mypets` to toggle your best pet ON — its multiplier boosts all earnings. You also earn **XP** by chatting and using commands!", inline=False)
        embed.add_field(name="5️⃣ Buy & Sell Pets", value="Buy pets from `/petshop` crates. Sell unwanted pets using `/sell` in the trading channel — set a price or let players bargain!", inline=False)
        embed.add_field(name="6️⃣ Climb the Ranks", value="Check `/lb` (coins) and `/xplb` (XP) to see the top 25 players. Daily leaderboards post automatically!", inline=False)
        embed.add_field(name="7️⃣ Useful Commands", value="`/balance` `/daily` `/work` `/gamble` `/transfer` `/shop` `/petshop` `/mypets` `/sell` `/lb` `/xplb` `/rank` `/flex` `/guide` `/supportpanel`", inline=False)
        embed.set_footer(text="Tip: Lucky Charms from /shop boost your gold pet chance!")
        await channel.send(content=content, embed=embed)
        await interaction.response.send_message("✅ Guide posted!", ephemeral=True)

    @app_commands.command(name="postrules", description="[Owner] Post the server rules")
    async def postrules(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(1515328387294433390)
        if not channel:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return
        content = "\u200b@everyone"
        embed = discord.Embed(
            title="📜 CASH EMPIRE RULES",
            description="Please read and follow all rules to keep the community enjoyable.",
            color=discord.Color.from_rgb(30, 30, 35)
        )
        rules = [
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
        for i, rule in enumerate(rules, 1):
            embed.add_field(name=f"Rule {i}", value=rule, inline=False)
        embed.set_footer(text="Violating rules may result in warnings, mutes, or bans.")
        await channel.send(content=content, embed=embed)
        await interaction.response.send_message("✅ Rules posted!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Owner(bot))
