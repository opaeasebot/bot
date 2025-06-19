import disnake
from disnake.ext import commands
from datetime import *
import json
import requests
import base64

from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Events.OnBotStart import *

def obterPainel(inter):
    msg = "Escolha uma opção e use sua criatividade e profissionalismo \\;)"

    components = [
        [
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Alterar Informações do Bot", emoji=editar, custom_id="AlterarInfoBot"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Alterar Status do Bot", emoji=editar, custom_id="AlterarStatusBot"),
        ],
        [
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
        ]
    ]

    return msg, components

def obter_token():
    with open("config.json") as config_file:
        config_db = json.load(config_file)
    return config_db["token"]

class EditarInformacoesBotModal(disnake.ui.Modal):
    def __init__(self):
        token = obter_token()
        url = "https://discord.com/api/v9/users/@me"
        headers = {"Authorization": f"Bot {token}"}
        response = requests.get(url, headers=headers)

        bot_nome = "Bot"
        if response.status_code == 200:
            bot_nome = response.json().get("username", "Bot")

        components = [
            disnake.ui.TextInput(
                label="Nome do Bot (Opcional)",
                placeholder="Digite o novo nome do bot",
                value=bot_nome,
                custom_id="nome_bot",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="URL do Avatar do Bot (Opcional)",
                placeholder="Digite a URL do novo avatar do bot",
                custom_id="avatar_bot",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="URL do Banner do Bot (Opcional)",
                placeholder="Digite a URL do novo banner do bot",
                custom_id="banner_bot",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
        ]
        super().__init__(title="Editar Informações do Bot", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        nome_bot = inter.text_values.get("nome_bot")
        avatar_url = inter.text_values.get("avatar_bot")
        banner_url = inter.text_values.get("banner_bot")

        await inter.response.defer(ephemeral=True)

        token = obter_token()
        url = "https://discord.com/api/v9/users/@me"
        headers = {"Authorization": f"Bot {token}"}

        payload = {}
        if nome_bot:
            payload["username"] = nome_bot
        if avatar_url:
            avatar_data = requests.get(avatar_url).content
            payload["avatar"] = f"data:image/png;base64,{base64.b64encode(avatar_data).decode()}"
        if banner_url:
            banner_data = requests.get(banner_url).content
            payload["banner"] = f"data:image/png;base64,{base64.b64encode(banner_data).decode()}"

        response = requests.patch(url, headers=headers, json=payload)

        if response.status_code == 200:
            await inter.followup.send(f"{positivo} As alterações foram salvas com sucesso.", ephemeral=True)
        else:
            await inter.followup.send(
                f"`❌` Não foi possível atualizar as informações do bot: {response.status_code}\n{response.text}"
            )

class Status():
    class AlterarStatusModal(disnake.ui.Modal):
        def __init__(self, bot):
            self.bot = bot
            components = [
                disnake.ui.TextInput(
                    label="Novo Status do Bot",
                    placeholder="Digite o novo status",
                    custom_id="novo_status",
                    style=disnake.TextInputStyle.short,
                    required=True,
                )
            ]
            super().__init__(title="Alterar Status do Bot", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            novo_status = inter.text_values.get("novo_status")

            with open("config.json", "r") as f:
                config = json.load(f)

            config["status"]["name"] = novo_status

            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)

            type, activity = OnBotStart.ObterStatus()
            await self.bot.change_presence(
                status=type,
                activity=activity
            )
            
            await inter.response.send_message(f"{positivo} As alterações foram salvas com sucesso.", ephemeral=True)

    @staticmethod
    def GerenciarStatus(inter: disnake.MessageInteraction):
        components = [
            disnake.ui.StringSelect(
                placeholder="Selecione um status para definir",
                custom_id="EditarStatusBotDropdown",
                options=[
                    disnake.SelectOption(
                        label="Online",
                        emoji="<:icons_online:1358597311663702118>",
                        value="online"
                    ),
                    disnake.SelectOption(
                        label="Ausente",
                        emoji="<:icons_idle:1358597307179991062>",
                        value="idle"
                    ),
                    disnake.SelectOption(
                        label="Não Pertubar",
                        emoji="<:icons_busy:1358597308807119018>",
                        value="dnd"
                    ),
                    disnake.SelectOption(
                        label="Transmitindo",
                        emoji="<:icons_stream:1358597309700509729>",
                        value="streaming"
                    ),
                ]
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Editar nome do status",
                custom_id="AlterarNomeStatus",
                emoji=editar
            ),
            disnake.ui.Button(
                label="Voltar",
                emoji=voltar,
                custom_id="GerenciarPainelPersonalizar"
            )
        ]
        return components

class PersonalizaçãoCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def PersonalizaçãoButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelPersonalizar":
           await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
           msg, components = obterPainel(inter) 
           await inter.edit_original_message(content=msg, components=components)

        elif inter.component.custom_id == "AlterarInfoBot":
            await inter.response.send_modal(EditarInformacoesBotModal())
        
        elif inter.component.custom_id == "AlterarStatusBot":
            components = Status.GerenciarStatus(inter)
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            await inter.edit_original_message("", components=components)
        
        elif inter.component.custom_id == "AlterarNomeStatus":
            await inter.response.send_modal(Status.AlterarStatusModal(self.bot))
        
    @commands.Cog.listener("on_dropdown")
    async def PersonalizaçãoDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "EditarStatusBotDropdown":
            with open("config.json") as f:
                config = json.load(f)
            
            config["status"]["type"] = inter.values[0]

            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            
            type, activity = OnBotStart.ObterStatus()
            await self.bot.change_presence(
                status=type,
                activity=activity
            )

            await inter.response.send_message(f"{positivo} As alterações foram salvas com sucesso.", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(PersonalizaçãoCommand(bot))