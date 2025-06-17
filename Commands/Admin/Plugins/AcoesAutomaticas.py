import disnake
import json
from disnake.ext import commands
from disnake import *
from Functions.CarregarEmojis import *
from datetime import datetime

# modais para alterar
class Modals():
    class AlterarLimpezaModal(disnake.ui.Modal):
        def __init__(self):
            db = ObterDatabase()
            limpeza = db["limpeza"]

            components = [
                disnake.ui.TextInput(
                    label="IDs dos canais para limpar (linha)",
                    placeholder="Deixe em branco para desativar, serve para todos os campos.",
                    custom_id="idscanais",
                    style=TextInputStyle.long,
                    required=False,
                    value="\n".join(limpeza["canal"])
                ),
                disnake.ui.TextInput(
                    label="Delay da limpeza",
                    placeholder="Calculado em minutos",
                    custom_id="delay",
                    style=TextInputStyle.short,
                    required=False,
                    value=limpeza["delay"]
                ),
            ]
            super().__init__(title="Configurar Limpeza", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            canais = inter.text_values["idscanais"]
            delay = inter.text_values["delay"]

            try:
                delay = int(delay)
            except:
                embed, components = Panels.ObterPainelLimpeza(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{negativo} Não foi possível transformar o delay em minutos.", ephemeral=True, delete_after=3)
                return
            
            canais2 = []
            for canal in canais.split("\n"):
                try:
                    canal = inter.guild.get_channel(int(canal))
                    if canal:
                        canais2.append(canal.id)
                    else: pass
                except: pass


            db = ObterDatabase()
            db["limpeza"]["canal"] = canais2
            db["limpeza"]["delay"] = int(delay) if delay else None

            with open("Database/Server/acoesauto.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = Panels.ObterPainelLimpeza(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

    class AlterarMensagensModal(disnake.ui.Modal):
        def __init__(self):
            db = ObterDatabase()
            mensagens = db["mensagens"]

            components = [
                disnake.ui.TextInput(
                    label="IDs dos canais para mensagens (linha)",
                    placeholder="Deixe em branco para desativar, serve para todos os campos.",
                    custom_id="idscanais",
                    style=TextInputStyle.long,
                    required=False,
                    value="\n".join(mensagens["canal"]) if mensagens["canal"] else ""
                ),
                disnake.ui.TextInput(
                    label="Delay das mensagens",
                    placeholder="Calculado em minutos",
                    custom_id="delay",
                    style=TextInputStyle.short,
                    required=False,
                    value=str(mensagens["delay"]) if mensagens["delay"] else ""
                ),
                disnake.ui.TextInput(
                    label="Conteúdo da mensagem",
                    placeholder="Conteúdo da mensagem automática",
                    custom_id="content",
                    style=TextInputStyle.long,
                    required=False,
                    value=mensagens["content"]
                ),
            ]
            super().__init__(title="Configurar Mensagens Automáticas", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            canais = inter.text_values["idscanais"]
            delay = inter.text_values["delay"]
            content = inter.text_values["content"]

            try:
                delay = int(delay) if delay else None
            except ValueError:
                embed, components = Panels.ObterPainelLimpeza(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{negativo} Não foi possível transformar o delay em minutos.", ephemeral=True, delete_after=3)
                return

            canais = canais.split("\n") if canais else []

            db = ObterDatabase()
            db["mensagens"]["canal"] = canais
            db["mensagens"]["delay"] = delay
            db["mensagens"]["content"] = content

            with open("Database/Server/acoesauto.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = Panels.ObterPainelMensagens(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

    class AlterarReacaoModal(disnake.ui.Modal):
        def __init__(self):
            db = ObterDatabase()
            reacoes = db["reacoes"]

            components = [
                disnake.ui.TextInput(
                    label="IDs dos canais para reações (linha)",
                    placeholder="Deixe em branco para desativar, serve para todos os campos.",
                    custom_id="idscanais",
                    style=TextInputStyle.long,
                    required=False,
                    value="\n".join(reacoes["canal"])
                ),
                disnake.ui.TextInput(
                    label="Emoji da reação",
                    placeholder="🎈 ou <:emoji:123456789101112>",
                    custom_id="emoji",
                    style=TextInputStyle.short,
                    required=False,
                    value=reacoes["emoji"]
                ),
            ]
            super().__init__(title="Configurar Reações Automáticas", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            
            canais = inter.text_values["idscanais"]
            emoji = inter.text_values["emoji"]

            if canais:
                canais = canais.split("\n")
            else:
                canais = []

            if not emoji:
                emoji = ""

            db = ObterDatabase()
            db["reacoes"]["canal"] = canais
            db["reacoes"]["emoji"] = emoji

            with open("Database/Server/acoesauto.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = Panels.ObterPainelReacoes(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

# para facilitar o processo
def ObterDatabase():
    with open("Database/Server/acoesauto.json") as f:
        db = json.load(f)
    return db

class Panels():
    def ObterPainelRepostagem(inter: disnake.MessageInteraction):
        db = ObterDatabase()
        repostagem = db["repostagem"]
        sistema = repostagem["sistema"]

        sistemaText = f"{positivo} ``Habilitado``" if sistema else f"{negativo} ``Desabilitado``"
        Button = {
            "Label": "Desabilitar" if sistema else "Habilitar",
            "Style": disnake.ButtonStyle.red if sistema else disnake.ButtonStyle.green,
        }

        embed = disnake.Embed(
            title="Repostagem | Ações Automáticas",
            description=f"""
    Seu EBot vai repostar seus produtos periodicamente (a cada 3 horas), apagando a mensagem antiga e enviando-a novamente, para evitar denúncias nas mensagens.
    **Observação:** O sistema ajustará automaticamente o intervalo e a frequência dos reposts, considerando o fluxo de interações e a quantidade de produtos postados.
        """,
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Sistema", value=sistemaText)

        components = [
            disnake.ui.Button(label=Button["Label"], style=Button["Style"], emoji=reload, custom_id="AtivarDesativarSistemaAcoesAuto_repostagem"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarAcoesAutomaticas"),
        ]

        return embed, components

    def ObterPainelLimpeza(inter: disnake.MessageInteraction):
        db = ObterDatabase()
        limpeza = db["limpeza"]
        sistema = limpeza["sistema"]
        canal = limpeza["canal"]
        delay = limpeza["delay"]

        if canal:
            canais_formatados = ""
            for canal_id in canal:
                channel = inter.guild.get_channel(int(canal_id))
                if channel:
                    canais_formatados += f"{channel.mention}\n"
                else:
                    canais_formatados += f"{negativo} ``Canal não encontrado``\n"
        else:
            canais_formatados = f"{negativo} ``Não definido``"

        if delay: delay = f"{positivo} ``{delay} minutos``"
        else: delay = f"{negativo} ``Não definido``"

        sistemaText = f"{positivo} ``Habilitado``" if sistema else f"{negativo} ``Desabilitado``"
        Button = {
            "Label": "Desabilitar" if sistema else "Habilitar",
            "Style": disnake.ButtonStyle.red if sistema else disnake.ButtonStyle.green,
        }

        embed = disnake.Embed(
            title="Limpeza | Ações Automáticas",
            description=f"""
    Seu EBot realizará a limpeza automática das mensagens nos canais selecionados por você, conforme o horário estabelecido.
        """,
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Sistema", value=sistemaText, inline=True)
        embed.add_field(name="Delay", value=delay, inline=True)
        embed.add_field(name="Canais", value=canais_formatados, inline=False)

        components = [
            disnake.ui.Button(label=Button["Label"], style=Button["Style"], emoji=reload, custom_id="AtivarDesativarSistemaAcoesAuto_limpeza"),
            disnake.ui.Button(label="Configurar", style=disnake.ButtonStyle.blurple, emoji=editar, custom_id="ConfigurarSistemaLimpeza"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarAcoesAutomaticas"),
        ]

        return embed, components

    def ObterPainelMensagens(inter: disnake.MessageInteraction):
        db = ObterDatabase()
        mensagens = db["mensagens"]
        sistema = mensagens["sistema"]
        canal = mensagens["canal"]
        delay = mensagens["delay"]
        content = mensagens["content"]

        sistemaText = f"{positivo} ``Habilitado``" if sistema else f"{negativo} ``Desabilitado``"
        Button = {
            "Label": "Desabilitar" if sistema else "Habilitar",
            "Style": disnake.ButtonStyle.red if sistema else disnake.ButtonStyle.green,
        }

        if canal:
            canais_formatados = ""
            for canal_id in canal:
                channel = inter.guild.get_channel(int(canal_id))
                if channel:
                    canais_formatados += f"{channel.mention}\n"
                else:
                    canais_formatados += f"{negativo} ``Canal não encontrado``\n"
        else:
            canais_formatados = f"{negativo} ``Não definido``"

        if delay: delay = f"{positivo} ``{delay} minutos``"
        else: delay = f"{negativo} ``Não definido``"

        content = f"{negativo} ``Não definido``" if content == "" else f"```{content}```"

        embed = disnake.Embed(
            title="Mensagens | Ações Automáticas",
            description=f"""
    Seu Ease Bot enviará mensagens automaticamente nos intervalos e no canal que você pré-definir.
        """,
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Sistema", value=sistemaText, inline=True)
        embed.add_field(name="Delay", value=delay, inline=True)
        embed.add_field(name="Canais", value=canais_formatados, inline=False)
        embed.add_field(name="Conteúdo", value=content, inline=False)

        components = [
            disnake.ui.Button(label=Button["Label"], style=Button["Style"], emoji=reload, custom_id="AtivarDesativarSistemaAcoesAuto_mensagens"),
            disnake.ui.Button(label="Configurar", style=disnake.ButtonStyle.blurple, emoji=editar, custom_id="ConfigurarSistemaMensagens"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarAcoesAutomaticas"),
        ]

        return embed, components

    def ObterPainelReacoes(inter: disnake.MessageInteraction):
        db = ObterDatabase()
        reacoes = db["reacoes"]
        sistema = reacoes["sistema"]
        canal = reacoes["canal"]
        emoji = reacoes["emoji"]

        sistemaText = f"{positivo} ``Habilitado``" if sistema else f"{negativo} ``Desabilitado``"
        Button = {
            "Label": "Desabilitar" if sistema else "Habilitar",
            "Style": disnake.ButtonStyle.red if sistema else disnake.ButtonStyle.green,
        }

        if canal:
            canais_formatados = ""
            for canal_id in canal:
                channel = inter.guild.get_channel(int(canal_id))
                if channel:
                    canais_formatados += f"{channel.mention}\n"
                else:
                    canais_formatados += f"{negativo} ``Canal não encontrado``\n"
        else:
            canais_formatados = f"{negativo} ``Não definido``"

        emoji = f"{negativo} ``Não definido``" if emoji == "" else f"{emoji}"

        embed = disnake.Embed(
            title="Reações | Ações Automáticas",
            description=f"""
    Seu Ease Bot reagirá a todas mensagens enviadas em um canal definido.
        """,
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Sistema", value=sistemaText, inline=True)
        embed.add_field(name="Emoji", value=emoji, inline=True)
        embed.add_field(name="Canais", value=canais_formatados, inline=False)

        components = [
            disnake.ui.Button(label=Button["Label"], style=Button["Style"], emoji=reload, custom_id="AtivarDesativarSistemaAcoesAuto_reacoes"),
            disnake.ui.Button(label="Configurar", style=disnake.ButtonStyle.blurple, emoji=editar, custom_id="ConfigurarSistemaReacoes"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarAcoesAutomaticas"),
        ]

        return embed, components

class AcoesAutoCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def AcoesAutoButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarAcoesAutomaticas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            msg = "Escolha uma ação para configurar"

            components = [
                [
                    disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Repostagem", emoji=reload, custom_id="AcessarRepostagemAcoesAuto"),
                    disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Limpeza", emoji=apagar, custom_id="AcessarLimpezaAcoesAuto"),
                    disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Mensagens", emoji=mensagem, custom_id="AcessarMensagensAcoesAuto"),
                    disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Reações", emoji=cloud, custom_id="AcessarReacoesAcoesAuto"),
                ],
                [
                    disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
                ]
            ]
            await inter.edit_original_message(content=msg, components=components)
        
        elif inter.component.custom_id == "AcessarRepostagemAcoesAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = Panels.ObterPainelRepostagem(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "AcessarLimpezaAcoesAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = Panels.ObterPainelLimpeza(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "AcessarMensagensAcoesAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = Panels.ObterPainelMensagens(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "AcessarReacoesAcoesAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = Panels.ObterPainelReacoes(inter)
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id.startswith("AtivarDesativarSistemaAcoesAuto_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            sistema = inter.component.custom_id.replace("AtivarDesativarSistemaAcoesAuto_", "")

            db = ObterDatabase()
            db[sistema]["sistema"] = not db[sistema]["sistema"]

            with open("Database/Server/acoesauto.json", "w") as newf:
                newdb = json.dump(db, newf, indent=4)
            
            if sistema == "repostagem":
                embed, components = Panels.ObterPainelRepostagem(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
            elif sistema == "limpeza":
                embed, components = Panels.ObterPainelLimpeza(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
            elif sistema == "mensagens":
                embed, components = Panels.ObterPainelMensagens(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
            elif sistema == "reacoes":
                embed, components = Panels.ObterPainelReacoes(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)


        elif inter.component.custom_id == "ConfigurarSistemaLimpeza": await inter.response.send_modal(Modals.AlterarLimpezaModal())
        elif inter.component.custom_id == "ConfigurarSistemaMensagens": await inter.response.send_modal(Modals.AlterarMensagensModal())
        elif inter.component.custom_id == "ConfigurarSistemaReacoes": await inter.response.send_modal(Modals.AlterarReacaoModal())

def setup(bot: commands.Bot):
    bot.add_cog(AcoesAutoCommand(bot))
