import json
import disnake
from disnake.ext import commands
from datetime import datetime, timedelta

from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Functions.Database import Database

class Rendimentos:
    def GerarEmbedRendimentos(periodo, resultados):
        periodo_titulos = {
            "hoje": "Painel de Rendimento Geral - **Hoje**",
            "ultimos_7_dias": "Painel de Rendimento Geral - **Últimos 7 Dias**",
            "ultimo_mes": "Painel de Rendimento Geral - **Último Mês**",
            "total": "Painel de Rendimento Geral - **Total**"
        }
        
        embed = disnake.Embed(
            description=f"{periodo_titulos.get(periodo)}",
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Total de Vendas", value=f"`{resultados['total_vendas']}`", inline=True)
        embed.add_field(name="Valor Total Ganho", value=f"`R${resultados['total_ganho']:.2f}`", inline=True)
        embed.add_field(name="Total de Produtos Entregues", value=f"`{resultados['total_produtos_entregues']}`", inline=False)
        embed.set_footer(text="Configuração do BOT")
        return embed

    def GerarComponentesRendimentos():
        return [
            disnake.ui.Button(label="Hoje", custom_id="VisualizarRendimentoHoje"),
            disnake.ui.Button(label="Últimos 7 Dias", custom_id="VisualizarRendimentoUltimos7Dias"),
            disnake.ui.Button(label="Último Mês", custom_id="VisualizarRendimentoUltimoMes"),
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Total", custom_id="VisualizarRendimentoTotal")
        ]

    def CalcularRendimentos(periodo="total"):
        vendasdb = Database.Obter("Database/Vendas/historicos.json")

        total_vendas = 0
        total_ganho = 0.0
        total_produtos_entregues = 0

        hoje = datetime.now()
        if periodo == "hoje":
            data_inicial = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == "ultimos_7_dias":
            data_inicial = hoje - timedelta(days=7)
        elif periodo == "ultimo_mes":
            primeiro_dia_mes_atual = hoje.replace(day=1)
            ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
            data_inicial = ultimo_dia_mes_anterior.replace(day=1)
        else:
            data_inicial = None

        for venda_id, dados_venda in vendasdb.items():
            if not isinstance(dados_venda, dict):
                print(f"Formato inválido para a venda ID {venda_id}.")
                continue

            try:
                timestamp_str = dados_venda["info"].get("timestamp")
                horario_venda = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M")


                if data_inicial and horario_venda < data_inicial:
                    continue

                quantidade = dados_venda["info"].get("quantidade", 0)
                valor = dados_venda["info"].get("valorFinal", 0.0)

                total_vendas += 1
                total_ganho += float(quantidade) * float(valor)
                total_produtos_entregues += quantidade
            except (KeyError, ValueError) as e:
                print(f"Erro ao processar a venda {venda_id}: {e}")
                continue

        return {
            "total_vendas": total_vendas,
            "total_ganho": total_ganho,
            "total_produtos_entregues": total_produtos_entregues
        }

class RendimentosCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def rendimentos(self, inter: disnake.MessageCommandInteraction):
        """
        Use to see all sells
        """

        if Perms.VerificarPerms(inter.user.id):
            components = Rendimentos.GerarComponentesRendimentos()
            await inter.response.send_message(f"Senhor(a) **{inter.user.name}**, selecione algum filtro abaixo.", components=components, ephemeral=True)
        else:
            await inter.response.send_message(f"{negativo} Faltam permissões para executar essa ação.", ephemeral=True)
            return

    @commands.Cog.listener("on_button_click")
    async def RendimentosListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelRendimento":
            components = Rendimentos.GerarComponentesRendimentos()
            await inter.response.send_message(f"Senhor(a) **{inter.user.name}**, selecione algum filtro abaixo.", components=components, ephemeral=True)

        elif inter.component.custom_id.startswith("VisualizarRendimento"):
            periodo_map = {
                "VisualizarRendimentoHoje": "hoje",
                "VisualizarRendimentoUltimos7Dias": "ultimos_7_dias",
                "VisualizarRendimentoUltimoMes": "ultimo_mes",
                "VisualizarRendimentoTotal": "total"
            }
            periodo = periodo_map.get(inter.component.custom_id, "total")
            resultados = Rendimentos.CalcularRendimentos(periodo=periodo)

            embed = Rendimentos.GerarEmbedRendimentos(periodo, resultados)
            components = Rendimentos.GerarComponentesRendimentos()

            await inter.response.edit_message("", embed=embed, components=components)

def setup(bot: commands.Bot):
    bot.add_cog(RendimentosCommand(bot))
