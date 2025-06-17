import json
import disnake
from disnake.ext import commands

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            with open("config.json") as f:
                config = json.load(f)
                server = config["server"]
                try:
                    server = self.bot.get_guild(int(server))
                except: return

            embed = disnake.Embed(
                description=f"""
**Bot exclusivo** do servidor `{server.name}`
Comando de painel: `/panel`
Versão do eOS: `{config["versao"]}`
Desenvolvido por [guilherme](https://mdsmax.dev) / [ferramentas](https://discord.gg/ferramentas)
Ping do eOS: `{round(self.bot.latency * 1000)}ms`
-# Para mais informações sobre o Bot, acesse os links abaixo
""",
                color=disnake.Color.blue()
            )
            components = [
                disnake.ui.Button(label="mdsmax.dev", url="https://mdsmax.dev"),
                disnake.ui.Button(label="Github", url="https://github.com/opaeasebot"),
            ]

            await message.reply(embed=embed, components=components)

def setup(bot):
    bot.add_cog(BotInfo(bot))