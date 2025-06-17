import disnake
from disnake.ext import commands
from disnake import *
import asyncio
import json
from datetime import datetime, timedelta
from Functions.Config.Repostagem.Vendas import *

# O auto-react ficou em Events/OnMessage, 
# para aproveitar o Cog feito especialmente para esse tipo de sistema
# De resto, todas as ações automáticas ficam aqui

def ObterDatabase():
    with open("Database/Server/acoesauto.json", "r") as f:
        return json.load(f)

async def acao_repostagem(bot):
    while True:
        db = ObterDatabase()
        repostagem = db.get("repostagem", {})

        if repostagem.get("sistema", False):
            await RepostagemTodasMensagensVendas(bot)
        await asyncio.sleep(5 * 60 * 60)

async def acao_limpeza(bot: commands.Bot):
    while True:
        db = ObterDatabase()
        if db.get("limpeza", {}).get("sistema", False):
            canais = db["limpeza"].get("canal", [])
            delay = db["limpeza"].get("delay", 0)

            if delay > 0:
                for canal in canais:
                    channel = bot.get_channel(int(canal))
                    if channel:
                        await channel.purge(limit=None)
                await asyncio.sleep(delay * 60)
        else:
            await asyncio.sleep(10) 

async def acao_mensagens(bot: commands.Bot):
    while True:
        db = ObterDatabase()
        if db.get("mensagens", {}).get("sistema", False):
            canais = db["mensagens"].get("canal", [])
            content = db["mensagens"].get("content", "")
            delay = db["mensagens"].get("delay", 0)

            lastMSG = db["mensagens"].get("lastMSG", [])
            if lastMSG:
                try:
                    for message_id in lastMSG:
                        msg = await bot.get_channel(int(canais[0])).fetch_message(int(message_id))
                        await msg.delete()
                except Exception as e:
                    print(f"Erro ao tentar apagar as mensagens anteriores: {e}")

            if content:
                new_message_ids = []
                for canal in canais:
                    try:
                        channel = bot.get_channel(int(canal))
                        components = [disnake.ui.Button(label="Mensagem do sistema", disabled=True)]
                        newmsg = await channel.send(content=content, components=components)
                        new_message_ids.append(str(newmsg.id))
                    except Exception as e:
                        print(f"Erro ao enviar mensagem no canal {canal}: {e}")

                db["mensagens"]["lastMSG"] = new_message_ids
                with open("Database/Server/acoesauto.json", "w") as f:
                    json.dump(db, f, indent=4)

            if delay > 0:
                await asyncio.sleep(delay * 60) 
            else:
                await asyncio.sleep(300)
        else:
            await asyncio.sleep(10)

async def executar_acoes(bot):
    await asyncio.gather(
        acao_repostagem(bot),
        acao_limpeza(bot),
        acao_mensagens(bot)
    )