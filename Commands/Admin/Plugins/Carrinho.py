import disnake
from disnake import *
from disnake.ext import commands

import shutil
import os

import json
import random
import string
import asyncio
from datetime import *

from Functions.CarregarEmojis import *
from Functions.Config.FormasPagamentos import *
from Functions.Config.FormasPagamento.Mensagens import *
from Functions.Config.Produto import *
from Functions.VerificarPerms import *
from Functions.VendaInfo import *


# Aqui ele registra as tasks (asyncio) que contam 10 minutos
# para apagar o carrinho. Ele encontra essa task e cancela
# se cada passo for concluido, como produto aprovado, etc.
tasks = {} # tasks => apagar carrinho 
tasksPagamento = {} # pagamento => verificar pagamento

def ObterDatabase():
    with open("Database/Vendas/produtos.json") as f:
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

def ObterCarrinho(carrinhoID):
    with open("Database/Vendas/carrinhos.json") as f:
        db = json.load(f)
        try:
            carrinho = db[carrinhoID]
        except: carrinho = None
        return carrinho

def ObterCupom(produtoID, cupom):
    with open("Database/Vendas/produtos.json") as f:
        db = json.load(f)
        try:
            produto = db[produtoID]
            cupom = produto["cupons"][cupom]
        except:
            cupom = None
        return cupom

def GerarString():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=13))

def ObterVenda(vendaID):
    with open("Database/Vendas/historicos.json") as f:
        db = json.load(f)
        venda = db[vendaID]
        return venda

class Logs():
    async def EnviarLogs(inter: disnake.MessageInteraction, content: str, embed: disnake.Embed, components: tuple, files=None):
        with open("Database/Server/canais.json") as f:
            db = json.load(f)
        
        if not db["logs"]: return

        try: channel = inter.guild.get_channel(int(db["logs"]))
        except: return

        try: await channel.send(content=content, embed=embed, components=components, files=files)
        except: return

class Pagamentos():
    def SalvarPagamento(carrinho, carrinhoID):
        with open("Database/Vendas/carrinhos.json", "r") as f:
            todos_carrinhos = json.load(f)

        todos_carrinhos[carrinhoID] = carrinho
        with open("Database/Vendas/carrinhos.json", "w") as f:
            json.dump(todos_carrinhos, f, indent=4)

    def GerarPagamento(carrinhoID: str):
        FormasPagamento = ObterFormasPagamento()
        carrinho = ObterCarrinho(carrinhoID)

        if FormasPagamento["mercadopago"]["habilitado"]:
            qr_code, qrcodeURL, payment = MercadoPagoPagamento.GerarPagamento(float(carrinho["info"]["valorFinal"]))
            carrinho["info"]["pagamento"]["url"] = qrcodeURL
            carrinho["info"]["pagamento"]["paymentID"] = payment
            carrinho["info"]["pagamento"]["copiacola"] = qr_code
            Pagamentos.SalvarPagamento(carrinho, carrinhoID)
            return "MercadoPago", qr_code, qrcodeURL
        
        elif FormasPagamento["efi"]["habilitado"]:
            qr_code, qrcodeURL, payment = EfiBankPagamento.GerarPagamento(float(carrinho["info"]["valorFinal"]))
            carrinho["info"]["pagamento"]["url"] = qrcodeURL
            carrinho["info"]["pagamento"]["txid"] = payment
            carrinho["info"]["pagamento"]["copiacola"] = qr_code
            Pagamentos.SalvarPagamento(carrinho, carrinhoID)
            return "EfiBank", qr_code, qrcodeURL
    
        elif FormasPagamento["semiauto"]["habilitado"]:
            chave, qr_code = SemiAutoPagamento.GerarPagamento()
            if not chave.startswith("55") and FormasPagamento["semiauto"]["tipoPix"] == "telefone":
                chave = "55" + chave
            carrinho["info"]["pagamento"]["copiacola"] = chave

            carrinho["info"]["pagamento"]["url"] = qr_code
            Pagamentos.SalvarPagamento(carrinho, carrinhoID)
            return "SemiAuto", chave, qr_code

        else:
            return None, None, None

class Cupom():
    @staticmethod
    def Estatisticas(produtoID, nome, carrinhoID):
        carrinho = ObterCarrinho(carrinhoID)
        with open("Database/Vendas/produtos.json") as f:
            db = json.load(f)
        
        db[produtoID]["cupons"][nome]["estatistics"]["uses"] += 1
        db[produtoID]["cupons"][nome]["estatistics"]["economizado"] += (carrinho["info"]["valorFinal"] * db[produtoID]["cupons"][nome]["porcentagem"]) / 100

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

