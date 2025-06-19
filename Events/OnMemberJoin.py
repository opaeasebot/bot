import json
import disnake
from disnake.ext import commands
from disnake import ui, ButtonStyle, Embed, Member
from datetime import datetime, timezone

from Functions.CarregarEmojis import *
from Functions.Database import Database

class OnMemberJoin:
    @staticmethod
    async def AutoRole(member: Member):
        try:
            with open("Database/Server/cargos.json", "r") as f:
                cargos_db = json.load(f)
                cargo_id = cargos_db.get("membro")

            with open("Database/Server/boasvindas.json", "r") as f:
                boasvindas_db = json.load(f)
                sistema = boasvindas_db["funcoes"]["autoRole"]["membro"]

            if sistema and cargo_id:
                cargo = member.guild.get_role(int(cargo_id))
                if cargo:
                    await member.add_roles(cargo, reason="[Ease Bot] Sistema de Auto Role")
        except:
            return

    @staticmethod
    async def MensagemBoasVindas(member: Member):
        try:
            with open("Database/Server/canais.json", "r") as f:
                canais_db = json.load(f)
                canal_id = canais_db.get("boasvindas")

            with open("Database/Server/boasvindas.json", "r") as f:
                boasvindas_db = json.load(f)
                sistema_ativado = boasvindas_db["mensagens"]["boas-vindas"]["mensagem"]

            if not (sistema_ativado and canal_id):
                return

            canal = member.guild.get_channel(int(canal_id))
            if not canal:
                return

            estilo = boasvindas_db["mensagens"]["boas-vindas"]["estiloMensagem"]
            delete_after = boasvindas_db["mensagens"]["boas-vindas"]["tempoApagar"]
            delete_after = int(delete_after) if delete_after else None

            content = estilo["content"]
            content = (
                content.replace("{mencao}", member.mention)
                    .replace("{nome}", member.name)
                    .replace("{servidor}", member.guild.name)
            )

            button = ui.Button(
                label="Mensagem do Sistema",
                style=ButtonStyle.gray,
                disabled=True
            )

            await canal.send(content=content, components=[button], delete_after=delete_after)
        except:
            return

    @staticmethod
    async def AntiFake(member: Member):
        try:
            antifake_db = Database.Obter("Database/Server/antifake.json")
            canais_db = Database
            with open("Database/Server/canais.json", "r") as f:
                canais_db = json.load(f)

            canal_id = canais_db.get("antifake")
            canal_id = int(canal_id) if canal_id else None
            channel = member.guild.get_channel(canal_id) if canal_id else None

            quantidade_minima = antifake_db.get("quantidadeMinima", 0)
            quantidade_minima = int(quantidade_minima) if quantidade_minima else 0

            nomes_bloqueados = antifake_db.get("nomesBloqueados", [])

            if member.name in nomes_bloqueados or member.display_name in nomes_bloqueados:
                await member.send(f"Você foi expulso do servidor: `{member.guild.name}`\nMotivo: `Sistema de Anti Fake`")
                await member.kick(reason="[Ease Bot] Sistema de Anti Fake")

            if quantidade_minima > 0:
                dias = (datetime.now(timezone.utc) - member.created_at).days
                if dias < quantidade_minima:
                    await member.send(
                        f"Você foi expulso do servidor: `{member.guild.name}`\n"
                        f"Motivo: `Sistema de Anti Fake`\n"
                        f"Sua conta foi criada há menos de {quantidade_minima} dias."
                    )
                    await member.kick(reason="[Ease Bot] Sistema de Anti Fake - Conta nova demais")

            if channel:
                embed = Embed(
                    title="Anti Fake | Expulsão",
                    description="Uma pessoa foi expulsa por um valor definido no Anti-Fake.\nVeja abaixo as informações",
                    timestamp=datetime.now(),
                    color=disnake.Color(0x00FFFF)
                )
                embed.add_field(name="Quem foi expulso", value=f"{member.mention}\n({member.id})", inline=True)
                embed.add_field(name="Quando foi expulso?", value=f"<t:{int(datetime.now().timestamp())}:D>")
                await channel.send(embed=embed)
        except:
            pass


class EventsOnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def MemberJoinListener(self, member: Member):
        await OnMemberJoin.AutoRole(member)
        await OnMemberJoin.MensagemBoasVindas(member)
        await OnMemberJoin.AntiFake(member)


def setup(bot: commands.Bot):
    bot.add_cog(EventsOnMemberJoin(bot))
