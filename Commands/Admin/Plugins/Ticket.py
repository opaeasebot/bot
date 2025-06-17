import disnake
import json
import re
from disnake.ext import commands
from disnake import *
from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Functions.Config.Repostagem.Ticket import *
from datetime import datetime
import random
import string

def ObterDatabase():
    with open("Database/Tickets/ticket.json") as f:
        db = json.load(f)
        return db

def ObterTicket(ticketID: str):
    db = ObterDatabase()
    try:
        return db[ticketID]
    except:
        return None

def ObterCategoria(ticketID: str, categoriaID: str):
    ticket = ObterTicket(ticketID)
    if not ticket: return None

    try:
        return ticket["categorias"][categoriaID]
    except: return None

def ObterTicketAberto(ticketID: str):
    with open("Database/Tickets/ticketsAbertos.json") as f:
        ticket = json.load(f)
    
    try:
        if ticket[ticketID]:
            return ticket[ticketID]
        else:
            return None
    except: return None

def GerarString():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=13))

def ObterPainelTicket(inter: disnake.MessageInteraction):
    db = ObterDatabase()
    
    embed = disnake.Embed(
        title="Gerenciar painel de Tickets",
        description="Utilize este painel para gerenciar o sistema de Ticket no seu servidor.",
        timestamp=datetime.now(),
        color=0x00FFFF
    )
    embed.set_footer(text=f"{inter.guild.name}", icon_url=inter.guild.icon)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1327815504865398854/1333664443258900583/a_d78e7542df8823e9c10eac06609d7473.gif?ex=67c9d60d&is=67c8848d&hm=4f2b22202b41d1729908a6ecf80d26068798cd5c8eaa4ad0d06c71dbf4905504&")
    embed.add_field(
        name="Tickets fornecidos",
        value=f"{ticket} `{len(db)} ticket(s)`"
    )

    options = []
    for ticketID, ticketData in db.items():
        options.append(
            disnake.SelectOption(
                value=ticketID,
                label=f"{ticketData["nome"]}",
                description=f"Categorias: {len(ticketData['categorias'])}",
                emoji=config2
            )
        )
    
    if not options:
        options = [disnake.SelectOption(label="Nenhum ticket disponível")]

    components = [
        disnake.ui.StringSelect(
            custom_id="GerenciarTicket",
            placeholder="Selecione um Ticket para gerenciar",
            options=options,
            disabled=False if any(ticketData["nome"] for ticketData in db.values()) else True
        ),
        disnake.ui.Button(label="Criar Ticket", emoji=mais2, custom_id="CriarTicket", style=disnake.ButtonStyle.green),
        disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial")
    ]

    return embed, components

