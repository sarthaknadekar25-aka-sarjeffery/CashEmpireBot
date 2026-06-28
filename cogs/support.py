import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from config import GAME_SERVER_SUPPORT_CHANNEL_ID, MAIN_SERVER_FEEDBACK_CHANNEL_ID

_cooldowns = {}

SUPPORT_OPTIONS = [
    discord.SelectOption(label="Report a Bug", emoji="🐞", description="Report a bug or glitch", value="bug"),
    discord.SelectOption(label="Suggest an Idea", emoji="💡", description="Suggest a new feature or idea", value="suggest"),
    discord.SelectOption(label="Report a Player", emoji="⚠️", description="Report a player for breaking rules", value="report_player"),
    discord.SelectOption(label="General Feedback", emoji="⭐", description="Share your thoughts about the bot", value="feedback"),
    discord.SelectOption(label="Other", emoji="❓", description="Something else", value="other"),
]


class SupportModal(discord.ui.Modal, title="Submit to Support"):
    def __init__(self, support_type: str):
        super().__init__()
        self.support_type = support_type
        self.type_label = {
            "bug": "🐞 Report a Bug",
            "suggest": "💡 Suggest an Idea",
            "report_player": "⚠️ Report a Player",
            "feedback": "⭐ General Feedback",
            "other": "❓ Other",
        }.get(support_type, "❓ Other")

    title_input = discord.ui.TextInput(label="Title", placeholder="Brief summary of your submission", max_length=100, required=True)
    description = discord.ui.TextInput(label="Description", placeholder="Provide full details here...", style=discord.TextStyle.paragraph, max_length=2000, required=True)
    screenshot = discord.ui.TextInput(label="Screenshot Link (optional)", placeholder="https://...", max_length=500, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(MAIN_SERVER_FEEDBACK_CHANNEL_ID)
        if not channel:
            try:
                channel = await interaction.client.fetch_channel(MAIN_SERVER_FEEDBACK_CHANNEL_ID)
            except Exception:
                pass
        if not channel:
            await interaction.response.send_message("Bot is not in your main server. Use this link to invite it:\nhttps://discord.com/api/oauth2/authorize?client_id=1518885591587098694&permissions=8&scope=bot%20applications.commands", ephemeral=True)
            return
        embed = discord.Embed(
            title=self.type_label,
            color=discord.Color.from_rgb(30, 30, 35),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 User", value=f"{interaction.user.mention}\n`{interaction.user.id}`", inline=True)
        embed.add_field(name="🌐 Server", value=interaction.guild.name if interaction.guild else "DM", inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="📌 Title", value=self.title_input.value, inline=False)
        embed.add_field(name="📝 Description", value=self.description.value, inline=False)
        screenshot = self.screenshot.value.strip()
        if screenshot:
            embed.set_image(url=screenshot)
            embed.add_field(name="🖼️ Screenshot", value=screenshot, inline=False)
        embed.set_footer(text=f"Type: {self.support_type}")
        print(f"Support: channel={channel} type={type(channel).__name__} id={channel.id}", flush=True)
        try:
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Your submission has been sent successfully! The team will review it.", ephemeral=True)
        except Exception as e:
            print(f"Support submission failed: {e}", flush=True)
            await interaction.response.send_message(f"Error: `{e}`", ephemeral=True)


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
        await interaction.response.send_modal(SupportModal(self.values[0]))


class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportSelect())


SUPPORT_PANEL_EMBED = discord.Embed(
    title="✦ SUPPORT CENTER ✦",
    description="Select a category below to submit your request.\nOur team will review it as soon as possible.",
    color=discord.Color.from_rgb(30, 30, 35)
)
SUPPORT_PANEL_EMBED.add_field(name="🐞 Report a Bug", value="Found a glitch or something broken?", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="💡 Suggest an Idea", value="Have a feature in mind?", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="⚠️ Report a Player", value="Report someone breaking rules", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="⭐ General Feedback", value="Share your thoughts", inline=True)
SUPPORT_PANEL_EMBED.add_field(name="❓ Other", value="Something else?", inline=True)
SUPPORT_PANEL_EMBED.set_footer(text="This panel is permanent — select a category to begin.")


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
