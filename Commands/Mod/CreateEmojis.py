import disnake
from disnake.ext import commands
import json
import os
import base64
import aiohttp
import sys
import asyncio

from Functions.VerificarPerms import *

async def ObterIDBOT(token):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": f"Bot {token}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["id"]
            else:
                raise Exception(f"Erro ao obter APP_ID: {response.status} - {await response.text()}")

def obter_app_id(token):
    return asyncio.run(ObterIDBOT(token))

with open("config.json") as f:
    config = json.load(f)
    BOT_TOKEN = config["token"]

EMOJIS_DB = "Database/emojis.json"
EMOJI_FOLDER = "Emojis/"
APP_ID = obter_app_id(BOT_TOKEN)

def load_emojis():
    if os.path.exists(EMOJIS_DB):
        with open(EMOJIS_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_emojis(data):
    with open(EMOJIS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def upload_emoji(session, name, image_path):
    file_extension = os.path.splitext(image_path)[1].lower()
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    if file_extension == ".gif":
        base64_image = f"data:image/gif;base64,{base64.b64encode(image_data).decode()}"
    else:
        base64_image = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"

    url = f"https://discord.com/api/v9/applications/{APP_ID}/emojis"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": name,
        "image": base64_image
    }

    async with session.post(url, headers=headers, json=payload) as response:
        if response.status == 201:
            data = await response.json()
            return data["id"]
        else:
            error = await response.text()
            raise Exception(f"Erro ao criar emoji: {response.status} {error}")

class CreateEmojis(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emojis = load_emojis()

    @commands.slash_command(description="Adiciona emojis diretamente no bot")
    async def add_emojis(self, inter: disnake.ApplicationCommandInteraction):
        quantidadeInicial = 0
        total_emojis = len(self.emojis)
        await inter.response.send_message(f"`🚀` Iniciando upload dos emojis para o bot (0/{total_emojis})", ephemeral=True)

        if not verificar_owner(inter.user.id):
            await inter.edit_original_message("`❌` Você não tem permissão para executar essa ação.")
            return

        async with aiohttp.ClientSession() as session:
            for name in self.emojis:
                if self.emojis[name]:
                    continue

                image_path = os.path.join(EMOJI_FOLDER, f"{name}.gif")
                if not os.path.isfile(image_path):
                    image_path = os.path.join(EMOJI_FOLDER, f"{name}.png")

                if not os.path.isfile(image_path):
                    continue

                try:
                    emoji_id = await upload_emoji(session, name, image_path)
                    emoji_tag = f"<a:{name}:{emoji_id}>" if image_path.endswith('.gif') else f"<:{name}:{emoji_id}>"
                    self.emojis[name] = emoji_tag
                    save_emojis(self.emojis)
                    quantidadeInicial += 1
                except Exception as e:
                    pass
                
                await inter.edit_original_message(f"`🚀` Iniciando upload dos emojis para o bot ({quantidadeInicial}/{total_emojis})")

        await inter.edit_original_message(f"`🎉` Upload dos emojis finalizado! ({quantidadeInicial}/{total_emojis})\n`🚧` Seu Bot será reiniciado para salvar as novas alterações.")
        
        os.execv(sys.executable, ['python'] + sys.argv)
        return

def setup(bot: commands.Bot):
    bot.add_cog(CreateEmojis(bot))
