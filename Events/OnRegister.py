import disnake
from disnake.ext import commands, tasks
from datetime import *
import json

from Functions.CarregarEmojis import *

def ObterDatabase():
    with open("Database/Server/canais.json") as f:
        db = json.load(f)
        return db

class EventsOnRegister(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.audit_task.start()

    def cog_unload(self):
        self.audit_task.cancel()

    @tasks.loop(seconds=10)
    async def audit_task(self):
        try:
            db = ObterDatabase()
            canal_id = db.get("registroauditoria", {})
            if not canal_id:
                return

            canal = self.bot.get_channel(int(canal_id))
            if not canal:
                return

            guild = self.bot.get_guild(canal.guild.id)
            if not guild:
                return

            try:
                async for entry in guild.audit_logs(limit=1):
                    if entry.created_at > datetime.now(tz=entry.created_at.tzinfo) - timedelta(seconds=10):  # Alteração recente
                        embed = disnake.Embed(
                            title="Alteração Detectada",
                            description="Este canal foi configurado para registrar alterações no servidor.",
                            timestamp=datetime.now(),
                            color=disnake.Color.orange()
                        )
                        embed.add_field(name="Mudança", value=f"**{entry.action.name.replace('_', ' ').title()}**", inline=False)
                        embed.add_field(name="Quem fez", value=f"{entry.user.mention}", inline=False)
                        embed.set_footer(text=f"ID: {entry.user.id}", icon_url=entry.user.display_avatar.url)

                        await canal.send(embed=embed)
            except Exception as e:
                print(f"Erro ao acessar o registro de auditoria: {e}")
        except: pass

    @audit_task.before_loop
    async def before_audit_task(self):
        await self.bot.wait_until_ready()

def setup(bot: commands.Bot):
    bot.add_cog(EventsOnRegister(bot))
