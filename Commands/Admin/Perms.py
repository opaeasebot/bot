import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

with open("config.json") as config:
    db = json.load(config)
    owner = db["owner"]

def ObterMensagemPerm():
    try:
        with open("Database/perms.json") as permsFile:
            perms = json.load(permsFile)
    except FileNotFoundError:
        perms = {}

    usuarios = "\n".join([f"<@{user_id}>" for user_id in perms.keys()])

    if not usuarios:
        usuarios = f"{negativo} Nenhum usuário possui permissões no momento."

    embed = disnake.Embed(
        description=f"`🔧` Usuários com permissão para usar o Bot:\n{usuarios}",
        color=disnake.Color.dark_theme()
    )
    components = [
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label="Adicionar", emoji=mais2, custom_id="addMemberPerm"),
        disnake.ui.Button(style=disnake.ButtonStyle.gray, label="Remover", emoji=menos2, custom_id="removeMemberPerm"),
    ]

    return embed, components

class PermsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def perms(self, inter):
        """Use to manage the permissions"""

        await inter.response.defer(ephemeral=True)

        if str(inter.user.id) == owner:
            try:
                with open("Database/perms.json") as permsFile:
                    perms = json.load(permsFile)
            except FileNotFoundError:
                perms = {}

            usuarios = "\n".join([f"<@{user_id}>" for user_id in perms.keys()])

            if not usuarios:
                usuarios = f"{negativo} Nenhum usuário possui permissões no momento."

            embed = disnake.Embed(
                description=f"`🔧` Usuários com permissão para usar o Bot:\n{usuarios}",
                color=disnake.Color.dark_theme()
            )
            components = [
                disnake.ui.Button(style=disnake.ButtonStyle.gray, label="Adicionar", emoji=mais2, custom_id="addMemberPerm"),
                disnake.ui.Button(style=disnake.ButtonStyle.gray, label="Remover", emoji=menos2, custom_id="removeMemberPerm"),
            ]

            await inter.followup.send(embed=embed, components=components, ephemeral=True)

        else:
            await inter.followup.send(f"{negativo} Faltam permissões para executar essa ação", delete_after=3)

    @commands.Cog.listener("on_button_click")
    async def permsListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "addMemberPerm":
            components = disnake.ui.UserSelect(
                custom_id="addMemberPermDropdown",
                placeholder="Escolha uma pessoa para adicionar",
                max_values=1,
                min_values=1
            )
            await inter.response.edit_message(components=components)

        elif inter.component.custom_id == "removeMemberPerm":
            components = disnake.ui.UserSelect(
                custom_id="removeMemberPermDropdown",
                placeholder="Escolha uma pessoa para remover",
                max_values=1,
                min_values=1
            )
            await inter.response.edit_message(components=components)

    @commands.Cog.listener("on_dropdown")
    async def addMemberListenerDropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "addMemberPermDropdown":
            try:
                with open("Database/perms.json", "r") as config:
                    dadosPerms = json.load(config)
            except FileNotFoundError:
                dadosPerms = {}

            user_id = inter.values[0]
            dadosPerms[user_id] = user_id

            with open("Database/perms.json", "w") as json_file:
                json.dump(dadosPerms, json_file, indent=4)

            embed, components = ObterMensagemPerm()
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id == "removeMemberPermDropdown":
            try:
                with open("Database/perms.json", "r") as config:
                    dadosPerms = json.load(config)
            except FileNotFoundError:
                dadosPerms = {}

            user_id = inter.values[0]

            if user_id in dadosPerms:
                del dadosPerms[user_id]

                with open("Database/perms.json", "w") as json_file:
                    json.dump(dadosPerms, json_file, indent=4)

                embed, components = ObterMensagemPerm()
                await inter.response.edit_message(embed=embed, components=components)
            else:
                embed, components = ObterMensagemPerm()
                await inter.response.edit_message(embed=embed, components=components)
                await inter.followup.send(f"{negativo} O usuário não possui permissões", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(PermsCommand(bot))
