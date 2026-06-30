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

    @app_commands.command(name="announcement", description="[Owner] Send a clean announcement")
    @app_commands.describe(title="Big announcement title", subtitle="Subtitle or tagline (optional)", description="Main message — use # ## for big text (optional)", event="Event type (optional)", location="Where (optional)", time="When (optional)", footer="Small footer text (optional)")
    async def announcement(self, interaction: discord.Interaction, title: str = "📢 ANNOUNCEMENT", subtitle: str = None, description: str = None, event: str = None, location: str = None, time: str = None, footer: str = None):
        desc_parts = []
        if subtitle:
            desc_parts.append(f"### {subtitle}")
        if description:
            desc_parts.append(description)

        embed = discord.Embed(
            title=title,
            description="\n\n".join(desc_parts) if desc_parts else None,
            color=discord.Color.from_rgb(212, 175, 55)
        )
        if event:
            embed.add_field(name="▸ Event", value=event, inline=True)
        if location:
            embed.add_field(name="▸ Location", value=location, inline=True)
        if time:
            embed.add_field(name="▸ Time", value=time, inline=True)
        if event or location or time:
            embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text=footer or f"Posted by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="permcheck", description="[Owner] Check bot permissions in channels")
    async def permcheck(self, interaction: discord.Interaction):
        channels = {
            "Guide": 1499070331594477798,
            "Rules": 1515328387294433390,
            "Bot Commands": 1499070938367660083,
            "Support Panel": 1520760975995699410,
            "Feedback": 1488847189471133827,
        }
        lines = []
        for name, cid in channels.items():
            ch = interaction.client.get_channel(cid)
            if not ch:
                try:
                    ch = await interaction.client.fetch_channel(cid)
                except:
                    lines.append(f"❌ {name} — channel not found")
                    continue
            me = ch.guild.me if ch.guild else None
            if not me:
                lines.append(f"❌ {name} — not in guild")
                continue
            perms = ch.permissions_for(me)
            can_send = perms.send_messages
            can_read = perms.read_messages
            can_mention = perms.mention_everyone
            can_embed = perms.embed_links
            status = "✅" if (can_send and can_read) else "❌"
            lines.append(f"{status} {name} — Send:{can_send} Read:{can_read} Embed:{can_embed} Mention:{can_mention}")
        embed = discord.Embed(title="🔍 Permission Check", description="\n".join(lines), color=discord.Color.from_rgb(30, 30, 35))
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Owner(bot))
