import disnake
from disnake.ext import commands
from Functions.Database import Database
from Functions.CarregarEmojis import *

async def AutoReaction(message: disnake.Message):
    try:
        db = Database.Obter("Database/Server/acoesauto.json")
        reacoes = db["reacoes"]
        sistema = reacoes["sistema"], canais = reacoes["canal"], emoji = reacoes["emoji"]

        if "ease" in message.content.lower():
            try: await message.add_reaction(emoji=ease)
            except: pass

        if sistema:
            if not canais: return
            
            for canal_id in canais:
                try:
                    channel = message.guild.get_channel(int(canal_id))
                    if channel and message.channel == channel:
                        if message.author.id != message.guild.me.id:
                            await message.add_reaction(emoji=emoji)
                            break
                except: pass
        else: return 
    except: pass
    

class EventsOnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def MessageEventListener(self, message: disnake.Message):
        await AutoReaction(message)

def setup(bot: commands.Bot):
    bot.add_cog(EventsOnMessage(bot))
