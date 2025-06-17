import json
import disnake
from disnake import *
from disnake.ext import commands
from Functions.CarregarEmojis import *
from datetime import *

################# MENSAGEM BOAS VINDAS #################
class BoasVindas():
    def obterPainelMensagemBoasVindas(inter: disnake.MessageInteraction):
        with open("Database/Server/boasvindas.json") as f:
            db = json.load(f)
            tempo_apagar = db["mensagens"]["boas-vindas"]["tempoApagar"]
            sistema = db["mensagens"]["boas-vindas"]["mensagem"]

        with open("Database/Server/canais.json") as canais:
            canaisdb = json.load(canais)
            canal_id = canaisdb["boasvindas"]

        if canal_id:
            canal = inter.guild.get_channel(int(canal_id))
            canal_text = f"{positivo} {canal.mention}" if canal else f"{negativo} ``Canal inválido``"
        else:
            canal_text = f"{negativo} ``Não configurado``"

        tempo_apagar_text = f"{positivo} ``{tempo_apagar} segundos``" if tempo_apagar else f"{negativo} ``Não configurado``"

        if sistema:
            sistema_text = f"{positivo} ``Ativado``"
            button = {
                "Label": "Desabilitar",
                "Emoji": reload,
                "Style": disnake.ButtonStyle.red,
            }
        else:
            sistema_text = f"{negativo} ``Desativado``"
            button = {
                "Label": "Habilitar",
                "Emoji": reload,
                "Style": disnake.ButtonStyle.green,
            }

        embed = disnake.Embed(
            title="Sistema de Boas-Vindas",
            description=(
                "Aqui você pode configurar seu sistema de Boas-Vindas.\n"
                "Ele será acionado sempre que um membro entrar no servidor:\n"
                "Auto Role, Mensagem de Boas-Vindas, etc.\n"
                "Configure o canal de boas vindas nas configurações."
            ),
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
            )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        embed.add_field(name="Canal Configurado", value=canal_text, inline=True)
        embed.add_field(name="Tempo para Apagar Mensagem", value=tempo_apagar_text, inline=True)
        embed.add_field(name="Status do Sistema", value=sistema_text, inline=True)

        components = [[
            disnake.ui.Button(label=button["Label"], emoji=button["Emoji"], style=button["Style"], custom_id="AtivarDesativarMensagemBoasVindas"),
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Editar Mensagem",
                custom_id="EditarMensagemBoasVindas",
                emoji=editar
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Pre-visualização",
                custom_id="PreviewMensagemBoasVindas",
                emoji=preview
            ),
        ],[
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarPainelBoasVindas"),
        ]
        ]

        return embed, components

    class ConfigurarMensagemBoasVindasModal(disnake.ui.Modal):
        def __init__(self):
            with open("Database/Server/boasvindas.json", "r") as f:
                db = json.load(f)

            components = [
                disnake.ui.TextInput(
                    label="Conteúdo da mensagem",
                    placeholder="{mencao} - Mencione o usuário\n{nome} - Nome do usuário\n{servidor} - Nome do servidor",
                    custom_id="content",
                    value=db["mensagens"]["boas-vindas"]["estiloMensagem"]["content"],
                    style=disnake.TextInputStyle.paragraph,
                    required=False
                ),
                disnake.ui.TextInput(
                    label="Tempo para apagar mensagem",
                    placeholder="Calculado em segundos",
                    custom_id="tempo",
                    value=db["mensagens"]["boas-vindas"]["tempoApagar"],
                    style=disnake.TextInputStyle.short,
                    required=False
                ),
            ]
            super().__init__(title="Editar Mensagem Boas-Vindas", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            content = inter.text_values["content"]
            tempo = inter.text_values["tempo"]

            if tempo != "":
                try:
                    tempo = int(tempo)
                    if tempo < 0:
                        raise ValueError("O tempo deve ser um número positivo.")
                except ValueError:
                    await inter.response.send_message(
                        content=f"{negativo} O valor do tempo deve ser um número inteiro positivo.",
                        ephemeral=True
                    )
                    return

            try:
                with open("Database/Server/boasvindas.json", "r") as f:
                    db = json.load(f)

                db["mensagens"]["boas-vindas"]["estiloMensagem"]["content"] = content
                db["mensagens"]["boas-vindas"]["tempoApagar"] = tempo

                with open("Database/Server/boasvindas.json", "w") as f:
                    json.dump(db, f, indent=4)

                embed, components = BoasVindas.obterPainelMensagemBoasVindas(inter)
                await inter.response.edit_message(content=None, embed=embed, components=components)

                await inter.followup.send(
                    content=f"{positivo} Mensagem de Boas-Vindas configurada com sucesso!",
                    delete_after=3,
                    ephemeral=True
                )

            except:
                await inter.response.send_message(
                    content=f"{negativo} Ocorreu um erro ao salvar as configurações",
                    ephemeral=True,
                    delete_after=3
                )

    async def PreviewMensagemBoasVindas(inter: disnake.MessageInteraction):
        try:
            with open("Database/Server/boasvindas.json", "r") as f:
                db = json.load(f)

            content = db["mensagens"]["boas-vindas"]["estiloMensagem"]["content"]
            deleteafter = db["mensagens"]["boas-vindas"]["tempoApagar"]

            if deleteafter == "":
                deleteafter = None

            try:
                if deleteafter:
                    deleteafter = int(deleteafter)
            except ValueError:
                deleteafter = None

            content_preview = (
                content.replace("{mencao}", inter.author.mention)
                .replace("{nome}", inter.author.name)
                .replace("{servidor}", inter.guild.name)
            )

            button = disnake.ui.Button(
                label="Mensagem do Sistema",
                style=disnake.ButtonStyle.gray,
                disabled=True
            )

            if deleteafter != None:
                await inter.response.send_message(
                    content=content_preview,
                    components=[button],
                    ephemeral=True,
                    delete_after=deleteafter
                )
            else:
                await inter.response.send_message(
                    content=content_preview,
                    components=[button],
                    ephemeral=True
                )

        except Exception as e:
            await inter.response.send_message(
                content=f"{negativo} Ocorreu um erro ao gerar a prévia: {str(e)}",
                ephemeral=True
            )



################# SISTEMA AUTO-ROLE ###################

class AutoRole():
    def obterPainelAutoRole(inter: disnake.MessageInteraction):
        with open("Database/Server/cargos.json", "r") as f:
            db = json.load(f)
            cargo_id = db["membro"]

        with open("Database/Server/boasvindas.json") as file:
            db2 = json.load(file)
            sistema = db2["funcoes"]["autoRole"]["membro"]

        if sistema:
            sistema_text = f"{positivo} ``Ativado``"
            button = {
                "Label": "Desabilitar",
                "Emoji": reload,
                "Style": disnake.ButtonStyle.red,
            }
        else:
            sistema_text = f"{negativo} ``Desativado``"
            button = {
                "Label": "Habilitar",
                "Emoji": reload,
                "Style": disnake.ButtonStyle.green,
            }

        if cargo_id:
            cargo = inter.guild.get_role(int(cargo_id))
            cargo_text = f"{positivo} {cargo.mention}" if cargo else f"{negativo} ``Cargo inválido``"
        else:
            cargo_text = f"{negativo} ``Não configurado``"

        embed = disnake.Embed(
            title="Sistema de Auto Role",
            description=(
                "Aqui você pode gerenciar o sistema de Auto Role.\n"
                "Ele atribuirá automaticamente um cargo aos membros que entrarem no servidor.\n"
                "Certifique-se de configurar um cargo válido."
            ),
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Status do Sistema", value=sistema_text, inline=True)
        embed.add_field(name="Cargo Configurado", value=cargo_text, inline=True)

        components = [
            [
                disnake.ui.Button(
                    label=button["Label"],
                    emoji=button["Emoji"],
                    style=button["Style"],
                    custom_id="AtivarDesativarAutoRole"
                ),
                disnake.ui.Button(
                    label="Voltar",
                    emoji=voltar,
                    style=disnake.ButtonStyle.grey,
                    custom_id="GerenciarPainelBoasVindas"
                ),
            ]
        ]

        return embed, components

#################### INÍCIO ###########################
class BoasVindasCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def BoasVindasButtunListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelBoasVindas":
            content = "Selecione um sistema para gerenciar \\;)"
            buttons = [
                [
                disnake.ui.Button(
                    style=disnake.ButtonStyle.blurple,
                    label="Gerenciar Mensagem de Boas-Vindas",
                    custom_id="GerenciarMensagemBoasVindas",
                    emoji=mensagem
                ),
                disnake.ui.Button(
                    style=disnake.ButtonStyle.blurple,
                    label="Gerenciar Sistema de Auto Role",
                    custom_id="GerenciarAutoRoleBoasVindas",
                    emoji=reload
                )
                ],
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
            ]
            await inter.response.edit_message(content=content, components=buttons, embed=None)
        
        elif inter.component.custom_id == "GerenciarMensagemBoasVindas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = BoasVindas.obterPainelMensagemBoasVindas(inter)
 
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "AtivarDesativarMensagemBoasVindas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            with open("Database/Server/boasvindas.json") as f:
                db = json.load(f)
            
            db["mensagens"]["boas-vindas"]["mensagem"] = not db["mensagens"]["boas-vindas"]["mensagem"]
            with open("Database/Server/boasvindas.json", "w") as f:
                json.dump(db, f, indent=4)

            if db["mensagens"]["boas-vindas"]["mensagem"]:
                embed, components = BoasVindas.obterPainelMensagemBoasVindas(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{positivo} O sistema de Mensagem de Boas Vindas foi habilitado.", ephemeral=True, delete_after=5)
            else:
                embed, components = BoasVindas.obterPainelMensagemBoasVindas(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{positivo} O sistema de Mensagem de Boas Vindas foi desabilitado.", ephemeral=True, delete_after=5)

        elif inter.component.custom_id == "EditarMensagemBoasVindas":
            await inter.response.send_modal(BoasVindas.ConfigurarMensagemBoasVindasModal())
        
        elif inter.component.custom_id == "PreviewMensagemBoasVindas":
            await BoasVindas.PreviewMensagemBoasVindas(inter)

        elif inter.component.custom_id == "GerenciarAutoRoleBoasVindas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = AutoRole.obterPainelAutoRole(inter)
 
            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "AtivarDesativarAutoRole":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            
            with open("Database/Server/boasvindas.json", "r") as f:
                db = json.load(f)
            
            db["funcoes"]["autoRole"]["membro"] = not db["funcoes"]["autoRole"]["membro"]
            
            with open("Database/Server/boasvindas.json", "w") as f:
                json.dump(db, f, indent=4)
            
            if db["funcoes"]["autoRole"]["membro"]:
                embed, components = AutoRole.obterPainelAutoRole(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{positivo} O sistema de Auto Role foi habilitado.", ephemeral=True, delete_after=5)
            else:
                embed, components = AutoRole.obterPainelAutoRole(inter)
                await inter.edit_original_message(content=None, embed=embed, components=components)
                await inter.followup.send(f"{positivo} O sistema de Auto Role foi desabilitado.", ephemeral=True, delete_after=5)
        


def setup(bot: commands.Bot):
    bot.add_cog(BoasVindasCommand(bot))