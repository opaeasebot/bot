import disnake
from disnake.ext import commands
from datetime import datetime
from disnake import *

import json
from Functions.CarregarEmojis import *
from Functions.Database import *
from Utils.Produto import *

class Produto:
    def GerarPainelProduto(inter: disnake.MessageInteraction | None, produtoID: str, bot: commands.Bot | None = None):
        db = Database.Obter("Database/Vendas/produtos.json")
        produto = db.get(produtoID, {})

        try:
            color = int(produto["assets"]["hex"], 16)
        except:
            color = 0x00FFFF

        embed = disnake.Embed(
            title=produto.get("nome", "Produto"),
            description=produto.get("desc", None),
            color=disnake.Color(color),
            timestamp=datetime.now()
        )

        if inter and inter.guild:
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        elif bot:
            config = Database.Obter("config.json")
            guild = bot.get_guild(int(config["server"]))
            embed.set_footer(text=guild.name, icon_url=guild.icon)

        if produto["assets"]["icon"]:
            try: embed.set_thumbnail(produto["assets"]["icon"])
            except: pass
        
        if produto["assets"]["banner"]:
            try: embed.set_image(produto["assets"]["banner"])
            except: pass

        select = None
        options = []

        if len(produto["campos"]) > 1:
            for campoID, campoData in produto["campos"].items():
                options.append(
                    disnake.SelectOption(
                        label=f'{campoData["nome"]}',
                        description=f'Preço: R${campoData["preco"]} | Estoque: {len(campoData["estoque"])}',
                        value=campoID
                    )
                )

            select = disnake.ui.StringSelect(
                placeholder="Selecione um campo para comprar",
                custom_id=f"ComprarCampo_{produtoID}",
                options=options
            )
        elif produto.get("campos") and len(produto["campos"]) == 1:
            campoID, campoData = next(iter(produto["campos"].items()))
            embed.add_field(name="Valor à vista", value=f"``R${campoData['preco']}``", inline=True)
            embed.add_field(name="Restam", value=f"``{len(campoData['estoque'])}``", inline=True)
            select = [
                disnake.ui.Button(label="Comprar", emoji=carrinho, custom_id=f"ComprarProduto_{produtoID}_{campoID}")
            ]

        else:
            embed.add_field(name="Valor à vista", value=f"``R$--``", inline=True)
            embed.add_field(name="Restam", value=f"``--``", inline=True)
            select = [
                disnake.ui.Button(label="Comprar", emoji=carrinho, custom_id=f"null", disabled=True)
            ]

        return embed, select

    async def NotificarUserEstoque(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
        db = Database.Obter("Database/Vendas/produtos.json")

        if produtoID not in db or campoID not in db[produtoID]["campos"]:
            return
        
        produto = db[produtoID]
        campo = produto["campos"][campoID]
        alertas = campo["estoqueinfo"].get("alertas", [])

        if "ids" in produto and produto["ids"]:
            canal_id = next(iter(produto["ids"][0].keys()), None)
        else: return

        try: canal = inter.guild.get_channel(int(canal_id))
        except: pass
        if not canal: pass
        else:
            botao = disnake.ui.Button(label="Ver Produto", url=canal.jump_url)

        for user_id in alertas:
            user = inter.guild.get_member(user_id)
            if user:
                embed = disnake.Embed(
                    description=f"Olá {user.mention}, o estoque do produto `{produto['nome']}` foi reabastecido!",
                    color=disnake.Color(0x00FFFF)
                )
                
                try:
                    await user.send(embed=embed, components=[botao])
                except:
                    pass

    async def SincronizarMensagens(inter: disnake.MessageInteraction, produtoID: str):
        try:
            db = Database.Obter("Database/Vendas/produtos.json")
            produto = db[produtoID]
            ids = produto["ids"]

            contagem = 0
            for id_dict in ids[:]:
                try:
                    channelID, msgID = list(id_dict.items())[0]

                    guild = inter.guild
                    channel = guild.get_channel(int(channelID))
                    if channel is None:
                        pass

                    msg = await channel.fetch_message(int(msgID))
                    if msg is None:
                        pass

                    embed, components = Produto.GerarPainelProduto(inter, produtoID)

                    await msg.edit(embed=embed, components=components)
                    contagem += 1
                except Exception as e:
                    ids.remove(id_dict)

            produto["ids"] = ids
            db[produtoID] = produto

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)

            return contagem

        except:
            return None