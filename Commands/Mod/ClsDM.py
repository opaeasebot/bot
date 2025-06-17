import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *

class ClsDMCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def clsdm(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        """
        Use to clear all messages with a member

        Parameters
        ----------
        user: usuário em que as mensagens serão apagadas
        """
        await inter.response.send_message(f"{carregarAnimado} Aguarde um momento", ephemeral=True)
        if verificar_permissao(inter.user.id):
            try:
                dm_channel = await user.create_dm()
                async for message in dm_channel.history(limit=100):
                    if message.author == inter.bot.user:
                        await message.delete()
                await inter.edit_original_message(f"{positivo} Todas as mensagens foram apagadas.")
            except:
                await inter.edit_original_message(f"{negativo} Não foi possível apagar as mensagens.")
        else: await inter.edit_original_message(f"{negativo} Faltam permissões para executar essa ação")

def setup(bot: commands.Bot):
    bot.add_cog(ClsDMCommand(bot))
