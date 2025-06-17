import disnake
from disnake.ext import commands

import json
import os
from datetime import *

from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *

def ObterPainelInicial():
    embed=None
    
    components = [
        [
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Sua Loja", emoji=casa, custom_id="GerenciarPainelVendas"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Ticket", emoji=ticket, custom_id="GerenciarPainelTicket"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Boas Vindas", emoji=sino, custom_id="GerenciarPainelBoasVindas"),
            disnake.ui.Button(style=disnake.ButtonStyle.grey, label="Ações Automáticas", emoji=reload, custom_id="GerenciarAcoesAutomaticas"),
        ],
        [
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Personalização", emoji=wand, custom_id="GerenciarPainelPersonalizar"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Meu eCloud", emoji=cloud, custom_id="GerenciarPainelECloud"),
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Rendimento", emoji=carteira, custom_id="GerenciarPainelRendimento"),
            disnake.ui.Button(style=disnake.ButtonStyle.grey, label="Definições", emoji=config2, custom_id="GerenciarPainelConfigurar"),
        ],
        [
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Estatísticas gerais do servidor", emoji=canal, custom_id="GerenciarPainelEstatisticas", disabled=True),
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Sistema de Giveaways", emoji="<:giveaway:1358865686813741147>", custom_id="GerenciarPainelGiveaways", disabled=True),
            disnake.ui.Button(label="Proteção", emoji="<:protection:1358876611595993158>", custom_id="GerenciarProtecaoServidor", disabled=True),
        ]
    ]
    return embed, components

class ConfigurarCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def panel(self, inter: disnake.ApplicationCommandInteraction):
        """
        Use to manage my features
        """
        
        await inter.response.defer(ephemeral=True)
        if verificar_permissao(inter.user.id):
            embed, components = ObterPainelInicial()
            await inter.followup.send("https://imgur.com/My4fEV7", embed=embed, components=components)
        else:
            await inter.followup.send(f"{negativo} Faltam permissões para executar essa ação", delete_after=3)
    
    @commands.Cog.listener("on_button_click")
    async def PainelListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "PainelInicial":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = ObterPainelInicial()
            await inter.edit_original_message("https://imgur.com/My4fEV7", embed=embed, components=components)


def setup(bot: commands.Bot):
    bot.add_cog(ConfigurarCommand(bot))