class Ticket():
    class CriarTicket(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="Título",
                    custom_id="name",
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Descrição",
                    custom_id="description",
                    required=False,
                    style=TextInputStyle.paragraph,
                ),
                disnake.ui.TextInput(
                    label="Banner",
                    custom_id="banner",
                    placeholder="Coloque o URL do banner",
                    required=False,
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Ícone",
                    custom_id="icon",
                    placeholder="Coloque o URL do ícone",
                    required=False,
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Hex",
                    custom_id="hex",
                    placeholder="#FFFFFF",
                    min_length=7,
                    max_length=7,
                    required=False,
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Criar Ticket", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            name = inter.text_values["name"]
            desc = inter.text_values["description"] or None
            banner = inter.text_values["banner"] or None
            icon = inter.text_values["icon"] or None
            hex = inter.text_values["hex"] or None

            def verificar_hex(cor: str) -> str | None:
                """Valida e formata um código hexadecimal para o formato 0xHEX."""
                if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", cor):
                    return None
                return "#" + cor[1:].upper()

            if hex:
                hex_formatado = verificar_hex(hex)
                if not hex_formatado:
                    await inter.response.send_message(
                        f"{negativo} O código hexadecimal fornecido é inválido. Use um formato como `#RRGGBB` ou `#RGB`.",
                        ephemeral=True
                    )
                    return
                hex = hex_formatado

            db = ObterDatabase()

            if len(db) >= 25:
                embed, components = ObterPainelTicket(inter)
                await inter.response.send_message(f"{negativo} Você não pode ter mais que 25 tickets.", ephemeral=True)
                return

            ticket_id = GerarString()
            db[ticket_id] = {
                "nome": name,
                "description": desc,
                "categorias": {},
                "embed": {
                    "hex": hex,
                    "banner": banner,
                    "icon": icon,
                },
                "ids": []
            }

            with open("Database/Tickets/ticket.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = await Ticket.ObterPainel(inter, ticket_id)
            await inter.response.edit_message("", embed=embed, components=components)

    class EditarTicket(disnake.ui.Modal):
        def __init__(self, ticket_id: str):
            self.ticket_id = ticket_id

            db = ObterDatabase()
            ticket = db.get(ticket_id, {})

            nome = ticket.get("nome", "Sem título")
            descricao = ticket.get("description", "")
            banner = ticket.get("embed", {}).get("banner", "")
            icon = ticket.get("embed", {}).get("icon", "")
            hex = ticket.get("embed", {}).get("hex", "#FFFFFF")

            components = [
                disnake.ui.TextInput(
                    label="Título",
                    custom_id="name",
                    value=nome,
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Descrição",
                    custom_id="description",
                    value=descricao,
                    required=False,
                    style=TextInputStyle.paragraph,
                ),
                disnake.ui.TextInput(
                    label="Banner",
                    custom_id="banner",
                    placeholder="Coloque o URL do banner",
                    value=banner,
                    required=False,
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Ícone",
                    custom_id="icon",
                    placeholder="Coloque o URL do ícone",
                    value=icon,
                    required=False,
                    style=TextInputStyle.long,
                ),
                disnake.ui.TextInput(
                    label="Hex",
                    custom_id="hex",
                    placeholder="#FFFFFF",
                    value=hex,
                    min_length=7,
                    max_length=7,
                    required=False,
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Editar Ticket", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            name = inter.text_values["name"]
            desc = inter.text_values["description"] or None
            banner = inter.text_values["banner"] or None
            icon = inter.text_values["icon"] or None
            hex = inter.text_values["hex"] or None

            def verificar_hex(cor: str) -> str | None:
                """Valida e formata um código hexadecimal para o formato 0xHEX."""
                if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", cor):
                    return None
                return "#" + cor[1:].upper()

            if hex:
                hex_formatado = verificar_hex(hex)
                if not hex_formatado:
                    await inter.response.send_message(
                        f"{negativo} O código hexadecimal fornecido é inválido. Use um formato como `#RRGGBB` ou `#RGB`.",
                        ephemeral=True
                    )
                    return
                hex = hex_formatado

            db = ObterDatabase()

            if self.ticket_id not in db:
                await inter.response.send_message(f"{negativo} O ticket não foi encontrado!", ephemeral=True)
                return

            db[self.ticket_id]["nome"] = name
            db[self.ticket_id]["description"] = desc
            db[self.ticket_id]["embed"]["hex"] = hex
            db[self.ticket_id]["embed"]["banner"] = banner
            db[self.ticket_id]["embed"]["icon"] = icon

            with open("Database/Tickets/ticket.json", "w") as f:
                json.dump(db, f, indent=4)

            embed, components = await Ticket.ObterPainel(inter, self.ticket_id)
            await inter.response.edit_message(embed=embed, components=components)

    @staticmethod
    async def ObterPainel(inter: disnake.MessageInteraction, ticketID: str):
        db = ObterDatabase()
        ticket = ObterTicket(ticketID)

        with open("Database/Server/cargos.json") as f:
            cargos = json.load(f)
            cargo_suporte = cargos["suporte"]

            if not cargo_suporte:
                cargo_suporte = f"{negativo} `Não definido`"
            else:
                cargo_suporte = f"<@&{cargo_suporte}>"

        if not ticket:
            return await inter.edit_original_message(f"{negativo} Ticket não encontrado")

        if not ticket["description"]:
            descricao = f"{negativo} `Não definida`"
        else: descricao = f"{ticket["description"]}"

        embed = disnake.Embed(
            title="Gerenciar Ticket",
            description=f"""
{mensagem} **Descrição:**
{descricao}
            """,
            color=disnake.Color(0x00FFFF),
            timestamp=datetime.now()
        )
        embed.set_author(
            name=f"Nome: {ticket["nome"]}"
        )

        embed.add_field(
            name=f"{embedE} Informações",
            value=f"""
-# Ícone: {ticket["embed"]["icon"] if ticket["embed"]["icon"] is not None else f"{negativo} `Não definido`"}
-# Banner: {ticket["embed"]["banner"] if ticket["embed"]["banner"] is not None else f"{negativo} `Não definido`"}
-# Hex: {ticket["embed"]["hex"] if ticket["embed"]["hex"] is not None else f"{negativo} `Não definido`"}
            """,
            inline=True
        )
        embed.add_field(
            name=f"{diretorio} Categorias",
            value=f"`{len(ticket["categorias"])} categoria(s)`",
            inline=True
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        components = [
            [
                disnake.ui.Button(
                    label="Editar",
                    emoji=editar,
                    custom_id=f"EditarTicket_{ticketID}",
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label="Categorias",
                    emoji=diretorio,
                    custom_id=f"GerenciarCategoriasTicket_{ticketID}",
                    style=disnake.ButtonStyle.green
                ),
                disnake.ui.Button(
                    label="Apagar",
                    custom_id=f"ApagarTicket_{ticketID}",
                    emoji=apagar,
                    style=disnake.ButtonStyle.red
                ),
            ],
            [
                disnake.ui.Button(
                    label="Enviar",
                    custom_id=f"EnviarTicket_{ticketID}",
                    emoji=arrow,
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label="Sincronizar",
                    custom_id=f"SincronizarTicket_{ticketID}",
                    emoji=reload
                ),
                disnake.ui.Button(
                    label="Voltar",
                    emoji=voltar,
                    custom_id="GerenciarPainelTicket"
                )
            ]
        ]

        return embed, components

    @staticmethod
    async def ApagarTicket(ticketID: str):
        db = ObterDatabase()

        if ticketID in db:
            del db[ticketID]

            with open("Database/Tickets/ticket.json", "w") as f:
                json.dump(db, f, indent=4)

    @staticmethod
    async def EnviarMensagem(inter: disnake.MessageInteraction, ticketID: str):
        await inter.response.edit_message(f"{carregarAnimado} Estamos enviando sua mensagem. Aguarde um momento.", components=None)
        channelID = inter.values[0]
        channel = inter.guild.get_channel(int(channelID))
        try:
            embed, components = GerarMensagemTicket(inter, ticketID)
            msg = await channel.send(embed=embed, components=components)
        except Exception as e:
            return await inter.edit_original_message(f"{negativo} Não foi possível enviar a mensagem para o canal. Tente novamente!")

        db = ObterDatabase()
        db[ticketID]["ids"].append(f"{channelID}_{msg.id}")

        with open("Database/Tickets/ticket.json", "w") as f:
            json.dump(db, f, indent=4)
        
        await inter.edit_original_message(f"{positivo} Mensagem enviada para o canal: {channel.jump_url} | {msg.jump_url}")


    class Categorias():
        class CriarCategoria(disnake.ui.Modal):
            def __init__(self, ticket_id: str):
                self.ticket_id = ticket_id

                components = [
                    disnake.ui.TextInput(
                        label="Nome",
                        placeholder="Suporte",
                        custom_id="name",
                        style=TextInputStyle.short,
                        max_length=50,
                    ),
                    disnake.ui.TextInput(
                        label="Descrição",
                        custom_id="description",
                        placeholder="Irá aparecer quando o usuário abrir o Ticket",
                        required=False,
                        max_length=1024,
                        style=TextInputStyle.paragraph,
                    ),
                    disnake.ui.TextInput(
                        label="Pré Descrição",
                        custom_id="pre-description",
                        max_length=100,
                        placeholder="Irá aparecer no dropdown do Ticket",
                        style=TextInputStyle.paragraph,
                        required=False
                    ),
                    disnake.ui.TextInput(
                        label="Emoji",
                        placeholder="Emoji da categoria no dropdown",
                        custom_id="emoji",
                        required=False,
                        style=TextInputStyle.short,
                    ),
                ]
                super().__init__(title="Criar Categoria", components=components)

            async def callback(self, inter: disnake.ModalInteraction):
                db = ObterDatabase()

                nome = inter.text_values["name"]
                descricao = inter.text_values["description"]
                pre_descricao = inter.text_values["pre-description"]
                emoji = inter.text_values["emoji"]

                categoriaID = GerarString()
                db[self.ticket_id]["categorias"][categoriaID] = {
                    "nome": nome,
                    "descricao": descricao if descricao != "" else None,
                    "pre_descricao": pre_descricao if pre_descricao != "" else None,
                    "emoji": emoji if emoji != "" else None
                }

                with open("Database/Tickets/ticket.json", "w") as f:
                    json.dump(db, f, indent=4)
                
                embed, components = await Ticket.Categorias.ObterPainelCategoria(self.ticket_id, categoriaID)
                await inter.response.edit_message("", embed=embed, components=components)

        class EditarCategoria(disnake.ui.Modal):
            def __init__(self, ticket_id: str, categoria_id: str):
                self.ticket_id = ticket_id
                self.categoria_id = categoria_id

                db = ObterDatabase()
                categoria = db.get(ticket_id, {}).get("categorias", {}).get(categoria_id, {})

                components = [
                    disnake.ui.TextInput(
                        label="Nome",
                        placeholder="Suporte",
                        custom_id="name",
                        style=TextInputStyle.short,
                        max_length=50,
                        value=categoria.get("nome", "")
                    ),
                    disnake.ui.TextInput(
                        label="Descrição",
                        custom_id="description",
                        placeholder="Irá aparecer quando o usuário abrir o Ticket",
                        required=False,
                        max_length=1024,
                        style=TextInputStyle.paragraph,
                        value=categoria.get("descricao", "") or ""
                    ),
                    disnake.ui.TextInput(
                        label="Pré Descrição",
                        custom_id="pre-description",
                        max_length=100,
                        placeholder="Irá aparecer no dropdown do Ticket",
                        style=TextInputStyle.paragraph,
                        required=False,
                        value=categoria.get("pre_descricao", "") or ""
                    ),
                    disnake.ui.TextInput(
                        label="Emoji",
                        placeholder="Emoji da categoria no dropdown",
                        custom_id="emoji",
                        required=False,
                        style=TextInputStyle.short,
                        value=categoria.get("emoji", "") or ""
                    ),
                ]
                
                super().__init__(title="Editar Categoria", components=components)

            async def callback(self, inter: disnake.ModalInteraction):
                db = ObterDatabase()

                nome = inter.text_values.get("name", "")
                descricao = inter.text_values.get("description", "")
                pre_descricao = inter.text_values.get("pre-description", "")
                emoji = inter.text_values.get("emoji", "")

                db[self.ticket_id]["categorias"][self.categoria_id] = {
                    "nome": nome,
                    "descricao": descricao if descricao else None,
                    "pre_descricao": pre_descricao if pre_descricao else None,
                    "emoji": emoji if emoji else None
                }

                with open("Database/Tickets/ticket.json", "w") as f:
                    json.dump(db, f, indent=4)
                
                embed, components = await Ticket.Categorias.ObterPainelCategoria(self.ticket_id, self.categoria_id)
                await inter.response.edit_message("", embed=embed, components=components)

        @staticmethod
        async def ObterPainelGerenciarCategorias(ticketID: str):
            db = ObterDatabase()
            ticket = ObterTicket(ticketID)

            options = []

            for categoriaID, categoriaData in ticket.get("categorias", {}).items():
                nome = categoriaData.get("nome", "Sem Nome")
                preDesc = categoriaData.get("pre_descricao")
                emoji = categoriaData.get("emoji")

                if not emoji:
                    emoji = diretorio

                if not preDesc:
                    preDesc = "Sem descrição"

                options.append(
                    disnake.SelectOption(
                        label=nome,
                        value=categoriaID,
                        description=preDesc,
                        emoji=emoji
                    )
                )

            if len(options) == 0:
                options.append(disnake.SelectOption(label="vai corinthians"))

            components = [
                disnake.ui.StringSelect(
                    placeholder="Selecione uma categoria para gerenciar",
                    custom_id=f"GerenciarCategoriasTicket_{ticketID}",
                    options=options,
                    disabled=False if len(ticket["categorias"]) > 0 else True
                ),
                disnake.ui.Button(
                    label="Criar Categoria",
                    emoji=mais2,
                    custom_id=f"CriarCategoria_{ticketID}",
                    style=disnake.ButtonStyle.green
                ),
                disnake.ui.Button(
                    label="Voltar",
                    emoji=voltar,
                    custom_id=f"GerenciarTicket_{ticketID}"
                )
            ]

            return components
            
        @staticmethod
        async def ObterPainelCategoria(ticketID: str, categoriaID: str):
            categoria = ObterCategoria(ticketID, categoriaID)
            ticket = ObterTicket(ticketID)
            if not categoria: return None, None

            if categoria["pre_descricao"]: predesc = categoria["pre_descricao"]
            else: predesc = f"{negativo} `Não definido`"

            if categoria["descricao"]: descricao = categoria["descricao"]
            else: descricao = f"{negativo} `Não definido`"

            if categoria["emoji"]: emoji = categoria["emoji"]
            else: emoji = f"{negativo} `Não definido`"

            embed = disnake.Embed(
                title="Gerenciar Categoria",
                description=f"""
**{mensagem} Pré-descrição:**
{predesc}

**{mensagem} Descrição:**
{descricao}
                """,
                color=disnake.Color(0x00FFFF),
                timestamp=datetime.now()
            )
            embed.set_author(name=f"Nome: {ticket["nome"]} | Categoria: {categoria["nome"]}")
            embed.add_field(
                name=f"{config2} Informações:",
                value=f"""
-# Pré-descrição: aparece na Dropdown da mensagem do Ticket
-# Descrição: aparece no canal quando a categoria é criada
                """,
                inline=False
            )
            embed.add_field(
                name=f"{embedE} Informações da categoria",
                value=f"""
`{ticket["nome"]}`
`{categoria["nome"]}`
""",
                inline=True
            )
            embed.add_field(
                name=f"{embedE} Emoji",
                value=f"{emoji}",
                inline=True
            )

            components = [
                disnake.ui.Button(
                    label="Editar",
                    emoji=editar,
                    custom_id=f"EditarCategoria_{ticketID}_{categoriaID}",
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label="Apagar",
                    custom_id=f"ApagarCategoria_{ticketID}_{categoriaID}",
                    emoji=apagar,
                    style=disnake.ButtonStyle.red
                ),
                disnake.ui.Button(
                    label="Voltar",
                    custom_id=f"GerenciarCategoriasTicket_{ticketID}",
                    emoji=voltar
                )
            ]

            return embed, components

        @staticmethod
        async def ApagarCategoria(ticketID: str, categoriaID: str):
            db = ObterDatabase()
            if categoriaID in db[ticketID]["categorias"]:
                del db[ticketID]["categorias"][categoriaID]

                with open("Database/Tickets/ticket.json", "w") as f:
                    json.dump(db, f, indent=4)

class Abertura():
    def VerificarTicketAberto(userID: int):
        with open("Database/Tickets/ticketsAbertos.json") as f:
            ticketsAbertos = json.load(f)
        
        for ticketID, ticketData in ticketsAbertos.items():
            if ticketData["server"]["userID"] == userID:
                return True
        
        return False

    @staticmethod
    async def AbrirTicket(inter: disnake.MessageInteraction, ticketID: str, categoriaID: str):
        await inter.response.send_message(f"{carregarAnimado} Abrindo seu ticket", ephemeral=True)
        ticket = ObterTicket(ticketID)
        categoria = ObterCategoria(ticketID, categoriaID)
        if not categoria:
            await inter.edit_original_message(f"{negativo} O ticket/categoria não foram encontrados")
            return

        if Abertura.VerificarTicketAberto(int(inter.user.id)) == True:
            await inter.edit_original_message(f"{negativo} Você já possui um ticket aberto.")
            return

        ticketIDAberto = GerarString()
        topic = await inter.channel.create_thread(
            name=f"{categoria["nome"]}・{inter.user.name}・{inter.user.id}",
            type=disnake.ChannelType.private_thread,
            invitable=False
        )

        def GerarContent():
            with open("Database/Server/cargos.json") as f:
                cargos = json.load(f)
            if cargos["suporte"]:
                return cargos["suporte"]
            else:
                return ""

        def GerarEmbed():
            hex_color = ticket["embed"]["hex"]

            try:
                if hex_color:
                    cor = int(hex_color.lstrip("#"), 16)
                else: cor = 0xFFFFFF
            except:
                cor = 0xFFFFFF

            embed = disnake.Embed(
                title=f"{categoria["nome"]}",
                description=categoria["descricao"],
                timestamp=datetime.now(),
                color=disnake.Color(cor)
            )
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
            embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.avatar)

            components = [
                disnake.ui.Button(
                    label="Lembrar",
                    custom_id=f"LembrarUsuario_{ticketIDAberto}",
                    emoji=clock,
                    style=disnake.ButtonStyle.blurple
                ),
                disnake.ui.Button(
                    label="Apagar",
                    custom_id=f"ApagarTicketAberto_{ticketIDAberto}",
                    emoji=apagar,
                    style=disnake.ButtonStyle.red
                )
            ]

            return embed, components

        def GerarEmbedLogs():
            embed = disnake.Embed(
                title="Ticket Aberto",
                description=f"O usuário {inter.user.mention} abriu um ticket. Veja as informações abaixo.",
                timestamp=datetime.now(),
                color=disnake.Color(0xf79b11)
            )
            embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)
            embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.avatar)
            embed.add_field(
                name="Informações da categoria",
                value=f"""
    `{ticket["nome"]}`
    `{categoria["nome"]}`
                """,
                inline=True
            )
            embed.add_field(
                name="Criador",
                value=f"{inter.user.mention}\n`{inter.user.id}`",
                inline=True
            )
            embed.add_field(
                name="Canal aberto",
                value=f"{topic.mention}"
            )

            components = [
                disnake.ui.Button(
                    label="Acessar",
                    url=topic.jump_url
                )
            ]

            return embed, components

        suporte = GerarContent()
        try:
            suporte = inter.guild.get_role(int(suporte))
            if suporte: suporteCargo = suporte.mention
            else: suporteCargo = ""
        except: suporteCargo = "" 
        
        content = f"{inter.user.mention} {suporteCargo}"
        embed, components = GerarEmbed()
        await topic.send(content=content, embed=embed, components=components)

        await inter.edit_original_message(f"{positivo} Seu Ticket foi aberto em {topic.mention}",
        components=[
            disnake.ui.Button(
                label="Acessar",
                url=topic.jump_url
            )
        ])

        embed, components = GerarEmbedLogs()
        with open("Database/Server/canais.json") as f:
            canais = json.load(f)
        
        if not canais["tickets"]:
            pass
        else:
            try:
                channel = inter.guild.get_channel(int(canais["tickets"]))
                if not channel: pass
                await channel.send(embed=embed, components=components)
            except:
                pass

        with open("Database/Tickets/ticketsAbertos.json") as f:
            ticketsAbertos = json.load(f)

        ticketsAbertos[ticketIDAberto] = {
            "ticketID": ticketID,
            "categoriaID": categoriaID,
            "server": {
                "userID": inter.user.id,
                "topicID": topic.id
            },
        }

        with open("Database/Tickets/ticketsAbertos.json", "w") as f:
            json.dump(ticketsAbertos, f, indent=4)

class TicketCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def TicketButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelTicket":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = ObterPainelTicket(inter)
            await inter.edit_original_message("", embed=embed, components=components)
        
        elif inter.component.custom_id == "CriarTicket":
            await inter.response.send_modal(Ticket.CriarTicket())

        elif inter.component.custom_id.startswith("GerenciarTicket_"):
            ticketID = inter.component.custom_id.replace("GerenciarTicket_", "")
            ticket = ObterTicket(ticketID)
            if not ticket: return await inter.response.send_message(f"{negativo} Ticket não encontrado")
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = await Ticket.ObterPainel(inter, ticketID)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("EditarTicket_"):
            ticketID = inter.component.custom_id.replace("EditarTicket_", "")
            ticket = ObterTicket(ticketID)
            if not ticket:
                return await inter.response.send_message(f"{negativo} Ticket não encontrado.")
            await inter.response.send_modal(Ticket.EditarTicket(ticketID))
        
        elif inter.component.custom_id.startswith("ApagarTicket_"):
            ticketID = inter.component.custom_id.replace("ApagarTicket_", "")
            await Ticket.ApagarTicket(ticketID)
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = ObterPainelTicket(inter)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("GerenciarCategoriasTicket_"):
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            ticketID = inter.component.custom_id.replace("GerenciarCategoriasTicket_", "")
            components = await Ticket.Categorias.ObterPainelGerenciarCategorias(ticketID)
            await inter.edit_original_message(f"{inter.user.mention} Selecione uma categoria para gerenciar.", embed=None, components=components)

        elif inter.component.custom_id.startswith("CriarCategoria_"):
            ticketID = inter.component.custom_id.replace("CriarCategoria_", "")
            await inter.response.send_modal(Ticket.Categorias.CriarCategoria(ticketID))

        elif inter.component.custom_id.startswith("EditarCategoria_"):
            _, ticketID, categoriaID = inter.component.custom_id.split("_")
            await inter.response.send_modal(Ticket.Categorias.EditarCategoria(ticketID, categoriaID))

        elif inter.component.custom_id.startswith("ApagarCategoria_"):
            _, ticketID, categoriaID = inter.component.custom_id.split("_")
            await Ticket.Categorias.ApagarCategoria(ticketID, categoriaID)
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            components = await Ticket.Categorias.ObterPainelGerenciarCategorias(ticketID)
            await inter.edit_original_message(f"{inter.user.mention} Selecione uma categoria para gerenciar.", embed=None, components=components)

        elif inter.component.custom_id.startswith("EnviarTicket_"):
            ticketID = inter.component.custom_id.replace("EnviarTicket_", "")
            dropdown = disnake.ui.ChannelSelect(
                custom_id=f"SelecionarCanalTicket_{ticketID}",
                channel_types=[ChannelType.text],
                placeholder="Selecione um canal para enviar a mensagem"
            )
            await inter.response.send_message(components=dropdown, ephemeral=True)

        elif inter.component.custom_id.startswith("SincronizarTicket_"):
            ticketID = inter.component.custom_id.replace("SincronizarTicket_", "")
            await inter.response.send_message(f"{carregarAnimado} Sincronizando mensagens...", ephemeral=True)
            await SincronizarTicket(inter, ticketID)

        elif inter.component.custom_id.startswith("AbrirTicketCategoria_"):
            _, ticketID, categoriaID = inter.component.custom_id.split("_")
            await Abertura.AbrirTicket(inter, ticketID, categoriaID)

        elif inter.component.custom_id.startswith("LembrarUsuario_"):
            ticketID = inter.component.custom_id.replace("LembrarUsuario_", "")
            ticket = ObterTicketAberto(ticketID)

            def VerificarPermissão():
                with open("Database/Server/cargos.json") as f:
                    cargos = json.load(f)

                suporte_cargo_id = cargos.get("suporte", None)
                
                if suporte_cargo_id is None:
                    return False

                for role in inter.user.roles:
                    if str(role.id) == str(suporte_cargo_id):
                        return True

                return False

            if VerificarPermissão() == False:
                return await inter.response.send_message(f"{negativo} Faltam permissões", ephemeral=True)
            
            await inter.response.send_message(f"{carregarAnimado} Aguarde um momento", ephemeral=True)

            try:
                userID = ticket["server"]["userID"]
                user = inter.guild.get_member(int(userID))
                if user:
                    await user.send(f"{user.mention}, você possui um ticket pendente de resposta; se não for respondido, poderá ser fechado.",
                    components=[
                        disnake.ui.Button(
                            label="Ir para o ticket",
                            url=inter.channel.jump_url
                        )
                    ])
                    await inter.edit_original_message(f"{positivo} Eu lembrei o usuário sobre o ticket")
                else:
                    await inter.edit_original_message(f"{negativo} Não foi possível mandar a mensagem para o usuário")
            except:
                await inter.edit_original_message(f"{negativo} Não foi possível mandar a mensagem para o usuário")

        elif inter.component.custom_id.startswith("ApagarTicketAberto_"):
            ticketID = inter.component.custom_id.replace("ApagarTicketAberto_", "")
            ticket = ObterTicketAberto(ticketID)

            def VerificarPermissão():
                with open("Database/Server/cargos.json") as f:
                    cargos = json.load(f)

                suporte_cargo_id = cargos.get("suporte", None)
                
                if suporte_cargo_id is None:
                    return False

                for role in inter.user.roles:
                    if str(role.id) == str(suporte_cargo_id):
                        return True

                return False

            if VerificarPermissão() == False:
                return await inter.response.send_message(f"{negativo} Faltam permissões", ephemeral=True)
            
            await inter.response.send_message(f"{carregarAnimado} Aguarde um momento", ephemeral=True)
            try:
                user = inter.guild.get_member(int(ticket["server"]["userID"]))
                if not user:
                    userMention = "`Não encontrado`"
                else:
                    userMention = user.mention
            except:
                userMention = "`Não encontrado`"

            def ObterUser():
                embed = disnake.Embed(
                    title="Ticket Fechado",
                    description="Seu ticket foi fechado por um moderador.",
                    timestamp=datetime.now(),
                    color=disnake.Color(0xff0000)
                )
                return embed

            def ObterLogs():
                embed = disnake.Embed(
                    title="Ticket Fechado",
                    description="Um ticket foi fechado por um moderador. Veja as informações abaixo.",
                    timestamp=datetime.now(),
                    color=disnake.Color(0xff0000)
                )
                embed.add_field(
                    name="Usuário",
                    value=f"{userMention}"
                )
                embed.add_field(
                    name="Moderador",
                    value=f"{inter.user.mention}"
                )
                return embed

            try:
                await inter.channel.delete()
            except:
                pass
        
            embed = ObterUser()
            if userMention != "`Não encontrado`":
                await user.send(embed=embed)
            
            with open("Database/Server/canais.json") as f:
                canais = json.load(f)
                logs = canais["tickets"]
            
            try:
                if logs:
                    channel = inter.guild.get_channel(int(logs))
                    embed = ObterLogs()
                    await channel.send(embed=embed)
            except: pass

            try:
                with open("Database/Tickets/ticketsAbertos.json") as f:
                    db = json.load(f)
                    del db[ticketID]
                    
                with open("Database/Tickets/ticketsAbertos.json", "w") as f:
                    json.dump(db, f, indent=4)
            except:
                pass

    @commands.Cog.listener("on_dropdown")
    async def TicketDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarTicket":
            ticketID = inter.values[0]
            ticket = ObterTicket(ticketID)
            if not ticket:
                await inter.response.send_message(f"{negativo} Ticket não encontrado.", ephemeral=True)

            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = await Ticket.ObterPainel(inter, ticketID)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("GerenciarCategoriasTicket_"):
            ticketID = inter.component.custom_id.replace("GerenciarCategoriasTicket_", "")
            categoriaID = inter.values[0]

            embed, components = await Ticket.Categorias.ObterPainelCategoria(ticketID, categoriaID)
            if not embed: return await inter.response.send_message(f"{negativo} Ticket ou categoria não encontrados.")
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id.startswith("SelecionarCanalTicket_"):
            ticketID = inter.component.custom_id.replace("SelecionarCanalTicket_", "")
            await Ticket.EnviarMensagem(inter, ticketID)

        elif inter.component.custom_id.startswith("AbrirCategoriaDropdown_"):
            ticketID = inter.component.custom_id.replace("AbrirCategoriaDropdown_", "")
            categoriaID = inter.values[0]
            await Abertura.AbrirTicket(inter, ticketID, categoriaID)


def setup(bot: commands.Bot):
    bot.add_cog(TicketCommand(bot))