import disnake
import requests
from Functions.CarregarEmojis import *
from datetime import datetime
import asyncio
import json

banner = r"""
     _     __  
    ( \   /  \  developed by guilherme
     ) )_(_/\_) https://mdsmax.dev
    (_/(_)     
"""

def obter_status():
    with open("config.json") as file:
        config = json.load(file)
        name = config["status"]["name"]
        type = config["status"]["type"]

        if type == "online": 
            type = disnake.Status.online
            activity = disnake.Game(
                name=name
            )
        if type == "idle": 
            type = disnake.Status.idle
            activity = disnake.Game(
                name=name
            )
        if type == "dnd": 
            type = disnake.Status.dnd
            activity = disnake.Game(
                name=name
            )
        if type == "streaming": 
            type = disnake.Status.streaming
            activity = disnake.Streaming(
                name=name,
                url="https://twitch.tv/discord"
            )

        return type, activity

def alterar_descricao_bot(bot):
    with open("config.json") as file:
        config = json.load(file)
        token = config['token']

    descricao = (
        "**Tecnologia Ease Solutions**\n"
        "https://mdsmax.dev"
    )

    url = f"https://discord.com/api/v9/applications/{bot.user.id}"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "description": descricao
    }
    response = requests.patch(url, headers=headers, json=payload)
    return response.status_code, response.text

async def startBotlogs(bot):
    try:
        with open("Database/Server/canais.json") as server_file:
            server_db = json.load(server_file)
            logs = server_db["sistema"]
        
        with open("config.json") as file:
            config = json.load(file)
            versao = config['versao']
            owner = config['owner']

        if not logs:
            return

        canal = bot.get_channel(int(logs))
        if not canal:
            return

        embed = disnake.Embed(
            title=f"{reload} — Sistema reiniciado",
            description="""
O bot foi desenvolvido por [Guilherme](https://mdsmax.dev), inspirado no Ease Bot, criado pela equipe da Ease. Este projeto foi elaborado e divulgado com propósitos exclusivamente educacionais, sendo uma adaptação baseada na estrutura do bot original.

A versão original do Ease Bot pode ser acessada através do seguinte link: <https://beta.easebot.app>.

Este projeto foi inicialmente divulgado na comunidade [Blank Vazamentos](https://discord.gg/exemplo). Ressaltamos a importância de manter os devidos créditos ao bot original, reconhecendo o trabalho realizado por seus criadores.""",
            timestamp=datetime.now(),
            color = disnake.Color(0x5865F2)
        )
        embed.add_field(name=f"{config3} Versão", value=f"`{versao}`", inline=True)
        embed.add_field(name=f"{clock} Data", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
        embed.add_field(name=f"{user} Dono", value=f"<@{owner}>", inline=True)
        embed.set_footer(text="© mdsmax.dev")

        embed2 = disnake.Embed(
            title=f"{lupa} — Verificando informações",
            description="A aplicação está realizando uma verificação abrangente de todas as informações para assegurar a presença de todos os componentes essenciais. É importante observar que, durante a inicialização, a aplicação pode apresentar instabilidade temporária, devido à execução simultânea de múltiplos processos.",
            timestamp=datetime.now(),
            color = disnake.Color(0xFFFFFF)
        )

        components = [
            disnake.ui.Button(label="Desenvolvedor", url="https://discord.com/users/358711420612771861"),
            disnake.ui.Button(label="Website", url="https://mdsmax.dev")
        ]
        await canal.send(embeds=[embed, embed2], components=components)

    except Exception as e:
        print(f"Erro ao executar startBotlogs: {e}")

async def mandarLogsServer(inter: disnake.MessageInteraction, embed):
    with open("Database/Server/canais.json") as server_file:
        server_db = json.load(server_file)
        logs = server_db["logs"]

    if not logs:
        return

    canal = inter.guild.get_channel(int(logs))
    if not canal: return

    await canal.send(embed=embed)