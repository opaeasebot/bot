import json
import disnake
from disnake import *
from datetime import *

from Functions.CarregarEmojis import *

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

def ObterCarrinho(carrinhoID):
    with open("Database/Vendas/carrinhos.json") as f:
        db = json.load(f)
        carrinho = db[carrinhoID]
        return carrinho

def ObterMensagemLogs(inter: disnake.CommandInteraction, type: str, carrinhoID):
    carrinho = ObterCarrinho(carrinhoID)
    produto = ObterProduto(carrinho["produtoID"])
    campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

    if type == "1":
        embed = disnake.Embed(
            title=f"{pedidoSolicitado} Pedido solicitado",
            description=f"Usuário {inter.user.mention} solicitou um pedido e está no pagamento.",
            color=disnake.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Detalhes do pedido", value=f"`{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]} | R${carrinho["info"]["valorFinal"]}`", inline=False)
        embed.add_field(name="ID do pedido", value=f"`{carrinhoID}`", inline=True)
        embed.add_field(name="Forma de Pagamento", value=f"{pix} `Pagamento: PIX`")
        components = [
            disnake.ui.Button(label="Ir para carrinho", url=inter.channel.jump_url, emoji=caixa)
        ]

    elif type == "2":
        embed = disnake.Embed(
            title=f"{pix} Pagamento via PIX Criado",
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(
            name="Expira em",
            value=f"<t:{int((datetime.now() + timedelta(minutes=10)).timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Valor final",
            value=f"`R${carrinho["info"]["valorFinal"]}`",
            inline=True
        )
        embed.add_field(
            name="Código Copia e Cola",
            value=f"```{carrinho["info"]["pagamento"]["copiacola"]}```",
            inline=False
        )
        embed.set_author(name=inter.user.name, icon_url=inter.user.avatar)
        embed.set_image(url=carrinho["info"]["pagamento"]["url"])

        components = [
            disnake.ui.Button(
                label="Código Copia e Cola",
                emoji=f"{mensagem}", # copia e cola igual cyans
                custom_id=f"CodigoCopiaCola_{carrinhoID}"
            ),
            disnake.ui.Button(style=disnake.ButtonStyle.red, label="Cancelar", emoji=apagar, custom_id=f"CancelarCarrinho_{carrinhoID}")
        ]
    
    elif type == "3":
        embed = disnake.Embed(
            title=f"{pedidoEntregue} Pagamento concluído",
            description="Seu pagamento foi aprovado, e o processo de entrega já foi iniciado.\nAguarde um momento enquanto separamos seu produto.",
            timestamp=datetime.now(),
            color=disnake.Color(0x0be34c)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(
            name="Informações do pedido",
            value=f"`{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]} | R${carrinho["info"]["valorFinal"]}`",
            inline=True
        )
        embed.add_field(
            name="ID do pedido",
            value=f"`{carrinhoID}`",
            inline=True
        )

        components = [
            disnake.ui.Button(
                label="Gerenciar Estoque",
                custom_id=f"GerenciarEstoqueVenda_{carrinho["produtoID"]}_{carrinho["campoID"]}",
                style=disnake.ButtonStyle.blurple,
                emoji=caixa
            ),
        ]

    elif type == "4":
        embed = disnake.Embed(
            title=f"{produtoEntregue} Entrega realizada",
            description="Seu pedido foi concluído e processado!\nSeu pedido foi anexado a essa mensagem.",
            color=disnake.Color(0x3808bd),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(
            name="Horário da entrega",
            value=f"<t:{int(datetime.now().timestamp())}:f>",
            inline=True
        )
        embed.add_field(
            name="ID do pedido",
            value=f"`{carrinhoID}`",
            inline=True
        )

        channel = inter.guild.get_channel(int(carrinho["server"]["produtoURL"]))
        components = [
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Ativar atualizações de estoque",
                emoji=sino,
                custom_id=f"AtivarNotificacoesEstoque_{carrinho["produtoID"]}_{carrinho["campoID"]}"
            ),
            disnake.ui.Button(
                label="Comprar novamente",
                url=channel.jump_url,
                emoji=caixa
            ),
        ]

    elif type == "blocked":
        embed = disnake.Embed(
            title=f"{bancoBloqueado} Banco bloqueado",
            description=f"""
O banco que você utilizou no pagamento foi bloqueado pela loja.
Por causa disso, reembolsamos seu pagamento (`R${carrinho["info"]["valorFinal"]}`)
Caso ocorreu algum engano, contate o suporte.
            """,
            color=disnake.Color(0xe31e10),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        components = None
    
    elif type == "ticket":
        with open("Database/Server/cargos.json") as db:
            cargos = json.load(db)
        
        with open("config.json") as config:
            confdb = json.load(config)
            owner = confdb["owner"]
            
        suporte = cargos["suporte"]
        if not suporte: suporte = f"<@{owner}>" 
        else: suporte = f"<@&{suporte}>"
        content = f"{inter.user.mention} {suporte}"

        embed = disnake.Embed(
            title="Entrega não automática",
            description="Utilize o ticket atual para receber sua entrega.\nAbaixo estão as informações do carrinho.",
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(
            name="Informações do pedido",
            value=f"```{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]} | R${carrinho["info"]["valorFinal"]}```",
            inline=False
        )
        embed.add_field(
            name="ID do Pedido",
            value=f"`{carrinhoID}`"
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1327815504865398854/1333664443258900583/a_d78e7542df8823e9c10eac06609d7473.gif?ex=67a8e08d&is=67a78f0d&hm=a9788d0dac946e924b4ad289e9e4d731bfff25168a35be92e0bc7e206d3c8d06&=&width=413&height=413"
        )

        components = [
            disnake.ui.Button(style=disnake.ButtonStyle.red, label="Fechar", emoji=apagar, custom_id=f"CancelarCarrinho_{carrinhoID}")
        ]
    
    elif type == "indisponivel":
        embed = disnake.Embed(
            title=f"{carrinhoCancelado} Produto indisponível",
            description="Não foi possível separar seu pedido pois o estoque acabou, se o método de pagamento usado for extornável, seu dinheiro foi devolvido.",
            color=disnake.Color(0xe31e10),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(
            name="ID da Compra",
            value=f"`{carrinhoID}`"
        )

        components = [
            disnake.ui.Button(
                label="Gerenciar Estoque",
                custom_id=f"GerenciarEstoqueVenda_{carrinho["produtoID"]}_{carrinho["campoID"]}",
                style=disnake.ButtonStyle.blurple,
                emoji=caixa
            )
        ]
    
    return embed, components