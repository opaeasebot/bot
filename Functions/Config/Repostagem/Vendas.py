from Commands.Admin.Plugins.Ticket import *
from Functions.Config.Produto  import *

async def RepostagemMensagemProdutoVendas(bot: commands.Bot, produtoID):
    db = ObterDatabase()
    produto = db.get(produtoID)
    if not produto:
        return

    msg = produto.get("mensagem", "")
    embed, components = GerarPainelProduto(None, produtoID, bot)

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
    with open("Database/Vendas/produtos.json", "w") as f:
        json.dump(db, f, indent=4)
    
    return

async def RepostagemTodasMensagensVendas(bot: commands.Bot):
    db = ObterDatabase()
    for produtoID in db.keys():
        await RepostagemMensagemProdutoVendas(bot, produtoID)
    
    return