class Carrinho():
    class EditarQuantidade(disnake.ui.Modal):
        def __init__(self, carrinhoID):
            self.carrinhoID = carrinhoID
            carrinho = ObterCarrinho(carrinhoID)
            components = [
                disnake.ui.TextInput(
                    label="Quantidade",
                    placeholder="Coloque um valor inteiro",
                    custom_id="quantidade",
                    value=f"{carrinho['info']['quantidade']}",
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Alterar quantidade", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
                try:
                    quant = int(inter.text_values["quantidade"])
                    if quant <= 0:
                        await inter.response.send_message(f"{negativo} A quantidade deve ser um número positivo.", ephemeral=True)
                        return
                except:
                        await inter.response.send_message(f"{negativo} A quantidade deve ser um número positivo.", ephemeral=True)
                        return

                if not Carrinho.VerificarQuantidade(self.carrinhoID, quant):
                    await inter.response.send_message(f"{negativo} Quantidade fora dos limites permitidos.", ephemeral=True)
                    return

                with open("Database/Vendas/carrinhos.json") as f:
                    db = json.load(f)

                carrinho = ObterCarrinho(self.carrinhoID)
                campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])
                valor_total = round(int(quant) * float(campo["preco"]), 2)

                if carrinho["info"]["cupom"]["usado"]:
                    cupom = ObterCupom(carrinho["produtoID"], carrinho["info"]["cupom"]["usado"])
                    porcentagem = cupom.get("porcentagem", 0)
                    desconto = (valor_total * porcentagem) / 100 
                    valor_total -= round(desconto, 2)


                db[self.carrinhoID]["info"]["quantidade"] = quant
                db[self.carrinhoID]["info"]["valorFinal"] = "{:.2f}".format(valor_total)

                with open("Database/Vendas/carrinhos.json", "w") as f:
                    json.dump(db, f, indent=4)

                embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, self.carrinhoID)
                await inter.response.edit_message(embed=embed, components=components)

    class AlterarCupom(disnake.ui.Modal):
        def __init__(self, carrinhoID):
            self.carrinhoID = carrinhoID
            components = [
                disnake.ui.TextInput(
                    label="Cupom",
                    placeholder="Coloque o valor do cupom",
                    custom_id="cupom",
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Adicionar Cupom", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            carrinho = ObterCarrinho(self.carrinhoID)
            produtoID = carrinho["produtoID"]
            cupomInserido = inter.text_values["cupom"]

            with open("Database/Vendas/produtos.json") as f:
                produtos = json.load(f)

            produto = produtos.get(produtoID)
            cupons = produto.get("cupons", {})

            if not cupomInserido in cupons:
                return await inter.response.send_message(f"{negativo} Cupom inserido não encontrado `{cupomInserido}`", ephemeral=True)

            cupomInfo = cupons[cupomInserido]

            if cupomInfo["estatistics"]["uses"] == cupomInfo["usage"]["maxuses"]:
                return await inter.response.send_message(f"{negativo} O cupom `{cupomInserido}` já foi utilizado por outras pessoas e o máximo de usos foi excedido.", ephemeral=True)

            desconto = cupomInfo["porcentagem"]
            minValue = cupomInfo["usage"].get("minvalue", None)

            valorFinal = float(carrinho["info"]["valorFinal"])

            if valorFinal == 0:
                return await inter.response.send_message(f"{negativo} O valor do seu carrinho já é `R$0`.", ephemeral=True)

            valorAtual = "{:.2f}".format(valorFinal)
            valorAtual = float(valorAtual)
            if minValue and valorAtual < float(minValue):
                await inter.response.send_message(f"{negativo} Este cupom requer um valor mínimo de {minValue}.", ephemeral=True)
                return

            if carrinho["info"]["cupom"]["usado"]:
                await inter.response.send_message(f"{negativo} Um cupom já está sendo utilizado. Para usar outro, crie outro carrinho.", ephemeral=True)
                return

            valorComDesconto = valorAtual * (1 - (desconto / 100))
            carrinho["info"]["valorFinal"] = "{:.2f}".format(valorComDesconto)
            carrinho["info"]["cupom"]["usado"] = cupomInserido
            carrinho["info"]["cupom"]["valorAntes"] = valorAtual

            with open("Database/Vendas/carrinhos.json") as f:
                db = json.load(f)

            db[self.carrinhoID] = carrinho

            with open("Database/Vendas/carrinhos.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, self.carrinhoID)
            await inter.response.edit_message(embed=embed, components=components)

    class Mensagens():
        def ObterMensagemCarrinho(inter: disnake.MessageInteraction, carrinhoID: str):
            carrinho = ObterCarrinho(carrinhoID)
            produto = ObterProduto(carrinho["produtoID"])
            campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

            embed = disnake.Embed(
                description="## Revisão do pedido",
                timestamp=datetime.now(),
                color=disnake.Color(0x00FFFF)
            )
            embed.set_author(name=f"Carrinho | {campo["nome"]}", icon_url=inter.user.avatar)

            if carrinho["info"]["cupom"]["usado"]:
                embed.add_field(name="Valor à vista", value=f"~~``R${carrinho["info"]["cupom"]["valorAntes"]}``~~\n``R${carrinho["info"]["valorFinal"]}``", inline=True)
            else: embed.add_field(name="Valor à vista", value=f"``R${carrinho["info"]["valorFinal"]}``", inline=True)

            embed.add_field(name="Quantidade", value=f"``{carrinho["info"]["quantidade"]}``", inline=True)
            embed.add_field(name="Em estoque", value=f"``{len(campo["estoque"])}``", inline=True)
            embed.add_field(name="Informações do pedido", value=f"``{carrinho["info"]["quantidade"]}x {produto["nome"]} - {campo["nome"]}``", inline=False)
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

            components = [
                [
                    disnake.ui.Button(style=disnake.ButtonStyle.green, label="Prosseguir para pagamento", emoji=arrow, custom_id=f"ProsseguirPagamento_{carrinhoID}"),
                    disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Editar", emoji=editar, custom_id=f"EditarQuantidade_{carrinhoID}")
                ],
                [
                    disnake.ui.Button(label="Utilizar Cupom", emoji=cupom, custom_id=f"UsarCupom_{carrinhoID}"),
                    disnake.ui.Button(style=disnake.ButtonStyle.red, label="Cancelar pedido", emoji=apagar, custom_id=f"CancelarCarrinho_{carrinhoID}")
                ]
            ]

            return embed, components

        def ObterMensagemCarrinhoCancelado(inter: disnake.MessageInteraction, carrinhoID: str):
            carrinho = ObterCarrinho(carrinhoID)

            embed = disnake.Embed(
                title=f"{carrinhoCancelado} Carrinho fechado",
                description="O seu carrinho foi encerrado com sucesso.\nCaso precise realizar novas compras ou revisar seus itens, sinta-se à vontade para abrir um novo carrinho a qualquer momento.",
                timestamp=datetime.now(),
                color=disnake.Color(0xe31e10)
            )
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

            return embed, None

        def ObterMensagemCarrinhoExpirado(inter: disnake.MessageInteraction):
            embed = disnake.Embed(
                title=f"{carrinhoCancelado} Pedido cancelado",
                timestamp=datetime.now(),
                color=disnake.Color.red()
            )
            embed.add_field(
                name="Razão",
                value="O tempo máximo (`10 minutos`) foi excedido."
            )
            return embed

    @staticmethod
    def VerificarValores(carrinhoID) -> bool:
        carrinho = ObterCarrinho(carrinhoID)
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])
        condicoes = campo["condicoes"]

        valorFinal = carrinho["info"]["valorFinal"]
        valorMin = condicoes["valorMin"]
        valorMax = condicoes["valorMax"]

        if valorMin is not None and valorFinal < float(valorMin):
            return False

        if valorMax is not None and valorFinal > float(valorMax):
            return False

        return True

    @staticmethod
    def VerificarID(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
        campo = ObterCampo(produtoID, campoID)
        try:
            for id in campo["condicoes"]["idCargo"]:
                if inter.user.id == int(id):
                    return True
            
            return False
        except: return False
    
    @staticmethod
    def VerificarQuantidade(carrinhoID, quantidade) -> bool:
        carrinho = ObterCarrinho(carrinhoID)
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])
        condicoes = campo["condicoes"]

        quantidadeMin = condicoes["quantidadeMin"]
        quantidadeMax = condicoes["quantidadeMax"]

        if quantidadeMin is not None and int(quantidadeMin) > int(quantidade):
            return False

        if quantidadeMax is not None and int(quantidade) > int(quantidadeMax):
            return False
        
        if quantidade > len(campo["estoque"]):
            return False

        return True

    @staticmethod
    async def AdicionarCargos(inter: disnake.MessageInteraction, carrinhoID):
        # quando a pessoa comprar, essa função será acionada
        # ela adicionará o cargo de cliente, se disponpivel
        # e adicionará/removerá os cargos setados no Gerenciar Cargos
        # que pode ser configurado no Gerenciar Campos

        carrinho = ObterCarrinho(carrinhoID)
        user = inter.guild.get_member(int(carrinho["server"]["usuario"]))
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        with open("Database/Server/cargos.json") as f:
            cargos = json.load(f)
        
        if cargos["cliente"]:
            try:
                cargo = inter.guild.get_role(int(cargos["cliente"]))
                await user.add_roles(cargo, reason="[Ease Bot] Cargo cliente")
            except:
                await Logs.EnviarLogs(inter, f"{negativo} Erro ao adicionar o cargo de **cliente** ao usuário {inter.user.mention}:\nO cargo é maior que o do Bot ou o Bot não possuí permissões", None, None)
                pass
        
        cargosAdd = []
        for cargoID in campo["cargos"]["add"]:
            try:
                cargo = inter.guild.get_role(int(cargoID))
                await user.add_roles(cargo, reason=f"[Ease Bot] Cargo | Campo: {campo["nome"]}")
                cargosAdd.append(cargo.id)
            except: pass
        
        cargosRem = []
        for cargoID in campo["cargos"]["rem"]:
            try:
                cargo = inter.guild.get_role(int(cargoID))
                await user.remove_roles(cargo, reason=f"[Ease Bot] Cargo | Campo: {campo["nome"]}")
            except: pass
        
        with open("Database/Vendas/produtos.json") as f:
            db = json.load(f)
        
        db[carrinho["produtoID"]]["campos"][carrinho["campoID"]]["cargos"]["add"] = cargosAdd
        db[carrinho["produtoID"]]["campos"][carrinho["campoID"]]["cargos"]["rem"] = cargosRem

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

    @staticmethod
    async def Cancelar(inter: disnake.MessageInteraction, carrinhoID: str, send=True):
        carrinho = ObterCarrinho(carrinhoID)
        await Carrinho.CancelarPagamento(carrinhoID)
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        try:
            channel = inter.guild.get_channel_or_thread(carrinho["server"]["carrinho"])
            await channel.delete(reason=f"[Ease Bot] Apagar carrinho: {inter.user.id}")
        except: pass

        with open("Database/Vendas/carrinhos.json") as f:
            db = json.load(f)
        
        if send:
            embed, components = Carrinho.Mensagens.ObterMensagemCarrinhoCancelado(inter, carrinhoID)
            embed.add_field(name="Informações do pedido", value=f"``{carrinho["info"]["quantidade"]}x {produto["nome"]} - {campo["nome"]}``", inline=False)
            embed.add_field(name="ID do pedido", value=f"`{carrinhoID}`")
            try:
                await inter.user.send(embed=embed, components=components)
            except: pass
            
            embed.description = f"O carrinho do usuário {inter.user.mention} (`{inter.user.id}`) foi cancelado.\nConsulte as informações do o carrinho abaixo"
            embed.add_field(name="Usuário", value=f"{inter.user.mention}", inline=False)
            try:
                await Logs.EnviarLogs(inter, content=None, embed=embed, components=components)
            except: pass
        try:
            del(db[carrinhoID])
        except: pass

        with open("Database/Vendas/carrinhos.json", "w") as f:
            json.dump(db, f, indent=4)

        await SincronizarMensagens(inter, carrinho["produtoID"])

    @staticmethod
    async def CriarCarrinho(inter: disnake.MessageInteraction, produtoID, campoID):
        await inter.response.send_message(f"{carregarAnimado} Aguarde, estamos criando seu carrinho", ephemeral=True)

        try:
            a1 = ObterProduto(produtoID)
            a2 = ObterCampo(produtoID, campoID)
            if not a1 or not a2: 
                await inter.edit_original_message(f"{negativo} Produto ou campo não encontrados")
                await SincronizarMensagens(inter, produtoID)
                return
            
        except:
            await inter.edit_original_message(f"{negativo} Não foi possível encontrar o produto.")
            await SincronizarMensagens(inter, produtoID)
            return

        CarrinhoID = GerarString()
        campo = ObterCampo(produtoID=produtoID, campoID=campoID)

        with open("Database/Vendas/carrinhos.json") as f:
            db = json.load(f)

        await inter.edit_original_message(f"{carregarAnimado} Verificando carrinhos")

        for carrinho_id, carrinho_data in db.items():
            if isinstance(carrinho_data, dict) and str(carrinho_data["server"]["usuario"]) == str(inter.user.id) and carrinho_data.get("produtoID") == produtoID and carrinho_data.get("campoID") == campoID:
                existe = False
                try:
                    channelid = carrinho_data["server"]["carrinho"]
                    channel = inter.guild.get_channel_or_thread(channelid)
                    if channel:
                        existe = True
                except:
                    existe = False

                if existe:
                    if channel:
                        await inter.edit_original_response(
                            content=f"{negativo} Você já possui um carrinho aberto para este produto e campo. Por favor, utilize o carrinho existente.",
                            components=[
                                disnake.ui.Button(
                                    label="Acessar Carrinho",
                                    url=channel.jump_url
                                )
                            ]
                        )
                    else:
                        await inter.edit_original_response(
                            content=f"{negativo} Você já possui um carrinho aberto para este produto e campo, mas não consegui encontrar o canal do carrinho."
                        )
                    return
                else:
                    await Carrinho.Cancelar(inter, carrinho_id, send=False)

        with open("Database/Vendas/carrinhos.json") as f:
            db = json.load(f)
        
        await inter.edit_original_message(f"{carregarAnimado} Verificando permissões")

        PermAbrir = Carrinho.VerificarID(inter, produtoID, campoID)
        if PermAbrir == True: return await inter.edit_original_message(f"{negativo} Você não tem permissão para abrir o carrinho.")

        await inter.edit_original_message(f"{carregarAnimado} Verificando estoque")
        if len(campo["estoque"]) == 0:
            return await inter.edit_original_message(
                f"{negativo} Não há estoque disponível. Tente novamente futuramente.",
                components=[
                    disnake.ui.Button(
                        style=disnake.ButtonStyle.blurple,
                        label="Ativar atualizações de estoque",
                        emoji=sino,
                        custom_id=f"AtivarNotificacoesEstoque_{produtoID}_{campoID}"
                    )
                ]
            )

        await inter.edit_original_message(f"{carregarAnimado} Criando seu carrinho")

        carrinho_nome = f"🛒・{inter.user.name}"

        with open("Database/Server/cargos.json") as db_file:
            server_db = json.load(db_file)

        suporte_role = f"<@&{server_db["administrador"]}>" if server_db["administrador"] else ""
        

        topic = await inter.channel.create_thread(
            name=carrinho_nome,
            type=disnake.ChannelType.private_thread,
            invitable=False
        )

        db[CarrinhoID] = {
            "produtoID": produtoID,
            "campoID": campoID,
            "carrinhoID": CarrinhoID,
            "server": {
                "produtoURL": inter.channel.id,
                "carrinho": topic.id,
                "usuario": inter.user.id
            },
            "info": {
                "quantidade": 1,
                "valorFinal": "{:.2f}".format(float(campo["preco"])),
                "pagamento": {
                    "copiacola": None,
                    "txid": None,
                    "url": None,
                    "paymentID": None
                },
                "cupom": {
                    "usado": None,
                    "valorAntes": round(float(campo["preco"]), 2),
                }
            }
        }

        with open("Database/Vendas/carrinhos.json", "w") as carrinhos_file:
            json.dump(db, carrinhos_file, indent=4)

        embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, CarrinhoID)
        await topic.purge()
        await topic.send(f"{inter.user.mention} {suporte_role}", embed=embed, components=components)

        await inter.edit_original_message(f"{positivo} Carrinho criado com êxito: {topic.jump_url}", components=[
            disnake.ui.Button(label="Ir para o carrinho", url=topic.jump_url)
        ])
        tasks[CarrinhoID] = asyncio.create_task(Carrinho.IniciarCountdownCarrinho(carrinho_id=CarrinhoID, inter=inter))

    @staticmethod
    async def CancelarCarrinho(carrinhoID): # para de contar aqueles 10 min para fechar
        if carrinhoID in tasks:
            try:
                tasks[carrinhoID].cancel()
                del tasks[carrinhoID]
            except: pass

    @staticmethod
    async def CancelarPagamento(carrinhoID):
        if carrinhoID in tasksPagamento:
            try:
                tasksPagamento[carrinhoID].cancel()
                del tasksPagamento[carrinhoID]
            except: pass

    @staticmethod
    async def IniciarCountdownCarrinho(carrinho_id: str, inter: disnake.MessageInteraction):
        countdown_time = 600
        await asyncio.sleep(countdown_time)
        try:
            with open("Database/Vendas/carrinhos.json", "r") as carrinhos_file:
                carrinhos_db = json.load(carrinhos_file)

            if carrinho_id not in carrinhos_db:
                return

            carrinho = carrinhos_db[carrinho_id]
            produto = ObterProduto(carrinho["produtoID"])
            campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])
            topic_id = carrinho["server"]["carrinho"]

            if topic_id:
                try:
                    topic = await inter.guild.fetch_channel(int(topic_id))
                    await topic.delete()
                except:
                    pass

            embedUser = Carrinho.Mensagens.ObterMensagemCarrinhoExpirado(inter)

            try:
                await inter.user.send(embed=embedUser)
            except:
                pass

            try:
                embedUser.add_field(
                    name="Detalhes do pedido", 
                    value=f"`{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]} | R${carrinho["info"]["valorFinal"]}`", inline=False
                )
                embedUser.add_field(
                    name="Usuário",
                    value=f"{inter.user.mention}\n(`{inter.user.id}`)",
                    inline=False
                )
                await Logs.EnviarLogs(inter, conttent=None, embed=embedUser, components=None)
            except:
                pass

        except:
            pass

        try:
            del carrinhos_db[carrinho_id]
            with open("Database/Vendas/carrinhos.json", "w") as carrinhos_file:
                json.dump(carrinhos_db, carrinhos_file, indent=4)
        except:
            pass

    @staticmethod
    async def ProsseguirPagamento(inter: disnake.MessageInteraction, carrinhoID: str):
        carrinho = ObterCarrinho(carrinhoID)
        await Carrinho.CancelarCarrinho(carrinhoID)
        await inter.response.edit_message(f"{carregarAnimado} Aguarde um momento...", embed=None, components=None)

        try:
            if not Carrinho.VerificarQuantidade(carrinhoID, carrinho["info"]["quantidade"]):
                embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, carrinhoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await inter.followup.send(f"{negativo} A quantidade excede/não alcança o limite definido para o produto.", ephemeral=True)
                return

            if not Carrinho.VerificarValores(carrinhoID):
                embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, carrinhoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await inter.followup.send(f"{negativo} O valor do carrinho excede/não alcança o limite definido para o produto.", ephemeral=True)
                return

            await inter.edit_original_message(f"{carregarAnimado} Aguarde mais um pouco, estamos quase lá!")


            # embed para enviar no canal de Logs [1]
            embed, components = ObterMensagemLogs(inter, "1", carrinhoID)
            try:
                await Logs.EnviarLogs(inter, content=None, embed=embed, components=components)
                await inter.user.send(embed=embed, components=components)
            except: pass
        
            if float(carrinho["info"]["valorFinal"]) == 0:
                await Carrinho.EntregarPedido(inter, carrinhoID)
                return

            # gerar pagamento -> pega a melhor chave encontrada (MP, Efi ou Semi)

            FormaPagamento, CopiaCola, QRCode = Pagamentos.GerarPagamento(carrinhoID)
            carrinho = ObterCarrinho(carrinhoID)

            if not FormaPagamento:
                embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, carrinhoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await Carrinho.CancelarPagamento(carrinhoID)
                await inter.followup.send(f"{negativo} Ocorreu um erro, nenhum método de pagamento implementado.", ephemeral=True)
                await Logs.EnviarLogs(inter, f"{negativo} Ocorreu um erro: Não há formas de pagamento disponíveis!\n-# @everyone", None, None)
                return

            # embed com CopiaCola/QR Code [2]
            embed, components = ObterMensagemLogs(inter, "2", carrinhoID)

            if FormaPagamento == "SemiAuto":
                components.insert(
                    1,
                    disnake.ui.Button(
                        style=disnake.ButtonStyle.green,
                        custom_id=f"AprovarCarrinho_{carrinhoID}",
                        emoji=f"{positivo}"
                    )
                )

            await inter.edit_original_message("", embed=embed, components=components)
            
            tasks[carrinhoID] = asyncio.create_task(Carrinho.IniciarCountdownCarrinho(carrinho_id=carrinhoID, inter=inter))

            if FormaPagamento == "MercadoPago":
                verificarPagamento = asyncio.create_task(Carrinho.VerificarPagamentoMercadoPago(inter, carrinhoID))
                tasksPagamento[carrinhoID] = verificarPagamento

            elif FormaPagamento == "EfiBank":
                verificarPagamento = asyncio.create_task(Carrinho.VerificarPagamentoEfiBank(inter, carrinhoID))
                tasksPagamento[carrinhoID] = verificarPagamento

        except Exception as e:
            embed, components = Carrinho.Mensagens.ObterMensagemCarrinho(inter, carrinhoID)
            await inter.edit_original_message("", embed=embed, components=components)
            print(e)
            await inter.followup.send(f"{negativo} Ocorreu um erro, tente novamente.", ephemeral=True)
            return

    @staticmethod
    async def VerificarPagamentoEfiBank(inter, carrinhoID):
        try:
            carrinho = ObterCarrinho(carrinhoID)
        except: 
            Carrinho.CancelarPagamento(carrinhoID)
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        txid = carrinho["info"]["pagamento"]["txid"]
        approved = False

        while approved == False:
            status = EfiBankPagamento.VerificarPagamento(txid, carrinhoID)

            if status == "Cancelled":
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.Cancelar(inter, carrinhoID, send=False)
                return

            elif status is True:
                await inter.edit_original_message(
                    f"{positivo} Produto pago com sucesso.\nAguarde um momento enquanto separamos seu pedido.",
                    embed=None, components=None
                )
                approved = True
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.EntregarPedido(inter, carrinhoID)
                return

            elif status == "Bloqueado":
                approved = True
                await inter.edit_original_message(
                    content=f"{negativo} Pagamento cancelado. Veja as informações no seu privado!", 
                    embed=None, components=None
                )

                embed, components = ObterMensagemLogs(inter, "blocked", carrinhoID)
                try:
                    await inter.user.send(embed=embed)
                except: 
                    pass

                embed.add_field(name="Pagador", value=f"{inter.user.mention}", inline=True)
                embed.add_field(name="Valor reembolsado", value=f"`R${carrinho['info']['valorFinal']}`", inline=True)
                embed.add_field(name="Informações do carrinho", 
                                value=f"`{carrinho['info']['quantidade']}x {campo['nome']} - {produto['nome']} | R${carrinho['info']['valorFinal']}`", 
                                inline=False)

                await Logs.EnviarLogs(inter, content=None, components=None, embed=embed)
                await asyncio.sleep(3)
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.Cancelar(inter, carrinhoID, send=False)
                return
            else: approved = False
            
            await asyncio.sleep(5)

    @staticmethod
    async def VerificarPagamentoMercadoPago(inter, carrinhoID):
        try:
            carrinho = ObterCarrinho(carrinhoID)
        except: 
            Carrinho.CancelarPagamento(carrinhoID)

        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        approved = False
        while not approved:
            status = await MercadoPagoPagamento.VerificarPagamento(carrinhoID)

            if status == "Cancelled":
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.Cancelar(inter, carrinhoID, send=False)
                return

            elif status is True:
                await inter.edit_original_message(
                    f"{positivo} Produto pago com sucesso.\nAguarde um momento enquanto separamos seu pedido.",
                    embed=None, components=None
                )
                approved = True
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.EntregarPedido(inter, carrinhoID)
                return

            elif status == "Bloqueado":
                approved = True
                await inter.edit_original_message(
                    content=f"{negativo} Pagamento cancelado. Veja as informações no seu privado!", 
                    embed=None, components=None
                )

                embed, components = ObterMensagemLogs(inter, "blocked", carrinhoID)
                try: 
                    await inter.user.send(embed=embed)
                except: 
                    pass

                embed.add_field(name="Pagador", value=f"{inter.user.mention}", inline=True)
                embed.add_field(name="Valor reembolsado", value=f"`R${carrinho['info']['valorFinal']}`", inline=True)
                embed.add_field(name="Informações do carrinho", 
                                value=f"`{carrinho['info']['quantidade']}x {campo['nome']} - {produto['nome']} | R${carrinho['info']['valorFinal']}`", 
                                inline=False)

                await Logs.EnviarLogs(inter, content=None, components=None, embed=embed)
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.Cancelar(inter, carrinhoID, send=False)
                return
            
            await asyncio.sleep(5)

    @staticmethod
    async def EntregarPedido(inter: disnake.MessageInteraction, carrinhoID: str):
        # coloquei uns comentarios para n ficar perdido
        carrinho = ObterCarrinho(carrinhoID)
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        await inter.edit_original_message(f"**Produto pago com sucesso.**\nAguarde um momento enquanto separamos seu pedido.", embed=None, components=None)
        user = inter.guild.get_member(int(carrinho["server"]["usuario"]))

        # embed -> user/logs -> sem nada, apenas informacoes [3]
        embed, components = ObterMensagemLogs(inter, "3", carrinhoID)
        try:
            await user.send(embed=embed)
        except:
            pass

        embed.add_field(
            name="ID do Pedido",
            value=f"`{carrinhoID}`"
        )

        embed.description = f"O pedido solicitado pelo usuário {user.mention} foi pago e está em fase de entrega.\nMais informações sobre o estado do produto aparecerão neste canal."
        await Logs.EnviarLogs(inter, content=None, embed=embed, components=components)


        # abrir ticket se a entrega não for automatica
        if produto["entrega"] == False:
            # embed de ticket -> caso n for entrega auto [ticket]
            embed, components = ObterMensagemLogs(inter, "ticket", carrinhoID)

            await inter.channel.purge()
            await inter.channel.send(
                content=None,
                embed=embed,
                components=components
            )
            arquivo = Entrega.ObterEstoque(carrinho["info"]["quantidade"], carrinho["produtoID"], carrinho["campoID"])
            await Entrega.RegistrarEntrega(inter, carrinhoID, arquivo)
            os.remove(arquivo) # ele so remove do stock do pedido, n envia para o user
            await Carrinho.AdicionarCargos(inter, carrinhoID)
            with open("Database/Vendas/vendas.json") as f:
                db = json.load(f)
                instrucoes = db["instrucoes"]
                if instrucoes:
                    await user.send(content=f"{user.mention}, {instrucoes}",
                    components=[
                        disnake.ui.Button(label="Mensagem do sistema", disabled=True)
                    ])
            await SincronizarMensagens(inter, carrinho["produtoID"])
            return

        # se for automática, ele continua        

        carrinho = ObterCarrinho(carrinhoID) # atualizar novamente para verificar
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        if len(campo["estoque"]) == 0: # verificacao se o produto estiver sem estoque
            # embed falando q o produto ta indisponivel [indisponivel]
            await inter.edit_original_message(f"{negativo} Ocorreu um problema. Verifique as informações no seu privado.")
            embed, components = ObterMensagemLogs(inter, "indisponivel", carrinhoID)

            await user.send(embed=embed)
            embed.description = f"Usuário {user.mention} teve seu dinheiro devolvido se o método usado for extornável, poís está fora de estoque."
            await Logs.EnviarLogs(inter, content=None, embed=embed, components=None)

            if carrinho["info"]["pagamento"]["paymentID"]: # falta o do txid
                MercadoPagoPagamento.ReembolsarBanco(
                    paymantData={
                        "id": carrinho["info"]["pagamento"]["paymentID"]
                    }
                )
            
            content = f"O estoque do produto `{produto["nome"]} -> {campo["nome"]}` esgotou.\n-# @everyone"
            await Logs.EnviarLogs(inter, content, None, components)
            vendaID = await Entrega.RegistrarEntrega(inter, carrinhoID)
            await asyncio.sleep(10)
            await Carrinho.Cancelar(inter, carrinhoID, send=False)
            return

        # entrega: enviar produto para o usuario
        # embed entrega realizada -> [4]
        embed, components = ObterMensagemLogs(inter, "4", carrinhoID)

        arquivo = Entrega.ObterEstoque(carrinho["info"]["quantidade"], carrinho["produtoID"], carrinho["campoID"])
        try:
            success = True
            msg = await user.send(file=disnake.File(arquivo, filename="itens_comprados.txt"), embed=embed, components=components)

            await inter.edit_original_message(f"**Entrega concluída com sucesso.**\nConsulte seu privado para obter as informações.\nEste carrinho será excluido em <t:{int((datetime.now() + timedelta(seconds=10)).timestamp())}:R>",
            components=[
                disnake.ui.Button(label="Acessar produto", url=msg.jump_url)
            ])
        except:
            success = False
            await inter.channel.send(content="**Não foi possível enviar seu produto na sua DM**\nSalve o produto entregue. O carrinho fecha em `120 segundos`", file=disnake.File(arquivo, filename="itens_comprados.txt"), embed=embed, components=components)

        vendaID = await Entrega.RegistrarEntrega(inter, carrinhoID, arquivo)

        components = [
            disnake.ui.Button(
                label="Informações da compra",
                emoji=carteira,
                custom_id=f"VendaInfo_{vendaID}",
                style=disnake.ButtonStyle.blurple
            ),
            disnake.ui.Button(
                label="Reembolsar",
                emoji=bancoBloqueado,
                custom_id=f"ReembolsarProduto_{vendaID}",
                disabled=False if carrinho["info"]["pagamento"]["paymentID"] else True
            )
        ]

        embed.add_field(
            name="Usuário",
            value=f"{user.mention}",
            inline=True
        )
        embed.add_field(
            name="ID do Pedido",
            value=f"`{carrinhoID}`",
            inline=True
        )
        embed.add_field(
            name="Informações do pedido",
            value=f"`{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]} | R${carrinho["info"]["valorFinal"]}`",
            inline=False
        )
        await Logs.EnviarLogs(
            inter,
            content=None,
            embed=embed,
            components=components,
            files=[disnake.File(arquivo, filename="itens_comprados.txt")]
        )


        # apagar arquivo (com stock) + apagar carrinho
        os.remove(arquivo)
        await Carrinho.AdicionarCargos(inter, carrinhoID)

        if carrinho["info"]["cupom"]["usado"]:
            Cupom.Estatisticas(carrinho["produtoID"], carrinho["info"]["cupom"]["usado"], carrinhoID)

        if success == True:
            await asyncio.sleep(10)
        else:
            await asyncio.sleep(120)
        await Carrinho.Cancelar(inter, carrinhoID, send=False)
        with open("Database/Vendas/vendas.json") as f:
            db = json.load(f)
            instrucoes = db["instrucoes"]
            if instrucoes:
                try:
                    await user.send(content=f"{user.mention}, {instrucoes}",
                    components=[
                        disnake.ui.Button(label="Mensagem do sistema", disabled=True)
                    ])
                except: pass

