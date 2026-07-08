import discord
from discord.ext import commands
from config import WELCOME_CHANNEL_ID, LEAVE_CHANNEL_ID, GUILD_ID
from datetime import datetime

VIP_DARK = discord.Color.from_rgb(30, 30, 35)


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != GUILD_ID:
            return
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return
        member_count = len(member.guild.members)
        created_at = discord.utils.format_dt(member.created_at, style="F")
        embed = discord.Embed(
            title="✦ WELCOME ✦",
            description=(
                f"{member.mention} joined **{member.guild.name}**\n\n"
                f"👤 You are member **#{member_count}**\n"
                f"📅 Account created: {created_at}"
            ),
            color=VIP_DARK
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Use /help to see all commands")
        await channel.send(embed=embed)

        role = discord.utils.get(member.guild.roles, name="Member")
        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != GUILD_ID:
            return
        channel = self.bot.get_channel(LEAVE_CHANNEL_ID)
        if not channel:
            return
        member_count = len(member.guild.members)
        joined_at = discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "Unknown"
        embed = discord.Embed(
            title="✦ GOODBYE ✦",
            description=(
                f"{member.display_name} left **{member.guild.name}**\n\n"
                f"👤 **{member_count}** members remaining\n"
                f"📅 Was here since: {joined_at}"
            ),
            color=discord.Color.from_rgb(40, 40, 45)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
