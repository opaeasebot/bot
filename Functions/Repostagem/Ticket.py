import disnake
from disnake import *
from datetime import datetime

from Functions.CarregarEmojis import *
from Functions.Database import Database

class Ticket:
    @staticmethod
    def ObterTicket(ticketID: str):
        db = Database.Obter("Database/Tickets/ticket.json")
        return db.get(ticketID)

    @staticmethod
    def ObterCategoria(ticketID: str, categoriaID: str):
        ticket = Ticket.ObterTicket(ticketID)
        return ticket["categorias"].get(categoriaID) if ticket else None

    @staticmethod
    def GerarMensagemTicket(inter: MessageInteraction, ticketID: str):
        ticket = Ticket.ObterTicket(ticketID)
        if not ticket: return

        nome = ticket.get("nome", "Sem Nome")
        descricao = ticket.get("description")
        embed_data = ticket.get("embed", {})
        categorias = ticket.get("categorias", {})

        hex_color = embed_data.get("hex", "#FFFFFF")
        banner = embed_data.get("banner")
        icon = embed_data.get("icon")

        try: cor = int(hex_color.lstrip("#"), 16)
        except: cor = 0xFFFFFF

        embed = Embed(
            title=nome,
            description=descricao,
            color=Color(cor),
            timestamp=datetime.now()
        )

        if inter.guild: embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon.url if inter.guild.icon else None)
        if banner: embed.set_image(url=banner)
        if icon: embed.set_thumbnail(url=icon)

        if len(categorias) == 1:
            for categoriaID, categoria in categorias.items():
                if isinstance(categoria, dict):
                    dropdown = [
                        ui.Button(
                            label=categoria["nome"],
                            emoji=categoria["emoji"],
                            custom_id=f"AbrirTicketCategoria_{ticketID}_{categoriaID}"
                        )
                    ]
        else:
            options = [
                SelectOption(
                    label=cat.get("nome", "Sem Nome"),
                    value=cat_id,
                    description=cat.get("pre_descricao"),
                    emoji=cat.get("emoji")
                )
                for cat_id, cat in categorias.items() if isinstance(cat, dict)
            ]

            if not options: options = [SelectOption(label="Nenhuma categoria disponível", emoji="❌", value="none")]

            dropdown = ui.StringSelect(
                placeholder="Selecione uma categoria para abrir",
                custom_id=f"AbrirCategoriaDropdown_{ticketID}",
                options=options,
                disabled=len(categorias) == 0
            )

        return embed, [dropdown]

    @staticmethod
    async def SincronizarTicket(inter: MessageInteraction, ticketID: str):
        try:
            config = Database.Obter("config.json")
            guild = inter.bot.get_guild(int(config["server"]))
            if not guild:
                return await inter.edit_original_message("Servidor não encontrado.")

            db = Database.Obter("Database/Tickets/ticket.json")
            if ticketID not in db:
                return await inter.edit_original_message("Ticket não encontrado.")

            ticket = db[ticketID]
            embed, components = Ticket.GerarMensagemTicket(inter, ticketID)

            novos_ids = []

            for ids in ticket.get("ids", []):
                channelID, messageID = ids.split("_")
                channel = inter.bot.get_channel(int(channelID))
                if not channel:
                    continue

                try:
                    oldmsg = await channel.fetch_message(int(messageID))
                    await oldmsg.delete()
                except:
                    pass

                newmsg = await channel.send(embed=embed, components=components)
                novos_ids.append(f"{newmsg.channel.id}_{newmsg.id}")

            db[ticketID]["ids"] = novos_ids
            Database.Salvar("Database/Tickets/ticket.json", db)

            await inter.edit_original_message(f"{positivo} Mensagens sincronizadas para todos os canais.")
        except Exception as e:
            await inter.edit_original_message(f"{negativo} Ocorreu um erro ao sincronizar os canais: {str(e)}")