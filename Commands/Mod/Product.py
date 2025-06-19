import disnake
from disnake.ext import commands
from datetime import *
from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Functions.VendaInfo import *

def ObterDatabase():
    with open("Database/Vendas/historicos.json") as f:
        db = json.load(f)
        return db

def ObterProduto(produtoID):
    with open("Database/Vendas/produtos.json") as f:
        db = json.load(f)
        try:
            produto = db[produtoID]
        except:
            produto = None
        return produto

def ObterCampo(produtoID, campoID):
    with open("Database/Vendas/produtos.json") as f:
        db = json.load(f)
        try:
            produto = db[produtoID]
            campo = produto["campos"][campoID]
        except:
            campo = None
        return campo

class InfoProdutoCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def order(self, inter):
        pass

    @order.sub_command()
    async def info(self, inter: disnake.MessageCommandInteraction, id: str):
        """
        Use to see informations about a sale

        Parameters
        ----------
        id: ID do Pedido
        """

        if Perms.VerificarPerms(inter.user.id):
            await inter.response.send_message(f"{carregarAnimado} Carregando informações", ephemeral=True)
            
            embed, components = ObterVendaPainel(inter, id)
            if embed == None:
                return await inter.edit_original_message(f"{negativo} Venda `{id}` não encontrada.")

            await inter.edit_original_message("", embed=embed, components=components, file=disnake.File(f"Database/Vendas/entregas/{id}.txt", filename="itens_comprados.txt"),)

        else:
            await inter.response.send_message(f"{negativo} Faltam permissões para executar essa ação", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(InfoProdutoCommand(bot))
