import disnake
from disnake.ext import commands
from datetime import *
from disnake import *

import json
from Functions.CarregarEmojis import *

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

def GerarMensagemTicket(inter: disnake.MessageInteraction, ticketID: str):
    ticket = ObterTicket(ticketID)
    
    if not ticket:
        raise ValueError(f"O ticket com ID {ticketID} não foi encontrado.")

    nome = ticket.get("nome", "Sem Nome")
    descricao = ticket.get("description", None)
    embed_data = ticket.get("embed", {})
    categorias = ticket.get("categorias", {})

    if not isinstance(embed_data, dict):
        embed_data = {}
    if not isinstance(categorias, dict):
        categorias = {}

    hex_color = embed_data.get("hex", "#FFFFFF")
    banner = embed_data.get("banner", None)
    icon = embed_data.get("icon", None)

    try:
        if hex_color:
            cor = int(hex_color.lstrip("#"), 16)
        else: cor = 0xFFFFFF
    except:
        cor = 0xFFFFFF

    embed = disnake.Embed(
        title=nome,
        description=descricao if descricao else None,
        color=disnake.Color(cor),
        timestamp=datetime.now()
    )

    if inter.guild:
        embed.set_footer(
            text=inter.guild.name,
            icon_url=inter.guild.icon.url if inter.guild.icon else None
        )

    if banner:
        embed.set_image(url=banner)
    if icon:
        embed.set_thumbnail(url=icon)

    if len(categorias) == 1:
        for categoriaID, categoria in categorias.items():
            if isinstance(categoria, dict):
                dropdown = [
                    disnake.ui.Button(
                        label=categoria["nome"],
                        emoji=categoria["emoji"],  
                        custom_id=f"AbrirTicketCategoria_{ticketID}_{categoriaID}"
                    )
                ]
    else:
        options = []
        for categoriaID, categoria in categorias.items():
            if isinstance(categoria, dict):
                options.append(
                    disnake.SelectOption(
                        label=categoria.get("nome", "Sem Nome"),
                        value=categoriaID,
                        description=categoria.get("pre_descricao", None),
                        emoji=categoria.get("emoji", None)
                    )
                )

        if not options:
            options = [
                disnake.SelectOption(
                    label="Nenhuma categoria disponível",
                    emoji="❌",
                    value="none"
                )
            ]

        dropdown = disnake.ui.StringSelect(
            placeholder="Selecione uma categoria para abrir",
            custom_id=f"AbrirCategoriaDropdown_{ticketID}",
            options=options,
            disabled=len(categorias) == 0
        )

    return embed, [dropdown]

async def SincronizarTicket(inter: disnake.MessageInteraction, ticketID: str):
    try:
        with open("config.json") as f:
            config = json.load(f)
            server = config["server"]
        
        server = int(server)
        server = inter.bot.get_guild(server)
        
        if not server:
            return await inter.edit_original_message("Servidor não encontrado.")
        
        db = ObterDatabase()
        
        if not db[ticketID]:
            return await inter.edit_original_message("Ticket não encontrado.")

        ticket = ObterTicket(ticketID)
        embed, components = GerarMensagemTicket(inter, ticketID)

        novos_ids = []
        for ids in ticket.get("ids", []):
            channelID, messageID = ids.split("_")
            try:
                channel = inter.bot.get_channel(int(channelID))
            except Exception as e:
                continue
            
            if channel:
                try:
                    oldmsg = await channel.fetch_message(int(messageID))
                    if oldmsg:
                        await oldmsg.delete()
                except Exception as e:
                    continue

                newmsg = await channel.send(embed=embed, components=components)
                novos_ids.append(f"{newmsg.channel.id}_{newmsg.id}")
        
        db[ticketID]["ids"] = novos_ids
        with open("Database/Tickets/ticket.json", "w") as f:
            json.dump(db, f, indent=4)
        
        await inter.edit_original_message(f"{positivo} Mensagens sincronizadas para todos os canais.")
        
    except Exception as e:
        return await inter.edit_original_message(f"{negativo} Ocorreu um erro ao sincronizar os canais: {str(e)}")