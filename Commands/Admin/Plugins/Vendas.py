from disnake.ext import commands
from datetime import *
from disnake import *
import requests
import disnake
import random
import string
import json
import re
import os

from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Functions.Config.Produto import *

# Modais

class AlterarInstrucoesModal(disnake.ui.Modal):
    def __init__(self):
        with open("Database/Vendas/vendas.json") as f:
            db = json.load(f)

        components = [
            disnake.ui.TextInput(
                label="Instruções",
                custom_id="instructions",
                value=db["instrucoes"],
                style=TextInputStyle.paragraph,
                required=False
            ),
        ]
        super().__init__(title="Configurar Instruções", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        instructions = inter.text_values["instructions"]
        with open("Database/Vendas/vendas.json") as f:
            db = json.load(f)
        
        db["instrucoes"] = instructions

        with open("Database/Vendas/vendas.json", "w") as f:
            json.dump(db, f, indent=4)
        
        await inter.response.send_message(f"{positivo} Alterações salvas com sucesso.", ephemeral=True)

class AlterarMarcaModal(disnake.ui.Modal):
    def __init__(self):
        with open("Database/Vendas/vendas.json") as f:
            db = json.load(f)

        components = [
            disnake.ui.TextInput(
                label="URL da sua imagem",
                custom_id="url",
                value=db["marca"]["url"],
                required=False,
                style=TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Cor primária (HEX)",
                custom_id="pri",
                max_length=6,
                min_length=6,
                required=False,
                value=db["marca"]["cores"]["principal"],
                style=TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Cor secundária (HEX)",
                custom_id="sec",
                value=db["marca"]["cores"]["sec"],
                max_length=6,
                min_length=6,
                required=False,
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(title="Configurar Marca", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        url = inter.text_values.get("url")
        cor_primaria = inter.text_values.get("pri")
        cor_secundaria = inter.text_values.get("sec")
        erro = f"{negativo} Você forneceu alguma informação errada. Tente novamente"

        def cor_hex_valida(cor):
            return bool(re.fullmatch(r"^[0-9A-Fa-f]{6}$", cor))

        if not cor_hex_valida(cor_primaria):
            return await inter.response.send_message(erro, ephemeral=True)

        if not cor_hex_valida(cor_secundaria):
            return await inter.response.send_message(erro, ephemeral=True)

        with open("Database/Vendas/vendas.json") as f:
            db = json.load(f)

        db["marca"]["url"] = url
        db["marca"]["cores"]["principal"] = cor_primaria
        db["marca"]["cores"]["sec"] = cor_secundaria

        with open("Database/Vendas/vendas.json", "w") as f:
            json.dump(db, f, indent=4)

        await inter.response.send_message(f"{positivo} Configurações atualizadas com sucesso!", ephemeral=True)

# Databases

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

# Paineis

def ObterPainelPrincipal(inter: disnake.MessageInteraction):
    db = ObterDatabase()

    embed = disnake.Embed(
        title="Gerenciar Painel de Vendas",
        description=f"""
Olá, **{inter.user.name}**,
Utilize este painel para gerenciar o sistema de vendas.
        """,
        color=disnake.Color(0x00FFFF),
        timestamp=datetime.now()
    )
    embed.add_field(name="Total de produtos fornecidos", value=f"{caixa} ``{len(db)} produto(s)``")
    embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1328079619026321563/1362201918658842874/0cb46b4b0e7ffcef2c33a922b215d228.jpg?ex=680231a5&is=6800e025&hm=3ae126a7e289f424d79ce141dc47527c1d3d51bec8dcdc33b5533c16b444c905&")

    components = [
        [
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Criar Produto", emoji=mais2, custom_id="CriarProdutoVendas"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Produtos", emoji=config3, custom_id="GerenciarProdutosVendas"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Personalizar Loja", emoji=wand, custom_id="GerenciarPersonalizarLoja", disabled=True)
        ],
        # [ # adicionar Sistema de personalizar loja -> tudo isso daqui
        #     disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Configurar Cargos", emoji=cargo, custom_id="GerenciarCargosVendas"),
        #     disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Configurar Marca", emoji=recibo, custom_id="GerenciarMarcaVendas"),
        #     disnake.ui.Button(label="Definir instruções", emoji=attach, custom_id="DefinirInstrucoesVendas"),
        # ], # dps adicionar sistema de saldo
        [
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Sistema de Saldo", emoji=dollar, custom_id="GerenciarSistemaDeSaldo", disabled=True),
            disnake.ui.Button(style=disnake.ButtonStyle.green, disabled=True, label="Sistema de Assinaturas", emoji="<:assinatura:1358866200138092656>", custom_id="GerenciarAssinaturas"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
        ],
    ]

    return embed, components

class Produto():
    class CriarProdutoModal(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="Nome",
                    custom_id="name",
                    placeholder="Insira o nome do seu produto",
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Descrição",
                    custom_id="desc",
                    placeholder="Insira uma descrição para seu produto",
                    required=False,
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Ícone (Opcional)",
                    placeholder="Insira uma URL de uma imagem ou gif",
                    custom_id="icon",
                    required=False,
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Banner (Opcional)",
                    placeholder="Insira uma URL de uma imagem ou gif",
                    custom_id="banner",
                    required=False,
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Criar Produto", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            db = ObterDatabase()
            
            produtoID = GerarString()
            nome = inter.text_values["name"]
            descricao = inter.text_values.get("desc", None)
            entrega_auto = "s"
            icone = inter.text_values.get("icon", None)
            banner = inter.text_values.get("banner", None)

            if entrega_auto == "s" or entrega_auto == "n":
                db[produtoID] = {
                    "nome": nome,
                    "desc": descricao,
                    "entrega": True if entrega_auto == "s" else False,
                    "assets": {
                        "icon": icone,
                        "banner": banner,
                        "hex": "00FFFF"
                    },
                    "campos": {},
                    "criadoEm": int(datetime.now().timestamp()),
                    "cupons": {},
                    "ids": []
                }

                with open("Database/Vendas/produtos.json", "w") as f:
                    json.dump(db, f, indent=4)
                
                embed, components = Produto.ObterPainelGerenciarProduto(inter, produtoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await inter.followup.send(f"{positivo} Produto **{nome}** criado com sucesso", delete_after=3, ephemeral=True)
            else:
                await inter.edit_original_message(f"{negativo} Você não informou corretamente a entrega automática.")

    class EditarProdutoModal(disnake.ui.Modal):
        def __init__(self, produtoID):
            self.produtoID = produtoID
            db = ObterProduto(produtoID)

            components = [
                disnake.ui.TextInput(
                    label="Nome",
                    custom_id="name",
                    placeholder="Insira o nome do seu produto",
                    style=TextInputStyle.short,
                    value=db["nome"]
                ),
                disnake.ui.TextInput(
                    label="Descrição",
                    custom_id="desc",
                    placeholder="Insira uma descrição para seu produto",
                    required=False,
                    value=db["desc"],
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Ícone (Opcional)",
                    placeholder="Insira uma URL de uma imagem ou gif",
                    custom_id="icon",
                    required=False,
                    value=db["assets"]["icon"],
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Banner (Opcional)",
                    placeholder="Insira uma URL de uma imagem ou gif",
                    custom_id="banner",
                    required=False,
                    value=db["assets"]["banner"],
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Hex da Embed",
                    custom_id="hex",
                    required=True,
                    placeholder="Coloque o HEX da Embed -> Sem #\nExemplo: FFFFFF para #FFFFFF",
                    style=TextInputStyle.short,
                    value=db["assets"]["hex"],
                    min_length=6,
                    max_length=6,
                ),
            ]
            super().__init__(title=f"Editar Produto {db["nome"]}", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            db = ObterDatabase()

            nome = inter.text_values["name"]
            descricao = inter.text_values.get("desc")
            entrega_auto = "s"
            icone = inter.text_values.get("icon", None)
            banner = inter.text_values.get("banner", None)
            hex = inter.text_values["hex"]

            def cor_hex_valida(cor):
                return bool(re.fullmatch(r"^[0-9A-Fa-f]{6}$", cor))

            if not cor_hex_valida(hex): return await inter.response.send_message(f"{negativo} Você não informou o HEX correto.\nUse um exemplo como esse: `FFFFFF` (branco, sem usar #)")

            if entrega_auto == "s" or entrega_auto == "n":
                db[self.produtoID] = {
                    "nome": nome,
                    "desc": descricao if descricao else "",
                    "entrega": True if entrega_auto == "s" else False,
                    "assets": {
                        "icon": icone if icone else "",
                        "banner": banner if banner else "",
                        "hex": hex
                    },
                    "campos": db[self.produtoID].get("campos", {}),
                    "criadoEm": db[self.produtoID].get("criadoEm", int(datetime.now().timestamp())),
                    "cupons": db[self.produtoID].get("cupons", {}),
                    "ids": db[self.produtoID].get("ids", [])
                }

                with open("Database/Vendas/produtos.json", "w") as f:
                    json.dump(db, f, indent=4)
            
                embed, components = Produto.ObterPainelGerenciarProduto(inter, self.produtoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await inter.followup.send(f"{positivo} Produto **{db[self.produtoID]["nome"]}** editado com sucesso", delete_after=3, ephemeral=True)
                await SincronizarMensagens(inter, self.produtoID)
            else:
                await inter.edit_original_message(f"{negativo} Você não informou corretamente a entrega automática.")

    @staticmethod
    async def GerenciarProdutos(inter: disnake.MessageInteraction):
        await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
        db = ObterDatabase()

        options = []
        for product_id, product_data in db.items():
            options.append(
                disnake.SelectOption(
                    label=product_data["nome"],
                    description=f"Campos: {len(product_data["campos"])} | Cupons: {len(product_data["cupons"])}",
                    value=product_id,
                    emoji=caixa
                )
            )
        
        if not options:
            options.append(
                disnake.SelectOption(
                    label="Nenhum produto disponível",
                ) 
            )
        
        select = disnake.ui.StringSelect(
            placeholder=f"[{len(db)}] Clique aqui para selecionar",
            custom_id="SelecionarProdutoDropdownVendas",
            options=options,
            disabled=True if len(db) == 0 else False
        )

        components = [
            select,
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Criar Produto", emoji=mais2, custom_id="CriarProdutoVendas"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarPainelVendas"),
        ]
        await inter.edit_original_message(f"{inter.user.mention} Qual produto deseja gerenciar?", embed=None, components=components)

    @staticmethod
    def ObterPainelGerenciarProduto(inter: disnake.MessageInteraction, produtoID: str):
        db = ObterDatabase()
        produto = ObterProduto(produtoID)
        desc = f"{negativo} ``Não definida``" if produto["desc"] == "" else produto["desc"]

        embed = disnake.Embed(
            description=f"""
    ### Detalhes
    **Descrição do produto:**
    {desc}
            """,
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_author(name=f"Gerenciando o produto: {produto["nome"]}")
        embed.add_field(name=f"Campos", value=f"-# {len(produto["campos"])} campo(s) fornecidos", inline=True)
        embed.add_field(name=f"Cupons", value=f"-# {len(produto["cupons"])} cupom(ns)", inline=True)
        embed.add_field(name=f"Informações das vendas", value=f"-# {len(produto["cupons"])} cupom(ns)", inline=True)
        embed.add_field(name=f"Entrega automática", value="-# Sim" if produto["entrega"] == True else "-# Não", inline=True)
        embed.add_field(name=f"Criado em", value=f"-# <t:{produto["criadoEm"]}:f>", inline=True)
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        components = [
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Editar Produto", emoji=editar, custom_id=f"EditarProduto_{produtoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Campos", emoji=caixa, custom_id=f"GerenciarCampos_{produtoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Cupons", emoji=cupom, custom_id=f"GerenciarCupons_{produtoID}"),
            ],
            [
                disnake.ui.Button(style=disnake.ButtonStyle.green, label="Colocar a venda", emoji=arrow, custom_id=f"ColocarVenda_{produtoID}"),
                disnake.ui.Button(
                    label="Entrega automática",
                    emoji=reload,
                    style=disnake.ButtonStyle.green if produto["entrega"] == True else disnake.ButtonStyle.red,
                    custom_id=f"AtivarDesativarEntregaAuto_{produtoID}"
                ),
                disnake.ui.Button(style=disnake.ButtonStyle.red, label="Excluir produto", emoji=apagar, custom_id=f"ApagarProduto_{produtoID}"),
            ],
            [
                disnake.ui.Button(label="Sincronizar Mensagens", emoji=reload, custom_id=f"SincronizarProduto_{produtoID}"),
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarProdutosVendas"),
            ]
        ]

        return embed, components

    @staticmethod
    def Apagar(produtoID: str):
        db = ObterDatabase()

        del(db[produtoID])

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

class Campo():
    class Criar(disnake.ui.Modal):
        def __init__(self, produtoID):
            self.produtoID = produtoID
            components = [
                disnake.ui.TextInput(
                    label="Nome do campo",
                    placeholder="Insira o nome desejado",
                    custom_id="name",
                    style=TextInputStyle.short,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Descrição do campo",
                    placeholder="Insira a descrição desejada",
                    custom_id="desc",
                    required=False,
                    style=TextInputStyle.paragraph,
                ),
                disnake.ui.TextInput(
                    label="Preço do campo",
                    placeholder="Insira o preço desejado (BRL)",
                    custom_id="price",
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Criar Campo", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            db = ObterDatabase()
            produto = ObterProduto(self.produtoID)
            campoID = GerarString()
            nome = inter.text_values["name"]
            desc = inter.text_values["desc"]
            preco = inter.text_values["price"]

            try:
                preco = float(preco)
                preco = "{:.2f}".format(preco)
            except: return await inter.response.send_message(f"{negativo} Você informou um valor errado. Utilize números inteiros/quebrados positivos.", ephemeral=True)

            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)

            db[self.produtoID]["campos"][campoID] = {
                "nome": nome,
                "desc": desc,
                "preco": preco,
                "condicoes": {
                    "valorMin": None,
                    "valorMax": None,
                    "quantidadeMin": None,
                    "quantidadeMax": None,
                    "idCargo": []
                },
                "estoque": [],
                "estoqueinfo": {
                    "last": None,
                    "alertas": []
                },
                "cargos": {
                    "add": [],
                    "rem": []
                }
            }

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            embed, components = Campo.ObterPainelGerenciarCampo(inter, self.produtoID, campoID)
            await inter.edit_original_message("", embed=embed, components=components)
            await SincronizarMensagens(inter, self.produtoID)

    class Editar(disnake.ui.Modal):
        def __init__(self, produtoID, campoID):
            self.produtoID = produtoID
            self.campoID = campoID

            campo = ObterCampo(produtoID=produtoID, campoID=campoID)

            components = [
                disnake.ui.TextInput(
                    label="Nome do campo",
                    placeholder="Insira o nome desejado",
                    custom_id="name",
                    value=campo["nome"],
                    style=TextInputStyle.short,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Descrição do campo",
                    placeholder="Insira a descrição desejada",
                    custom_id="desc",
                    required=False,
                    value=campo["desc"],
                    style=TextInputStyle.paragraph,
                ),
                disnake.ui.TextInput(
                    label="Preço do campo",
                    placeholder="Insira o preço desejado (BRL)",
                    custom_id="price",
                    value=f"{campo["preco"]}",
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Criar Campo", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            db = ObterDatabase()
            produto = ObterProduto(self.produtoID)
            nome = inter.text_values["name"]
            desc = inter.text_values["desc"]
            preco = inter.text_values["price"]

            try:
                preco = float(preco)
                preco = "{:.2f}".format(preco)
            except: return await inter.response.send_message(f"{negativo} Você informou um valor errado. Utilize números inteiros/quebrados positivos.", ephemeral=True)

            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)

            db[self.produtoID]["campos"][self.campoID]["nome"] = nome
            db[self.produtoID]["campos"][self.campoID]["desc"] = desc
            db[self.produtoID]["campos"][self.campoID]["preco"] = preco

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            embed, components = Campo.ObterPainelGerenciarCampo(inter, self.produtoID, self.campoID)
            await inter.edit_original_message("", embed=embed, components=components)
            await SincronizarMensagens(inter, self.produtoID)

    class Condicoes(disnake.ui.Modal):
        def __init__(self, produtoID, campoID):
            self.produtoID = produtoID
            self.campoID = campoID

            campo = ObterCampo(produtoID=produtoID, campoID=campoID)
            idsFormatado = "\n".join(map(str, campo["condicoes"]["idCargo"]))
            valorMin = str(campo["condicoes"]["valorMin"]) if campo["condicoes"]["valorMin"] else ""
            valorMax = str(campo["condicoes"]["valorMin"]) if campo["condicoes"]["valorMax"] else ""
            quantidadeMin = str(campo["condicoes"]["quantidadeMin"]) if campo["condicoes"]["quantidadeMin"] else ""
            quantidadeMax = str(campo["condicoes"]["quantidadeMax"]) if campo["condicoes"]["quantidadeMax"] else ""

            components = [
                disnake.ui.TextInput(
                    label="Valor mínimo",
                    placeholder="Coloque o valor mínimo para comprar",
                    custom_id="valuemin",
                    required=False,
                    value=valorMin,
                    style=TextInputStyle.short,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Valor máximo",
                    placeholder="Coloque o valor máximo para comprar",
                    custom_id="valuemax",
                    required=False,
                    value=valorMax,
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Quantidade mínima",
                    placeholder="Coloque a quantidade mínima para comprar",
                    custom_id="quantidademin",
                    required=False,
                    value=quantidadeMin,
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Quantidade máxima",
                    placeholder="Coloque a quantidade máxima para comprar",
                    custom_id="quantidademax",
                    required=False,
                    value=quantidadeMax,
                    style=TextInputStyle.short, 
                ),
            ]
            super().__init__(title="Gerenciar Condições", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            try:
                valuemin = float(inter.text_values["valuemin"]) if inter.text_values["valuemin"] else None
                valuemax = float(inter.text_values["valuemax"]) if inter.text_values["valuemax"] else None
                quantidademin = int(inter.text_values["quantidademin"]) if inter.text_values["quantidademin"] else None
                quantidademax = int(inter.text_values["quantidademax"]) if inter.text_values["quantidademax"] else None
            except:
                await inter.response.send_message(f"{negativo} Você informou algum valor inválido.")

            db = ObterDatabase()
            campo = db[self.produtoID]["campos"][self.campoID]
            campo["condicoes"]["valorMin"] = valuemin
            campo["condicoes"]["valorMax"] = valuemax
            campo["condicoes"]["quantidadeMin"] = quantidademin
            campo["condicoes"]["quantidadeMax"] = quantidademax
        
            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            embed, components = Campo.ObterPainelGerenciarCampo(inter, self.produtoID, self.campoID)
            await inter.response.edit_message(embed=embed, components=components)

    class Cargos():
        @staticmethod
        def ObterDropdown(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
            campo = ObterCampo(produtoID=produtoID, campoID=campoID)

            roleAdd = []
            for roleID in campo["cargos"]["add"]:
                try:
                    role = inter.guild.get_role(int(roleID))
                    if role:
                        roleAdd.append(SelectDefaultValue(id=role.id, type=SelectDefaultValueType.role))
                except: 
                    pass

            roleRem = []
            for roleID in campo["cargos"]["rem"]:
                try:
                    role = inter.guild.get_role(int(roleID))
                    if role:
                        roleRem.append(SelectDefaultValue(id=role.id, type=SelectDefaultValueType.role))
                except: 
                    pass

            dropdownCargos = [
                disnake.ui.RoleSelect(
                    placeholder="Selecione os cargos para serem adicionados",
                    max_values=25,
                    min_values=0,
                    custom_id=f"GerenciarCargos_Adicionar_{produtoID}_{campoID}",
                    default_values=roleAdd if roleAdd else None
                ),
                disnake.ui.RoleSelect(
                    placeholder="Selecione os cargos para serem removidos",
                    max_values=25,
                    min_values=0,
                    custom_id=f"GerenciarCargos_Remover_{produtoID}_{campoID}",
                    default_values=roleRem if roleRem else None
                ),
            ]

            return dropdownCargos
        
        @staticmethod
        def atualizarDB(produtoID: str, campoID: str, cargosAdd=None, cargosRem=None):
            db = ObterDatabase()

            if cargosAdd:
                db[produtoID]["campos"][campoID]["cargos"]["add"] = cargosAdd if cargosAdd else []
            
            if cargosRem:
                db[produtoID]["campos"][campoID]["cargos"]["rem"] = cargosRem if cargosRem else []

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)

    @staticmethod
    async def Apagar(inter, produtoID: str, campoID: str):
        db = ObterDatabase()
        del(db[produtoID]["campos"][campoID])

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

        await SincronizarMensagens(inter, produtoID)


    @staticmethod
    async def GerenciarCampos(inter: disnake.MessageInteraction, produtoID: str):
        await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
        db = ObterDatabase()
        campos = db[produtoID]["campos"]

        options = []
        for campoID, campodata in campos.items():
            options.append(
                disnake.SelectOption(
                    label=campodata["nome"],
                    description=f"R${campodata["preco"]}",
                    value=f"{produtoID}_{campoID}",
                    emoji=config3
                )
            )
        
        if not options:
            options.append(
                disnake.SelectOption(
                    label="Nenhum campo disponível",
                ) 
            )
        
        select = disnake.ui.StringSelect(
            placeholder=f"[{len(campos)}] Clique aqui para selecionar",
            custom_id="SelecionarCampoDropdownVendas",
            options=options,
            disabled=True if len(campos) == 0 else False
        )

        components = [
            select,
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Criar Campo", emoji=mais2, custom_id=f"CriarCampo_{produtoID}"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id=f"GerenciarProduto_{produtoID}"),
        ]
        await inter.edit_original_message(f"{inter.user.mention} Qual campo deseja gerenciar?", embed=None, components=components)

    @staticmethod
    def ObterPainelGerenciarCampo(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
        produto = ObterProduto(produtoID=produtoID)
        campo = ObterCampo(produtoID=produtoID, campoID=campoID)

        embed = disnake.Embed(
            description=f"""
### Detalhes
**Nome do produto:** ``{produto["nome"]}``
**Nome do campo:** ``{campo["nome"]}``
**Preço do campo:** ``R${campo["preco"]}``
**Descrição:**
{f"{negativo} ``Não informado``" if campo["desc"] == "" else campo["desc"]}
            """,
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Condições", 
        value=f"""
-# Valor mínimo: {f"{negativo} ``Não informado``" if campo["condicoes"]["valorMin"] == None else f"`R${campo["condicoes"]["valorMin"]}`"}
-# Valor máximo: {f"{negativo} ``Não informado``" if campo["condicoes"]["valorMax"] == None else f"`R${campo["condicoes"]["valorMax"]}`"}
-# Quantidade mínima: {f"{negativo} ``Não informado``" if campo["condicoes"]["quantidadeMin"] == None else f"`{campo["condicoes"]["quantidadeMin"]}`"}
-# Quantidade máxima: {f"{negativo} ``Não informado``" if campo["condicoes"]["quantidadeMax"] == None else f"`{campo["condicoes"]["quantidadeMax"]}`"}
-# Quem não pode comprar? {len(campo["condicoes"]["idCargo"])} cargos
        """,
        inline=False)
        embed.add_field(name="Estoque disponível", value=f"``{len(campo["estoque"])}``", inline=True)
        embed.add_field(name="Última reposição", value=f"{f"<t:{campo["estoqueinfo"]["last"]}:f>" if campo["estoqueinfo"]["last"] else f"{negativo} ``Não disponível``"}", inline=True)
        embed.add_field(name="Cargos", value=f"""
-# Para adicionar: `{len(campo["cargos"]["add"])}`
-# Para remover: `{len(campo["cargos"]["rem"])}`
        """,
        inline=False)

        components = [
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Editar Campo", emoji=editar, custom_id=f"EditarCampo_{produtoID}_{campoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Estoque", emoji=caixa, custom_id=f"GerenciarEstoque_{produtoID}_{campoID}"),
            ],
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Condições", emoji=attach, custom_id=f"GerenciarCondicoes_{produtoID}_{campoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Gerenciar Cargos", emoji=users, custom_id=f"GerenciarCargos_{produtoID}_{campoID}"),
            ],
            [

                disnake.ui.Button(style=disnake.ButtonStyle.red, label="Excluir campo", emoji=apagar, custom_id=f"ApagarCampo_{produtoID}_{campoID}"),
                disnake.ui.Button(style=disnake.ButtonStyle.red, label="Limpar Estoque", emoji=wand, custom_id=f"LimparEstoque_{produtoID}_{campoID}"),
            ],
            [
                disnake.ui.Button(label="Sincronizar Mensagens", emoji=reload, custom_id=f"SincronizarProduto_{produtoID}"),
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id=f"GerenciarProduto_{produtoID}"),
            ]
        ]

        return embed, components

    class Estoque():
        class AdicionarEstoqueFantasmaModal(disnake.ui.Modal):
            def __init__(self, produtoID: str, campoID: str):
                self.produtoID = produtoID
                self.campoID = campoID
                components = [
                    disnake.ui.TextInput(
                        label="Quantidade do Estoque Fantasma",
                        custom_id="quantidade_fantasma",
                        style=disnake.TextInputStyle.short,
                        placeholder="Digite a quantidade (número inteiro)",
                    ),
                    disnake.ui.TextInput(
                        label="Valor/Informação Entregue",
                        custom_id="valor_fantasma",
                        style=disnake.TextInputStyle.paragraph,
                        placeholder="Exemplo: Abra um suporte para resolver o problema",
                        required=True
                    ),
                ]
                super().__init__(title="Adicionar Estoque Fantasma", components=components)

            async def callback(self, inter: disnake.ModalInteraction):
                quantidade_texto = inter.text_values.get("quantidade_fantasma", "").strip()
                valor_fantasma = inter.text_values.get("valor_fantasma", "").strip()

                try:
                    quantidade = int(quantidade_texto)
                    if quantidade <= 0:
                        return await inter.response.send_message(f"{negativo} Quantidade inválida: insira um número inteiro maior que zero.", ephemeral=True)
                except ValueError:
                    await inter.response.send_message(f"{negativo} Quantidade inválida: insira um número inteiro maior que zero.", ephemeral=True)
                    return
            
                db = ObterDatabase()
                estoque_fantasma = [valor_fantasma] * quantidade
                db[self.produtoID]["campos"][self.campoID]["estoque"].extend(estoque_fantasma)
                db[self.produtoID]["campos"][self.campoID]["estoqueinfo"]["last"] = int(datetime.now().timestamp())

                with open("Database/Vendas/produtos.json", "w") as f:
                    json.dump(db, f, indent=4)

                embed, components = Campo.ObterPainelGerenciarCampo(inter, self.produtoID, self.campoID)
                await inter.response.edit_message("", embed=embed, components=components)
                await inter.followup.send(f"{positivo} Estoque adicionado com sucesso.\nInformações: ``{quantidade_texto}x {valor_fantasma}``", ephemeral=True)
                await SincronizarMensagens(inter, self.produtoID)
                await NotificarUserEstoque(inter, self.produtoID, self.campoID)

        class AdicionarEstoqueModal(disnake.ui.Modal):
            def __init__(self, produtoID, campoID):
                self.produtoID = produtoID
                self.campoID = campoID
                components = [
                    disnake.ui.TextInput(
                        label="Estoque (separado por linha)",
                        custom_id="estoque",
                        style=TextInputStyle.long,
                    ),
                ]
                super().__init__(title="Adicionar Estoque", components=components)

            async def callback(self, inter: disnake.ModalInteraction):
                await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)

                estoque_texto = inter.text_values.get("estoque")
                estoque_itens = [item.strip() for item in estoque_texto.split("\n") if item.strip()]
                
                if not estoque_itens:
                    await inter.response.send_message(f"{negativo} Nenhum item válido detectado no estoque.", ephemeral=True)
                    return

                db = ObterDatabase()
                db[self.produtoID]["campos"][self.campoID]["estoque"].extend(estoque_itens)
                db[self.produtoID]["campos"][self.campoID]["estoqueinfo"]["last"] = int(datetime.now().timestamp())

                with open("Database/Vendas/produtos.json", "w") as f:
                    json.dump(db, f, indent=4)

                embed, components = Campo.ObterPainelGerenciarCampo(inter, self.produtoID, self.campoID)
                await inter.edit_original_message("", embed=embed, components=components)
                await inter.followup.send(f"{positivo} Estoque adicionado com sucesso.", ephemeral=True)
                await SincronizarMensagens(inter, self.produtoID)
                await NotificarUserEstoque(inter, self.produtoID, self.campoID)

        @staticmethod
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
    
        @staticmethod
        async def AdicionarEstoqueArquivo(inter: disnake.MessageInteraction, produtoID: str, campoID: str):
            db = ObterDatabase()
            await inter.response.send_message("Envie o arquivo `.txt` contendo o estoque.", ephemeral=True)
            
            def check(message):
                return message.author == inter.author and isinstance(message, disnake.Message) and message.attachments
            
            try:
                msg = await inter.bot.wait_for("message", check=check, timeout=60.0)
            except Exception as e:
                return await inter.edit_original_message(f"{negativo} Tempo esgotado. Operação cancelada.")
            
            for attachment in msg.attachments:
                if attachment.filename.endswith(".txt"):
                    file_content = await attachment.read()
                    file_content = file_content.decode("utf-8")
                    
                    estoque_itens = [item.strip() for item in file_content.split("\n") if item.strip()]
                    
                    db[produtoID]["campos"][campoID]["estoque"].extend(estoque_itens)
                    db[produtoID]["campos"][campoID]["estoqueinfo"]["last"] = int(datetime.now().timestamp())
                    
                    with open("Database/Vendas/produtos.json", "w") as f:
                        json.dump(db, f, indent=4)
                    
                    await msg.delete()
            
            embed, components = Campo.ObterPainelGerenciarCampo(inter, produtoID, campoID)
            await inter.edit_original_message("", embed=embed, components=components)
            
            await inter.followup.send(f"{positivo} Estoque adicionado com sucesso.", ephemeral=True)
            await SincronizarMensagens(inter, produtoID)
            await NotificarUserEstoque(inter, produtoID, campoID)

        @staticmethod
        def ApagarEstoque(produtoID: str, campoID: str):
            db = ObterDatabase()
            db[produtoID]["campos"][campoID]["estoque"] = []

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)

        @staticmethod
        def ObterEstoque(produtoID: str, campoID: str):
            nome_arquivo = f"Estoque_{produtoID}_{campoID}.txt"
            caminho_pasta = os.path.join("Database", "Vendas", "temp")
            caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
            
            campo = ObterCampo(produtoID, campoID)
            os.makedirs(caminho_pasta, exist_ok=True)
            
            with open(caminho_completo, "w", encoding="utf-8") as arquivo:
                for linha in campo["estoque"]:
                    arquivo.write(linha + "\n")
            
            return caminho_completo

        @staticmethod
        def ObterItemEstoque(produtoID: str, campoID: str):
            db = ObterDatabase()
            estoque = db[produtoID]["campos"][campoID]["estoque"]
            item = estoque.pop(0)
            
            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            return item

class Cupom():
    class CriarModal(disnake.ui.Modal):
        def __init__(self, produtoID: str):
            self.produtoID = produtoID
            components = [
                disnake.ui.TextInput(
                    label="Código do cupom",
                    placeholder="Ex: DESCONTO10",
                    custom_id="code",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Porcentagem de desconto (%)",
                    placeholder="Ex: 10 para 10% ou 5.5 para 5,5%",
                    custom_id="porcentagem",
                    style=disnake.TextInputStyle.short,
                ),
            ]
            super().__init__(title="Criar Cupom", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            nome_cupom = inter.text_values["code"].strip()
            porcentagem_texto = inter.text_values["porcentagem"].strip()

            try:
                porcentagem = float(porcentagem_texto)
                if porcentagem <= 0 or porcentagem > 100:
                    return await inter.response.send_message(f"{negativo} Insira um valor numérico válido entre 0 e 100!", ephemeral=True)
            except ValueError:
                return await inter.response.send_message(f"{negativo} Insira um valor numérico válido entre 0 e 100!", ephemeral=True)

            Cupom.Criar(nome_cupom, porcentagem, self.produtoID)
            embed, components = Cupom.ObterPainel(inter, self.produtoID, nome_cupom)
            await inter.response.edit_message("", embed=embed, components=components)

    class EditarModal(disnake.ui.Modal):
        def __init__(self, produtoID: str, nome: str):
            self.produtoID = produtoID
            self.nome = nome

            cupom = ObterCupom(produtoID, nome)

            components = [
                disnake.ui.TextInput(
                    label="Código do cupom",
                    placeholder="Ex: DESCONTO10",
                    custom_id="code",
                    style=disnake.TextInputStyle.short,
                    value=cupom["nome"],
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Porcentagem de desconto (%)",
                    placeholder="Ex: 10 para 10% ou 5.5 para 5,5%",
                    custom_id="porcentagem",
                    value=f"{cupom["porcentagem"]}",
                    style=disnake.TextInputStyle.short,
                ),
            ]
            super().__init__(title="Editar Cupom", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            nome_cupom = inter.text_values["code"].strip()
            porcentagem_texto = inter.text_values["porcentagem"].strip()

            try:
                porcentagem = float(porcentagem_texto)
                if porcentagem <= 0 or porcentagem > 100:
                    return await inter.response.send_message(f"{negativo} Insira um valor numérico válido entre 0 e 100!", ephemeral=True)
            except ValueError:
                return await inter.response.send_message(f"{negativo} Insira um valor numérico válido entre 0 e 100!", ephemeral=True)

            Cupom.Editar(nome_cupom, porcentagem, self.produtoID)
            embed, components = Cupom.ObterPainel(inter, self.produtoID, nome_cupom)
            await inter.response.edit_message("", embed=embed, components=components)

    class AvançadosModal(disnake.ui.Modal):
        def __init__(self, produtoID: str, nome: str):
            self.produtoID = produtoID
            self.nome = nome

            cupom = ObterCupom(produtoID, nome)

            components = [
                disnake.ui.TextInput(
                    label="Valor mínimo para usar",
                    placeholder="Ex: 10 para 10 reais",
                    custom_id="value",
                    required=False,
                    style=disnake.TextInputStyle.short,
                    value=cupom["usage"]["minvalue"],
                ),
                disnake.ui.TextInput(
                    label="Uso máximos (TOTAL)",
                    placeholder="Ex: 10 para 10 usos total",
                    custom_id="uses",
                    required=False,
                    value=cupom["usage"]["maxuses"],
                    style=disnake.TextInputStyle.short,
                ),
            ]
            super().__init__(title="Editar Avançados Cupom", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            try:
                valormin = int(inter.text_values["value"].strip()) if inter.text_values["value"].strip() else ""
                usemax = int(inter.text_values["uses"].strip()) if inter.text_values["uses"].strip() else ""
            except:
                return await inter.response.send_message(f"{negativo} Forneça números válidos.", ephemeral=True)

            db = ObterDatabase()
            db[self.produtoID]["cupons"][self.nome] = {
                "nome": db[self.produtoID]["cupons"][self.nome]["nome"],
                "porcentagem": db[self.produtoID]["cupons"][self.nome]["porcentagem"],
                "usage": {
                    "minvalue": valormin,
                    "maxuses": usemax
                },
                "estatistics": {
                    "uses": db[self.produtoID]["cupons"][self.nome]["estatistics"]["uses"],
                    "economizado": db[self.produtoID]["cupons"][self.nome]["estatistics"]["economizado"]
                },
            }

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = Cupom.ObterPainel(inter, self.produtoID, self.nome)
            await inter.response.edit_message("", embed=embed, components=components)

    @staticmethod
    def Criar(nome, porcentagem, produtoID):
        db = ObterDatabase()

        db[produtoID]["cupons"][nome] = {
            "nome": nome,
            "porcentagem": float(porcentagem),
            "usage": {
                "minvalue": "",
                "maxuses": ""
            },
            "estatistics": {
                "uses": 0,
                "economizado": 0
            },
        }

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)

    @staticmethod
    def Editar(nome, porcentagem, produtoID):
        db = ObterDatabase()

        db[produtoID]["cupons"][nome] = {
            "nome": nome,
            "porcentagem": float(porcentagem),
            "usage": {
                "minvalue": db[produtoID]["cupons"][nome]["usage"]["minvalue"],
                "maxuses": db[produtoID]["cupons"][nome]["usage"]["maxuses"]
            },
            "estatistics": {
                "uses": db[produtoID]["cupons"][nome]["estatistics"]["uses"],
                "economizado": db[produtoID]["cupons"][nome]["estatistics"]["economizado"]
            },
        }

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)
    
    @staticmethod
    def Apagar(produtoID, nome):
        db = ObterDatabase()
        del db[produtoID]["cupons"][nome]

        with open("Database/Vendas/produtos.json", "w") as f:
            json.dump(db, f, indent=4)


    @staticmethod
    async def GerenciarCupons(inter: disnake.MessageInteraction, produtoID: str):
        await inter.response.edit_message(f"{carregarAnimado} Carregando cupons...", embed=None, components=None)

        db = ObterDatabase()

        product_data = db[produtoID]
        cupons = product_data.get("cupons", {})

        options = []
        for cupom_id, cupom_data in cupons.items():
            desconto = cupom_data.get("porcentagem", "Desconhecido")
            options.append(
                disnake.SelectOption(
                    label=f"{cupom_id}",
                    description=f"Porcentagem: {desconto}%",
                    value=f"{produtoID}_{cupom_id}"
                )
            )

        if not options:
            options.append(
                disnake.SelectOption(
                    label="Nenhum cupom disponível",
                    value="nenhum",
                    description="Não há cupons cadastrados."
                )
            )

        select = disnake.ui.StringSelect(
            placeholder=f"[{len(cupons)}] Selecione um cupom para gerenciar",
            custom_id="SelecionarCupomDropdownVendas",
            options=options,
            disabled=len(options) == 1 and options[0].value == "nenhum"
        )

        components = [
            select,
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Adicionar Cupom", emoji=mais2, custom_id=f"AdicionarCupom_{produtoID}"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id=f"GerenciarProduto_{produtoID}"),
        ]

        await inter.edit_original_message(
            content=f"{inter.user.mention} Qual cupom deseja gerenciar?",
            embed=None,
            components=components
        )

    @staticmethod
    def ObterPainel(inter, produtoID, nome):
        db = ObterDatabase()
        cupom = db[produtoID]["cupons"][nome]
        valorMin = f"R${cupom["usage"]["minvalue"]}" if cupom["usage"]["minvalue"] != "" else f"Não definido"
        maxUses = f"{cupom["usage"]["maxuses"]}" if cupom["usage"]["maxuses"] != "" else f"Não definido"
        usos = f"{cupom["estatistics"]["uses"]}"
        economizado = f"R${cupom["estatistics"]["economizado"]}"

        embed = disnake.Embed(
            description=f"""
### Detalhes
**Nome/Código:** ``{nome}``
**Porcentagem:** ``{cupom["porcentagem"]}%``
            """,
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_author(name=f"Gerenciando o cupom: {nome}")
        embed.add_field(name="Informações Avançadas", value=f"-# Valor mínimo: {valorMin}\n-# Usos máximos: {maxUses}", inline=True)
        embed.add_field(name="Estatísticas", value=f"-# Usos: {usos}\n-# Valor economizado: {economizado}", inline=True)
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        components = [
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Editar", emoji=editar, custom_id=f"EditarCupom_{produtoID}_{nome}"),
                disnake.ui.Button(style=disnake.ButtonStyle.grey, label="Avançados", emoji=config2, custom_id=f"Avancados_{produtoID}_{nome}"),
            ],
            [

                disnake.ui.Button(style=disnake.ButtonStyle.red, label="Excluir Cupom", emoji=apagar, custom_id=f"ApagarCupom_{produtoID}_{nome}"),
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id=f"GerenciarCupons_{produtoID}"),
            ]
        ]

        if cupom: return embed, components
        else: return None, None

# Personalizar Loja
class PersonalizarLoja():
    async def PersonalizarLoja(inter: disnake.MessageInteraction):
        with open("Database/Vendas/vendas.json") as f:
            config = json.load(f)
        
        embed = disnake.Embed(
            title="Personalizar Loja",
            description="""
Aqui você consegue personalizar e configurar a sua loja do seu jeito. Use sua criatividade para alterar cores, cargos e instruções.
**Lembre-se:** as alterações são utilizadas apenas na parte do carrinho.
""",
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )

# Events Listener

class VendasCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands

    @commands.slash_command()
    async def manage(self, inter):
        pass

    @manage.sub_command(description="Use to manage a specific product")
    async def produto(
        self,
        inter: disnake.ApplicationCommandInteraction,
        produto: str = commands.Param(description="Selecione um produto", autocomplete=True),
    ):
        if not VerificarDM(inter):
            return await inter.response.send_message(f"{negativo} Use este comando apenas em servidores", ephemeral=True)
        
        if produto != "FaltamPermissoes":
            embed, components = Produto.ObterPainelGerenciarProduto(inter, produto)
            await inter.response.send_message(embed=embed, components=components, ephemeral=True)
        else: await inter.response.send_message(f"{negativo} Faltam permissões.", ephemeral=True)

    @produto.autocomplete("produto")
    async def produto_autocomplete(
        self, inter: disnake.ApplicationCommandInteraction, string: str
    ):
        produtos_db = ObterDatabase()

        if verificar_permissao(inter.user.id):
            suggestions = [
                disnake.OptionChoice(
                    name=f"🛒 {dados['nome']}",
                    value=produto_id
                )
                for produto_id, dados in produtos_db.items()
                if string.lower() in dados["nome"].lower()
            ]
        else:
            suggestions = [
                disnake.OptionChoice(
                    name="❌ Faltam permissões",
                    value="FaltamPermissoes"
                )
            ]

        return suggestions[:25]

    @manage.sub_command(description="Use to manage a specific item")
    async def item(
        self,
        inter: disnake.ApplicationCommandInteraction,
        opcao: str = commands.Param(description="Selecione um produto e campo", autocomplete=True),
    ):
        if not VerificarDM(inter):
            return await inter.response.send_message(f"{negativo} Use este comando apenas em servidores", ephemeral=True)
        
        if opcao != "FaltamPermissoes":
            produto_id, campo_id = opcao.split(":")
            embed, components = Campo.ObterPainelGerenciarCampo(inter, produto_id, campo_id)
            await inter.response.send_message(embed=embed, components=components, ephemeral=True)
        else: await inter.response.send_message(f"{negativo} Faltam permissões.", ephemeral=True)

    @item.autocomplete("opcao")
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
                    name="❌ Faltam permissões",
                    value="FaltamPermissoes"
                )
            ]

        return suggestions[:25]

    # Listener

    @commands.Cog.listener("on_button_click")
    async def VendasButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelVendas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = ObterPainelPrincipal(inter)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id == "DefinirInstrucoesVendas": await inter.response.send_modal(AlterarInstrucoesModal())
        elif inter.component.custom_id == "GerenciarMarcaVendas": await inter.response.send_modal(AlterarMarcaModal())

        elif inter.component.custom_id == "CriarProdutoVendas": await inter.response.send_modal(Produto.CriarProdutoModal())
        elif inter.component.custom_id == "GerenciarProdutosVendas": await Produto.GerenciarProdutos(inter=inter)

        elif inter.component.custom_id.startswith("EditarProduto_"):
            produtoID = inter.component.custom_id.replace("EditarProduto_", "")
            await inter.response.send_modal(Produto.EditarProdutoModal(produtoID))
        
        elif inter.component.custom_id.startswith("GerenciarProduto_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            produtoID = inter.component.custom_id.replace("GerenciarProduto_", "")
            produto = ObterProduto(produtoID)
            if produto:
                embed, components = Produto.ObterPainelGerenciarProduto(inter, produtoID)
                await inter.edit_original_message("", embed=embed, components=components)
            else: await inter.edit_original_message(f"{negativo} O produto não foi encontrado. Tente novamente.")

        elif inter.component.custom_id.startswith("ApagarProduto_"):
            produtoID = inter.component.custom_id.replace("ApagarProduto_", "")
            Produto.Apagar(produtoID)
            await Produto.GerenciarProdutos(inter)
            await SincronizarMensagens(inter, produtoID)

        elif inter.component.custom_id.startswith("GerenciarCupons_"):
            produtoID = inter.component.custom_id.replace("GerenciarCupons_", "")
            await Cupom.GerenciarCupons(inter, produtoID)
        
        elif inter.component.custom_id.startswith("AdicionarCupom_"):
            produtoID = inter.component.custom_id.replace("AdicionarCupom_", "")
            await inter.response.send_modal(Cupom.CriarModal(produtoID))

        elif inter.component.custom_id.startswith("EditarCupom_"):
            _, produtoID, cupom = inter.component.custom_id.split("_")
            await inter.response.send_modal(Cupom.EditarModal(produtoID=produtoID, nome=cupom))

        elif inter.component.custom_id.startswith("Avancados_"):
            _, produtoID, cupom = inter.component.custom_id.split("_")
            await inter.response.send_modal(Cupom.AvançadosModal(produtoID, cupom))

        elif inter.component.custom_id.startswith("ApagarCupom_"):
            _, produtoID, cupom = inter.component.custom_id.split("_")
            Cupom.Apagar(produtoID=produtoID, nome=cupom)

            await Cupom.GerenciarCupons(inter, produtoID)

        elif inter.component.custom_id.startswith("GerenciarCampos_"):
            produtoID = inter.component.custom_id.replace("GerenciarCampos_", "")
            await Campo.GerenciarCampos(inter, produtoID)
        
        elif inter.component.custom_id.startswith("CriarCampo_"):
            produtoID = inter.component.custom_id.replace("CriarCampo_", "")
            await inter.response.send_modal(Campo.Criar(produtoID))

        elif inter.component.custom_id.startswith("GerenciarCampo_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            _, produtoID, campoID = inter.component.custom_id.split("_")
            embed, components = Campo.ObterPainelGerenciarCampo(inter, produtoID, campoID)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("EditarCampo_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await inter.response.send_modal(Campo.Editar(produtoID=produtoID, campoID=campoID))
        
        elif inter.component.custom_id.startswith("ApagarCampo_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await Campo.Apagar(inter, produtoID, campoID)
            await Campo.GerenciarCampos(inter, produtoID)
        
        elif inter.component.custom_id.startswith("GerenciarCondicoes_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await inter.response.send_modal(Campo.Condicoes(produtoID=produtoID, campoID=campoID))
        
        elif inter.component.custom_id.startswith("GerenciarCargos_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            components = Campo.Cargos.ObterDropdown(inter, produtoID, campoID)
            components.append(
                disnake.ui.Button(
                    label="Voltar",
                    emoji=voltar,
                    custom_id=f"GerenciarCampo_{produtoID}_{campoID}"),
            )
            await inter.response.edit_message(components=components)

        elif inter.component.custom_id.startswith("GerenciarEstoque_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            if verificar_permissao(inter.user.id):
                _, produtoID, campoID = inter.component.custom_id.split("_")
                embed, components = Campo.Estoque.ObterPainelGerenciarEstoque(inter, produtoID, campoID)
                await inter.edit_original_message("", embed=embed, components=components)
            else: await inter.edit_original_message(f"{negativo} Você não tem permissão para executar essa função.")
            
        elif inter.component.custom_id.startswith("LimparEstoque_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            _, produtoID, campoID = inter.component.custom_id.split("_")
            Campo.Estoque.ApagarEstoque(produtoID, campoID)
            embed, components = Campo.ObterPainelGerenciarCampo(inter, produtoID, campoID)
            await inter.edit_original_message("", embed=embed, components=components)
            await SincronizarMensagens(inter, produtoID)

        elif inter.component.custom_id.startswith("AdicionarEstoqueFantasma_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await inter.response.send_modal(Campo.Estoque.AdicionarEstoqueFantasmaModal(produtoID, campoID))

        elif inter.component.custom_id.startswith("AdicionarEstoque_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await inter.response.send_modal(Campo.Estoque.AdicionarEstoqueModal(produtoID, campoID))

        elif inter.component.custom_id.startswith("VerEstoque_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            campo = ObterCampo(produtoID, campoID)
            if len(campo["estoque"]) <= 0:
                return await inter.response.send_message(f"{negativo} Não há estoque no produto.", ephemeral=True, delete_after=3)
            
            estoquefp = Campo.Estoque.ObterEstoque(produtoID, campoID)
            await inter.response.send_message(files=[disnake.File(fp=estoquefp)], ephemeral=True)
            os.remove(estoquefp)
        
        elif inter.component.custom_id.startswith("PegarItemEstoque_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            campo = ObterCampo(produtoID, campoID)
            if len(campo["estoque"]) <= 0:
                return await inter.response.send_message(f"{negativo} Não há estoque no produto.", ephemeral=True, delete_after=3)
            
            item = Campo.Estoque.ObterItemEstoque(produtoID, campoID)
            await inter.response.send_message(f"{positivo} Seu item está pronto:\n```{item}```", ephemeral=True)
            await SincronizarMensagens(inter, produtoID)

        elif inter.component.custom_id.startswith("EnviarArquivoEstoque_"):
            _, produtoID, campoID = inter.component.custom_id.split("_")
            await Campo.Estoque.AdicionarEstoqueArquivo(inter, produtoID, campoID)

        elif inter.component.custom_id.startswith("ColocarVenda_"):
            produtoID = inter.component.custom_id.replace("ColocarVenda_", "")
            select = disnake.ui.ChannelSelect(
                placeholder="Selecione o canal onde o produto será enviado",
                custom_id=f"EnviarProduto_{produtoID}",
                channel_types=[ChannelType.text]
            )
            await inter.response.send_message(components=select, ephemeral=True)

        elif inter.component.custom_id.startswith("SincronizarProduto_"):
            await inter.response.send_message(f"{carregarAnimado} Sincronizando mensagens", ephemeral=True)
            produtoID = inter.component.custom_id.replace("SincronizarProduto_", "")
            await SincronizarMensagens(inter, produtoID)
            await inter.edit_original_message(f"{positivo} Mensagens sincronizadas com sucesso")

        elif inter.component.custom_id.startswith("AtivarDesativarEntregaAuto_"):
            produtoID = inter.component.custom_id.replace("AtivarDesativarEntregaAuto_", "")
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            db = ObterDatabase()
            produto = ObterProduto(produtoID)
            if not produto: return await inter.edit_original_message(f"{negativo} Produto não encontrado")

            db[produtoID]["entrega"] = True if produto["entrega"] == False else False

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            embed, components = Produto.ObterPainelGerenciarProduto(inter, produtoID)
            await inter.edit_original_message("", embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def VendasDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "SelecionarProdutoDropdownVendas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            produto = ObterProduto(inter.values[0])
            if produto:
                embed, components = Produto.ObterPainelGerenciarProduto(inter, inter.values[0])
                await inter.edit_original_message("", embed=embed, components=components)
            else: await inter.edit_original_message(f"{negativo} O produto não foi encontrado. Tente novamente.")

        elif inter.component.custom_id == "SelecionarCampoDropdownVendas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            produtoID, campoID = inter.values[0].split("_")
            embed, components = Campo.ObterPainelGerenciarCampo(inter, produtoID, campoID)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id == "SelecionarCupomDropdownVendas":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            produtoID, cupomID = inter.values[0].split("_")
            embed, components = Cupom.ObterPainel(inter, produtoID, cupomID)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("EnviarProduto_"):
            channel = inter.values[0]
            produtoID = inter.component.custom_id.replace("EnviarProduto_", "")
            channel = inter.guild.get_channel(int(channel))
            embed, components = GerarPainelProduto(inter, produtoID)
            msg = await channel.send(embed=embed, components=components)

            db = ObterDatabase()
            produto = db[produtoID]

            ids = {
                f"{msg.channel.id}": f"{msg.id}"
            }
            produto["ids"].append(ids)

            with open("Database/Vendas/produtos.json", "w") as f:
                json.dump(db, f, indent=4)
            
            await inter.response.edit_message(f"{positivo} Mensagem enviada com sucesso em: {msg.jump_url}", components=None)

        elif inter.component.custom_id.startswith("GerenciarCargos_"):
            _, type, produtoID, campoID = inter.component.custom_id.split("_")
            
            if type == "Adicionar":
                if inter.values:
                    cargosAdd = [int(role_id) for role_id in inter.values]
                else: cargosAdd = []
                Campo.Cargos.atualizarDB(produtoID, campoID, cargosAdd=cargosAdd)
            elif type == "Remover":
                if inter.values:
                    cargosRem = [int(role_id) for role_id in inter.values]
                else: cargosRem = []
                Campo.Cargos.atualizarDB(produtoID, campoID, cargosRem=cargosRem)

            embed, components = Campo.ObterPainelGerenciarCampo(inter, produtoID, campoID)
            await inter.response.edit_message("", embed=embed, components=components)

def setup(bot: commands.Bot):
    bot.add_cog(VendasCommand(bot))