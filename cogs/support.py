import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from config import GAME_SERVER_SUPPORT_CHANNEL_ID, MAIN_SERVER_FEEDBACK_CHANNEL_ID

_cooldowns = {}

SUPPORT_OPTIONS = [
    discord.SelectOption(label="Report a Bug", emoji="🐞", value="bug"),
    discord.SelectOption(label="Suggest an Idea", emoji="💡", value="suggest"),
    discord.SelectOption(label="Report a Player", emoji="⚠️", value="report_player"),
    discord.SelectOption(label="General Feedback", emoji="⭐", value="feedback"),
    discord.SelectOption(label="Other", emoji="❓", value="other"),
]
TYPE_LABELS = {
    "bug": "🐞 Report a Bug",
    "suggest": "💡 Suggest an Idea",
    "report_player": "⚠️ Report a Player",
    "feedback": "⭐ General Feedback",
    "other": "❓ Other",
}


class SubmitTicketButton(discord.ui.Button):
    def __init__(self, user_id, support_type, thread_id):
        self.target_user = user_id
        self.support_type = support_type
        self.thread_id = thread_id
        super().__init__(label="Submit Ticket", style=discord.ButtonStyle.success, emoji="✅")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your ticket.", ephemeral=True)
            return
        thread = interaction.guild.get_thread(self.thread_id)
        if not thread:
            await interaction.response.send_message("Thread not found.", ephemeral=True)
            return
        channel = interaction.client.get_channel(MAIN_SERVER_FEEDBACK_CHANNEL_ID)
        if not channel:
            try:
                channel = await interaction.client.fetch_channel(MAIN_SERVER_FEEDBACK_CHANNEL_ID)
            except Exception:
                pass
        if not channel:
            await interaction.response.send_message("Feedback channel not found.", ephemeral=True)
            return
        messages = []
        async for m in thread.history(limit=50, oldest_first=True):
            if m.author.id == interaction.client.user.id:
                continue
            messages.append(m)
        if not messages:
            await interaction.response.send_message("Write your message in the thread first!", ephemeral=True)
            return
        first = messages[0]
        embed = discord.Embed(
            title=TYPE_LABELS.get(self.support_type, "❓ Other"),
            color=discord.Color.from_rgb(30, 30, 35),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=first.author.display_name, icon_url=first.author.display_avatar.url)
        embed.add_field(name="👤 User", value=f"{first.author.mention}\n`{first.author.id}`", inline=True)
        embed.add_field(name="🌐 Server", value=first.guild.name if first.guild else "DM", inline=True)
        embed.add_field(name="", value="", inline=False)
        content = first.content or "*no text*"
        embed.add_field(name="📝 Message", value=content[:1024], inline=False)
        embed.set_footer(text=f"Type: {self.support_type}")
        files = []
        for m in messages:
            for a in m.attachments[:2]:
                try:
                    files.append(await a.to_file())
                except Exception:
                    pass
        try:
            await channel.send(embed=embed, files=files[:3] if files else None)
            await interaction.response.send_message("✅ Ticket submitted! Thank you.", ephemeral=True)
            await thread.edit(archived=True, locked=True)
            await thread.send("✅ Ticket submitted and closed.")
        except Exception as e:
            print(f"Ticket submit failed: {e}", flush=True)
            await interaction.response.send_message("Failed to submit. Try again.", ephemeral=True)


class CancelTicketButton(discord.ui.Button):
    def __init__(self, user_id, thread_id):
        self.target_user = user_id
        self.thread_id = thread_id
        super().__init__(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user:
            await interaction.response.send_message("Not your ticket.", ephemeral=True)
            return
        thread = interaction.guild.get_thread(self.thread_id)
        if thread:
            await thread.edit(archived=True, locked=True)
        await interaction.response.send_message("Ticket cancelled.", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self, user_id, support_type, thread_id):
        super().__init__(timeout=None)
        self.add_item(SubmitTicketButton(user_id, support_type, thread_id))
        self.add_item(CancelTicketButton(user_id, thread_id))


class SupportSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(custom_id="support_select", placeholder="Choose a support category...", options=SUPPORT_OPTIONS, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.utcnow().timestamp()
        last = _cooldowns.get(user_id, 0)
        if now - last < 120:
            remaining = int(120 - (now - last))
            await interaction.response.send_message(f"Please wait **{remaining}s** between submissions.", ephemeral=True)
            return
        _cooldowns[user_id] = now
        support_type = self.values[0]
        channel = interaction.channel
        thread = await channel.create_thread(
            name=f"{TYPE_LABELS.get(support_type, 'Support')} — {interaction.user.display_name}",
            type=discord.ChannelType.private_thread,
            reason="Support ticket"
        )
        await thread.add_user(interaction.user)
        embed = discord.Embed(
            title=TYPE_LABELS.get(support_type, "Support Ticket"),
            description="Type your message below and attach any screenshots.\nWhen you're done, click **Submit Ticket**.",
            color=discord.Color.from_rgb(30, 30, 35)
        )
        embed.add_field(name="📝 Instructions", value="1. Write your message in this thread\n2. Upload images directly (drag & drop or paste)\n3. Click **Submit Ticket** when done", inline=False)
        embed.set_footer(text="Your ticket will be forwarded to the team.")
        view = TicketView(interaction.user.id, support_type, thread.id)
        await thread.send(embed=embed, view=view)
        await interaction.response.send_message(f"📩 Ticket created! Check {thread.mention}", ephemeral=True)


class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportSelect())


SUPPORT_PANEL_EMBED = discord.Embed(
    title="✦ SUPPORT CENTER ✦",
    description="Select a category below to open a private ticket.\nType your message, attach images, then submit.",
    color=discord.Color.from_rgb(30, 30, 35)
)
SUPPORT_PANEL_EMBED.add_field(name="🐞 Report a Bug", value="Found a glitch?", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="💡 Suggest an Idea", value="Have a feature in mind?", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="⚠️ Report a Player", value="Report rule breakers", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="⭐ General Feedback", value="Share your thoughts", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="❓ Other", value="Something else?", inline=True)
SUPPORT_PANEL_EMBED.set_footer(text="Select a category — a private thread will open.")


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="supportpanel", description="Post the permanent support panel in this channel")
    async def supportpanel(self, interaction: discord.Interaction):
        if interaction.channel_id != GAME_SERVER_SUPPORT_CHANNEL_ID:
            await interaction.response.send_message(f"This command can only be used in the support channel.", ephemeral=True)
            return
        await interaction.channel.send(embed=SUPPORT_PANEL_EMBED, view=SupportView())
        await interaction.response.send_message("✅ Support panel posted!", ephemeral=True)


async def setup(bot):
    bot.add_view(SupportView())
    await bot.add_cog(Support(bot))
