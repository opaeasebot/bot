from Functions.Database import Database
from Functions.Produto import *

class Vendas:
    @staticmethod
    async def RepostagemMensagemProdutoVendas(bot: commands.Bot, produtoID):
        db = Database.Obter("Database/Vendas/produtos.json")
        produto = db.get(produtoID)
        if not produto:
            return

        msg = produto.get("mensagem", "")
        embed, components = Produto.GerarPainelProduto(None, produtoID, bot)

        novos_ids = []
        for id_dict in produto.get("ids", []):
            try:
                channelID, messageID = list(id_dict.items())[0]
                channel = bot.get_channel(int(channelID))

                if not channel:
                    continue
                oldmsg = await channel.fetch_message(int(messageID))
                if oldmsg:
                    await oldmsg.delete()
            except:
                continue
            
            newmsg = await channel.send(content=msg, embed=embed, components=components)
            novos_ids.append({str(newmsg.channel.id): str(newmsg.id)})
        
        db[produtoID]["ids"] = novos_ids
        Database.Salvar("Database/Vendas/produtos.json", db)
        return

    @staticmethod
    async def RepostagemTodasMensagensVendas(bot: commands.Bot):
        db = Database.Obter("Database/Vendas/produtos.json")
        for produtoID in db.keys(): await Vendas.RepostagemMensagemProdutoVendas(bot, produtoID)
        return