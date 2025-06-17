import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *

class ClsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def cls(self, inter: disnake.ApplicationCommandInteraction, quantidade: int):
        """
        Use to clear a quantity of messages
        
        Parameters
        ----------
        quantidade: quantidade de mensagens a serem apagadas
        """
        await inter.response.send_message(f"{carregarAnimado} Aguarde um momento", ephemeral=True)

        if not inter.user.guild_permissions.manage_messages:
            await inter.followup.send(f"{negativo} Você não tem permissão para gerenciar mensagens.", ephemeral=True)
            return

        if not inter.guild.me.guild_permissions.manage_messages:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para limpar mensagens.", ephemeral=True)
            return

        try:
            await inter.channel.purge(limit=quantidade)
            await inter.channel.send(
                f"`{quantidade}` mensagens limpas no canal por {inter.user.mention}"
            )
        except:
            await inter.edit_original_message(f"{negativo} Ocorreu um erro ao tentar limpar o canal.")

def setup(bot: commands.Bot):
    bot.add_cog(ClsCommand(bot))
