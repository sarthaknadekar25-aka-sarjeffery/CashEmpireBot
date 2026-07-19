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
        self.status_message = None
        self.loop_count = 0
        self.voice_farm_loop.start()

    def cog_unload(self):
        self.voice_farm_loop.cancel()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if after.channel and after.channel.id == VOICE_FARM_CHANNEL_ID:
            self.vc_users[member.id] = {"joined": datetime.now(timezone.utc), "session_earned": 0}
            await self.announce_join(member)
        elif before.channel and before.channel.id == VOICE_FARM_CHANNEL_ID:
            self.vc_users.pop(member.id, None)

    async def announce_join(self, member):
        channel = self.bot.get_channel(VOICE_FARM_TEXT_CHANNEL_ID)
        if not channel:
            return
        await channel.send(f"{member.mention} joined AFK farm! 🎧")

    @tasks.loop(seconds=10)
    async def voice_farm_loop(self):
        self.loop_count += 1
        vc = self.bot.get_channel(VOICE_FARM_CHANNEL_ID)
        if not vc:
            return
        current_ids = {m.id for m in vc.members if not m.bot}
        for uid in list(self.vc_users.keys()):
            if uid not in current_ids:
                self.vc_users.pop(uid, None)
        for mid in current_ids:
            if mid not in self.vc_users:
                self.vc_users[mid] = {"joined": datetime.now(timezone.utc), "session_earned": 0}
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
        await self.update_status(vc)

    async def update_status(self, vc):
        channel = self.bot.get_channel(VOICE_FARM_TEXT_CHANNEL_ID)
        if not channel:
            return
        now = datetime.now(timezone.utc)
        lines = []
        total_session = 0
        for uid, info in list(self.vc_users.items()):
            member = vc.guild.get_member(uid)
            name = member.display_name if member else "Unknown"
            delta = now - info["joined"]
            minutes = int(delta.total_seconds() // 60)
            seconds = int(delta.total_seconds() % 60)
            session = info["session_earned"]
            total_session += session
            mention = member.mention if member else name
            lines.append(f"{mention} — {minutes}m {seconds}s — +{session} coins")
        lines.append("")
        lines.append("**2 coins per 10s** | **+100 coins every 10 min**")
        embed = discord.Embed(
            title="🎧 AFK Farm",
            description="\n".join(lines) if lines else "No one is farming.",
            color=discord.Color.from_rgb(30, 30, 35)
        )
        embed.set_footer(text=f"Total session earned: {total_session} coins")
        if self.status_message:
            try:
                await self.status_message.edit(embed=embed)
            except:
                self.status_message = await channel.send(embed=embed)
        else:
            self.status_message = await channel.send(embed=embed)

    @voice_farm_loop.before_loop
    async def before_farm(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)


async def setup(bot):
    await bot.add_cog(VoiceFarm(bot))
