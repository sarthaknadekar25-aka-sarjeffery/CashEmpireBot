import discord
from discord.ext import commands, tasks
from config import VOICE_FARM_CHANNEL_ID, VOICE_FARM_TEXT_CHANNEL_ID
from database import load_data, save_data, get_player
from datetime import datetime, timezone
import asyncio


class VoiceFarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_users = {}
        self.loop_count = 0
        self.voice_farm_loop.start()

    def cog_unload(self):
        self.voice_farm_loop.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if after.channel and after.channel.id == VOICE_FARM_CHANNEL_ID:
            info = {"joined": datetime.now(timezone.utc), "session_earned": 0, "message": None}
            self.vc_users[member.id] = info
            await self.send_panel(member, info)
        elif before.channel and before.channel.id == VOICE_FARM_CHANNEL_ID:
            info = self.vc_users.pop(member.id, None)
            if info and info["message"]:
                await self.stop_panel(member, info)

    async def send_panel(self, member, info):
        channel = self.bot.get_channel(VOICE_FARM_TEXT_CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title="🎧 AFK Farm",
            description=f"{member.mention} started farming!",
            color=discord.Color.from_rgb(30, 30, 35)
        )
        embed.add_field(name="⏱ Time", value="0m 0s", inline=True)
        embed.add_field(name="💰 Earned", value="0 coins", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text="2 coins per 10s | +100 coins every 10 min")
        msg = await channel.send(embed=embed)
        info["message"] = msg

    async def stop_panel(self, member, info):
        if not info["message"]:
            return
        delta = datetime.now(timezone.utc) - info["joined"]
        minutes = int(delta.total_seconds() // 60)
        seconds = int(delta.total_seconds() % 60)
        embed = discord.Embed(
            title="🎧 AFK Farm — Stopped",
            description=f"{member.mention} left the farm.",
            color=discord.Color.from_rgb(60, 60, 65)
        )
        embed.add_field(name="⏱ Duration", value=f"{minutes}m {seconds}s", inline=True)
        embed.add_field(name="💰 Earned", value=f"+{info['session_earned']} coins", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.set_footer(text="Come back anytime to farm more!")
        try:
            await info["message"].edit(embed=embed)
        except:
            pass

    @tasks.loop(seconds=10)
    async def voice_farm_loop(self):
        self.loop_count += 1
        vc = self.bot.get_channel(VOICE_FARM_CHANNEL_ID)
        if not vc:
            return
        current_ids = {m.id for m in vc.members if not m.bot}
        for uid in list(self.vc_users.keys()):
            if uid not in current_ids:
                info = self.vc_users.pop(uid, None)
                if info and info["message"]:
                    member = vc.guild.get_member(uid)
                    if member:
                        await self.stop_panel(member, info)
        for mid in current_ids:
            if mid not in self.vc_users:
                member = vc.guild.get_member(mid)
                if member:
                    info = {"joined": datetime.now(timezone.utc), "session_earned": 0, "message": None}
                    self.vc_users[mid] = info
                    await self.send_panel(member, info)
        if not self.vc_users:
            return

        data = load_data()
        is_bonus = self.loop_count % 60 == 0

        for uid in self.vc_users:
            player = get_player(data, uid)
            player["balance"] += 2
            self.vc_users[uid]["session_earned"] += 2
            if is_bonus:
                player["balance"] += 100
                self.vc_users[uid]["session_earned"] += 100

        save_data(data)

        channel = self.bot.get_channel(VOICE_FARM_TEXT_CHANNEL_ID)
        if not channel:
            return
        now = datetime.now(timezone.utc)
        for uid, info in list(self.vc_users.items()):
            if not info["message"]:
                continue
            member = vc.guild.get_member(uid)
            if not member:
                continue
            delta = now - info["joined"]
            minutes = int(delta.total_seconds() // 60)
            seconds = int(delta.total_seconds() % 60)
            session = info["session_earned"]
            embed = discord.Embed(
                title="🎧 AFK Farm",
                description=f"{member.mention} is farming!",
                color=discord.Color.from_rgb(30, 30, 35)
            )
            embed.add_field(name="⏱ Time", value=f"{minutes}m {seconds}s", inline=True)
            embed.add_field(name="💰 Earned", value=f"+{session} coins", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            bonus_count = int(delta.total_seconds()) // 600
            embed.set_footer(text=f"2 coins/10s | +100 coins every 10min | Bonuses: {bonus_count}")
            try:
                await info["message"].edit(embed=embed)
            except:
                pass

    @voice_farm_loop.before_loop
    async def before_farm(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)


async def setup(bot):
    await bot.add_cog(VoiceFarm(bot))
