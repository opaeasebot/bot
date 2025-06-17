import disnake
from disnake.ext import commands
from datetime import datetime, timedelta, timezone
from Functions.CarregarEmojis import *
import json

async def AutoRole(member: disnake.Member):
    try:
        with open("Database/Server/cargos.json", "r") as f:
            db = json.load(f)
            cargo_id = db.get("membro", None)

        with open("Database/Server/boasvindas.json") as file:
            db2 = json.load(file)
            sistema = db2["funcoes"]["autoRole"]["membro"]
        
        if sistema == True:

            if cargo_id:
                cargo = member.guild.get_role(int(cargo_id))
                if cargo:
                    await member.add_roles(cargo, reason="[Ease Bot] Sistema de Auto Role")
                    return
                else:
                    return
            else:
                return
        
        else: return
    except: return

async def MensagemBoasVindas(member: disnake.Member):
    try:
        with open("Database/Server/canais.json") as canais:
            canaisdb = json.load(canais)
            canal_id = canaisdb["boasvindas"]

        with open("Database/Server/boasvindas.json", "r") as f:
            db = json.load(f)
            sistema_ativado = db["mensagens"]["boas-vindas"]["mensagem"]
        
        if sistema_ativado and canal_id:
            canal = member.guild.get_channel(int(canal_id))
            if canal:
                content = db["mensagens"]["boas-vindas"]["estiloMensagem"]["content"]
                deleteafter = db["mensagens"]["boas-vindas"]["tempoApagar"]

                if deleteafter == "":
                    deleteafter = None
                else: deleteafter = int(deleteafter)

                content_preview = (
                    content.replace("{mencao}", member.mention)
                    .replace("{nome}", member.name)
                    .replace("{servidor}", member.guild.name)
                )
                button = disnake.ui.Button(
                    label="Mensagem do Sistema",
                    style=disnake.ButtonStyle.gray,
                    disabled=True
                )

                await canal.send(content=content_preview, components=[button], delete_after=deleteafter)
            else:
                return
        else:
            return
    except: return

async def AntiFake(member: disnake.Member):
    try:
        with open("Database/Server/antifake.json") as f:
            db = json.load(f)

        with open("Database/Server/canais.json") as f2:
            db2 = json.load(f2)
        
        canal = db2["antifake"]
        if canal != "":
            canal = int(canal)
        else:
            canal = None
        
        if canal:
            channel = member.guild.get_channel(canal)

        quantidade_minima = db.get("quantidadeMinima", 0)
        nomes_bloqueados = db.get("nomesBloqueados", [])

        if quantidade_minima == "":
            quantidade_minima = 0
        else: quantidade_minima = int(quantidade_minima)

        if member.name in nomes_bloqueados:
            await member.send(f"Você foi expulso do servidor: ``{member.guild.name}``\nMotivo: ``Sistema de Anti Fake``")
            await member.kick(reason="[Ease Bot] Sistema de Anti Fake")
        elif member.display_name in nomes_bloqueados:
            await member.send(f"Você foi expulso do servidor: ``{member.guild.name}``\nMotivo: ``Sistema de Anti Fake``")
            await member.kick(reason="[Ease Bot] Sistema de Anti Fake")

        if quantidade_minima > 0:
            account_age = datetime.now(timezone.utc) - member.created_at
            account_age_days = account_age.days

            if account_age_days < quantidade_minima:
                await member.send(f"Você foi expulso do servidor: ``{member.guild.name}``\nMotivo: ``Sistema de Anti Fake``\nSua conta foi criada há menos de {quantidade_minima} dias.")
                await member.kick(reason="[Ease Bot] Sistema de Anti Fake - Conta nova demais")
        else:
            pass

        embed = disnake.Embed(
            title="Anti Fake | Expulsão",
            description="Uma pessoa foi expulsa por um valor definido no Anti-Fake.\nVeja abaixo as informações",
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.add_field(
            name="Quem foi expulso",
            value=f"{member.mention}\n({member.id})",
            inline=True
        )
        embed.add_field(
            name="Quando foi expulso?",
            value=f"<t:{int(datetime.now().timestamp())}:D>"
        )
        await channel.send(embed=embed)
    except: pass
    
class EventsOnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def MemberJoinListener(self, member: disnake.Member):
        await AutoRole(member)
        await MensagemBoasVindas(member)
        await AntiFake(member)

def setup(bot: commands.Bot):
    bot.add_cog(EventsOnMemberJoin(bot))