class Entrega():
    def ObterEstoque(quantidade, produtoID, campoID):
        campo = ObterCampo(produtoID, campoID)

        itens = []
        for _ in range(quantidade):
            if campo["estoque"]:
                item = campo["estoque"].pop(0)
                itens.append(item)
        
        db = ObterDatabase()
        db[produtoID]["campos"][campoID] = campo

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

        arquivo_nome = f"Database/Vendas/temp/estoque_{produtoID}_{campoID}.txt"
        with open(arquivo_nome, "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(itens))
        
        return arquivo_nome

    async def RegistrarEntrega(inter: disnake.MessageInteraction, carrinhoID: str, arquivo: str):
        carrinho = ObterCarrinho(carrinhoID)
        VendaID = Entrega.RegistrarVenda(carrinhoID, arquivo) # vendaID => carrinhoID
        produto = ObterProduto(carrinho["produtoID"])
        campo = ObterCampo(carrinho["produtoID"], carrinho["campoID"])

        user = inter.guild.get_member(int(carrinho["server"]["usuario"]))

        with open("Database/Server/canais.json") as f:
            canais = json.load(f)
            vendas = canais["vendas"]
        
        embed = disnake.Embed(
            title=f"{pedidoRealizado} Compra realizada",
            description=f"O usuário {user.mention} teve seu pedido entregue.",
            timestamp=datetime.now(),
            color=disnake.Color.green()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.set_author(name=user.name, icon_url=user.avatar)

        channel = inter.guild.get_channel(int(carrinho["server"]["produtoURL"]))
        components = [
            disnake.ui.Button(
                label="Comprar",
                url=channel.jump_url,
                emoji=caixa
            )
        ]

        embed.add_field(
            name="Carrinho",
            value=f"`{carrinho["info"]["quantidade"]}x {campo["nome"]} - {produto["nome"]}`",
            inline=False
        )
        embed.add_field(
            name="Valor pago",
            value=f"`R${carrinho["info"]["valorFinal"]}`",
            inline=True
        )
        embed.add_field(
            name="Usuário",
            value=f"{user.mention}",
            inline=True
        )

        try:
            channel = inter.guild.get_channel(int(vendas))
            await channel.send(embed=embed, components=components)
        except: pass

        return VendaID
    
    def RegistrarVenda(carrinhoID, arquivo):
        carrinho = ObterCarrinho(carrinhoID)

        pasta_destino = "Database/Vendas/entregas"
        os.makedirs(pasta_destino, exist_ok=True)

        destino = os.path.join(pasta_destino, f"{carrinhoID}.txt")
        shutil.copy2(arquivo, destino)

        with open("Database/Vendas/historicos.json") as f:
            db = json.load(f)
        
        db[carrinhoID] = carrinho
        db[carrinhoID]["info"]["timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        db[carrinhoID]["info"]["reembolso"] = False

        with open("Database/Vendas/historicos.json", "w") as f:
            json.dump(db, f, indent=4)
        
        return carrinhoID

    def ObterPainelGerenciarEstoque(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
        embed = None
        components = [
            [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label="Adicionar", emoji=mais2, custom_id=f"AdicionarEstoque_{produtoID}_{campoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Adicionar Estoque Fantasma", emoji=fantasma, custom_id=f"AdicionarEstoqueFantasma_{produtoID}_{campoID}"),
            ],
            [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label="Enviar Arquivo", emoji=diretorio, custom_id=f"EnviarArquivoEstoque_{produtoID}_{campoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Pegar item do estoque", emoji=arrow, custom_id=f"PegarItemEstoque_{produtoID}_{campoID}"),
            ],
            [
                disnake.ui.Button(label="Ver estoque", emoji=lupa, custom_id=f"VerEstoque_{produtoID}_{campoID}"),
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id=f"GerenciarCampo_{produtoID}_{campoID}"),
            ]
        ]

        return embed, components

class CarrinhoExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def deliver(
        self,
        inter: disnake.ApplicationCommandInteraction,
        campo: str = commands.Param(description="Selecione um campo", autocomplete=True),
        quantidade: int = commands.Param(description="Coloque a quantidade para ser recebida", default=1),
        user: disnake.User = commands.Param(description="Selecione um usuário para entregar o produto")
    ):
        """
        Use to deliver a product to an user
        """
        if not verificar_permissao(inter.user.id):
            return await inter.response.send_message(f"{negativo} Faltam permissões para executar essa ação.", ephemeral=True)

        if campo == "FaltamPermissoes":
            return await inter.response.send_message(f"{negativo} Faltam permissões para executar essa ação.", ephemeral=True)

        produto_id, campo_id = campo.split(":")
        produto = ObterProduto(produto_id)
        campo = ObterCampo(produto_id, campo_id)

        if quantidade > len(campo["estoque"]):
            return await inter.response.send_message(f"{negativo} Você precisa informar uma quantiade menor ou igual a do estoque. (`{quantidade}` | `{len(campo["estoque"])}`)", ephemeral=True)

        await inter.response.send_message(f"{carregarAnimado} Aguarde um momento...", ephemeral=True)

        embed = disnake.Embed(
            title="Pagamento manual",
            description="Você recebeu um produto manualmente por um moderador.\nVisualize as informações sobre o produto abaixo.",
            color=disnake.Color(0xdb0d9a),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Informações do produto", value=f"`{quantidade}x {produto["nome"]} - {campo["nome"]}`", inline=False)
        embed.add_field(name="Moderador", value=inter.user.mention, inline=True)
        arquivo = Entrega.ObterEstoque(quantidade, produto_id, campo_id)
        await user.send(embed=embed, files=[disnake.File(arquivo, filename="itens_recebidos.txt")])

        embed.description = "Um moderador entregou um produto manualmente para um usuário.\nAcompanhe os detalhes abaixo."
        embed.add_field(name="Usuário", value=user.mention)
        components = [
            disnake.ui.Button(
                label="Gerenciar Estoque",
                custom_id=f"GerenciarEstoqueVenda_{produto_id}_{campo_id}",
                style=disnake.ButtonStyle.blurple,
                emoji=caixa
            ),
        ]

        await Logs.EnviarLogs(inter, None, embed, components, [disnake.File(arquivo, filename="itens_recebidos.txt")])
        await inter.edit_original_message(f"{positivo} Pedido entregado com sucesso para {user.mention}")

    @deliver.autocomplete("campo")
    async def campo_autocomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        produtos_db = ObterDatabase()

        if verificar_permissao(inter.user.id):
            suggestions = []
            for produto_id, produto_data in produtos_db.items():
                nome_produto = produto_data["nome"]
                campos = produto_data.get("campos", {})
                for campo_id, campo_data in campos.items():
                    nome_campo = campo_data["nome"]

                    display_name = f"🛒 {nome_produto} ⭢ {nome_campo}"
                    value = f"{produto_id}:{campo_id}"
                    if string.lower() in display_name.lower():
                        suggestions.append(disnake.OptionChoice(name=display_name, value=value))
        else:
            suggestions = [
                disnake.OptionChoice(
                    name="❌ Faltam permissões para executar essa ação",
                    value="FaltamPermissoes"
                )
            ]

        return suggestions[:25]

    @commands.Cog.listener("on_button_click")
    async def CarrinhoListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith("ComprarProduto_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await Carrinho.CriarCarrinho(inter, produtoID, campoID)

        elif inter.component.custom_id.startswith("CancelarCarrinho_"):
            carrinhoID = inter.component.custom_id.replace("CancelarCarrinho_", "")
            await Carrinho.Cancelar(inter, carrinhoID)
        
        elif inter.component.custom_id.startswith("EditarQuantidade_"):
            carrinhoID = inter.component.custom_id.replace("EditarQuantidade_", "")
            await inter.response.send_modal(Carrinho.EditarQuantidade(carrinhoID))

        elif inter.component.custom_id.startswith("UsarCupom_"):
            carrinhoID = inter.component.custom_id.replace("UsarCupom_", "")
            await inter.response.send_modal(Carrinho.AlterarCupom(carrinhoID))

        elif inter.component.custom_id.startswith("ProsseguirPagamento_"):
            carrinhoID = inter.component.custom_id.replace("ProsseguirPagamento_", "")
            await Carrinho.ProsseguirPagamento(inter, carrinhoID)
        
        elif inter.component.custom_id.startswith("CodigoCopiaCola_"):
            carrinhoID = inter.component.custom_id.replace("CodigoCopiaCola_", "")
            carrinho = ObterCarrinho(carrinhoID)
            await inter.response.send_message(f"{carrinho["info"]["pagamento"]["copiacola"]}", ephemeral=True)
        
        elif inter.component.custom_id.startswith("ReembolsarProduto_"):
            vendaID = inter.component.custom_id.replace("ReembolsarProduto_", "")
            venda = ObterVenda(vendaID)
            if not venda:
                return await inter.response.send_message(f"{negativo} Venda `{vendaID}` não encontrada no sistema.")

            await inter.response.send_message(f"{carregarAnimado} Aguarde um momento", ephemeral=True)

            # enviar embed de banco bloqueado/modificada [reembolso]
            embed = disnake.Embed(
                title=f"{carrinhoCancelado} Reembolso concluído",
                description=f"Um moderador executou seu reembolso e todo o valor (`R${venda["info"]["valorFinal"]}`) foi reembolsado.\nPara mais informações, abra um suporte, mostrando o ID abaixo.",
                color=disnake.Color(0x53edb5),
                timestamp=datetime.now()
            )
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
            embed.add_field(
                name="ID da Compra",
                value=f"`{vendaID}`",
                inline=True
            )

            if verificar_permissao(inter.user.id):
                if venda["info"]["pagamento"]["paymentID"]:
                    paymentData = {
                        "id": venda["info"]["pagamento"]["paymentID"]
                    }
                    MercadoPagoPagamento.ReembolsarBanco(paymentData)
                    await inter.edit_original_message(f"{positivo} Reembolsado com sucesso.")

                    try:
                        member = inter.guild.get_channel(venda["server"]["usuario"])
                        await member.send(embed=embed)
                    except: pass

                    embed.description = f'Um moderador executou um reembolso e todo o valor (`R${venda["info"]["valorFinal"]}`) foi reembolsado.\nVeja as informações sobre o reembolso abaixo.'
                    embed.add_field(
                        name="Moderador",
                        value=f"{inter.user.mention}",
                        inline=True
                    )
                    await Logs.EnviarLogs(inter, content=None, components=None, embed=embed)
                else: return await inter.edit_original_message(f"{negativo} Esse método de pagamento é incompativel com o reembolso.")

            else: await inter.edit_original_message(f"{negativo} Faltam permissões para executar essa ação para executar essa ação")

        elif inter.component.custom_id.startswith("GerenciarEstoqueVenda_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            embed, components = Entrega.ObterPainelGerenciarEstoque(inter, produtoID, campoID)

            if verificar_permissao(inter.user.id):
                await inter.response.send_message(components=components, ephemeral=True)
            else: await inter.response.defer()

        elif inter.component.custom_id.startswith("AtivarNotificacoesEstoque_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await inter.response.send_message(f"{carregarAnimado} Registrando informações", ephemeral=True)
            db = ObterDatabase()

            alertas = db[produtoID]["campos"][campoID]["estoqueinfo"]["alertas"]

            if inter.user.id in alertas:
                alertas.remove(inter.user.id)
                mensagem = f"{positivo} Você **não receberá** mais atualizações."
            else:
                alertas.append(inter.user.id)
                mensagem = f"{positivo} Você **receberá** atualizações de estoque."

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)

            await inter.edit_original_message(mensagem)

        elif inter.component.custom_id.startswith("AprovarCarrinho_"):
            if verificar_permissao(inter.user.id):
                await inter.response.edit_message(
                    f"{positivo} Produto pago com sucesso.\nAguarde um momento enquanto separamos seu pedido.",
                    embed=None, components=None
                )

                carrinhoID = inter.component.custom_id.replace("AprovarCarrinho_", "")
                await Carrinho.CancelarCarrinho(carrinhoID)
                await Carrinho.EntregarPedido(inter, carrinhoID)
            else:
                await inter.response.defer()

        elif inter.component.custom_id.startswith("VendaInfo_"):
            vendaID = inter.component.custom_id.replace("VendaInfo_", "")
            if verificar_permissao(inter.user.id):
                await inter.response.send_message(f"{carregarAnimado} Carregando informações", ephemeral=True)
                
                embed, components = ObterVendaPainel(inter, vendaID)
                if embed == None:
                    return await inter.edit_original_message(f"{negativo} Venda `{vendaID}` não encontrada.")

                await inter.edit_original_message("", embed=embed, components=components, file=disnake.File(f"Database/Vendas/entregas/{vendaID}.txt", filename="itens_comprados.txt"),)

            else:
                await inter.response.send_message(f"{negativo} Faltam permissões para executar essa ação", ephemeral=True)

    @commands.Cog.listener("on_dropdown")
    async def CarrinhoDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith("ComprarCampo_"):
            produtoID = inter.component.custom_id.replace("ComprarCampo_", "")
            campoID = inter.values[0]
            await Carrinho.CriarCarrinho(inter, produtoID, campoID)

def setup(bot: commands.Bot):
    bot.add_cog(CarrinhoExtension(bot))