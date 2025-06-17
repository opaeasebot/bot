import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

class UnlockCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Use to unlock the text channel")
    async def unlock(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        if not inter.user.guild_permissions.manage_channels:
            await inter.followup.send(f"{negativo} Você não tem permissão para gerenciar canais.", ephemeral=True)
            return

        if not inter.guild.me.guild_permissions.manage_channels:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para desbloquear este canal.", ephemeral=True)
            return

        channel = inter.channel
        guild = inter.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = None
        overwrite.create_public_threads = None
        overwrite.create_private_threads = None

        try:
            await channel.set_permissions(guild.default_role, overwrite=overwrite, reason=f"Canal desbloqueado por {inter.user.name}")

            await inter.followup.send(f"{positivo} O canal `{channel.name}` foi desbloqueado com sucesso.", ephemeral=True)
            await channel.send(f"Este canal foi desbloqueado por `{inter.user.name}`. Agora é possível enviar mensagens e criar tópicos.")

        except disnake.Forbidden:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para desbloquear este canal.", ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"{negativo} Ocorreu um erro ao tentar desbloquear o canal: {e}", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(UnlockCommand(bot))
