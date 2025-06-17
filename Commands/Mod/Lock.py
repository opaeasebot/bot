import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

class LockCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Use to lock text channel")
    async def lock(self, inter: disnake.ApplicationCommandInteraction):
        try:
            await inter.response.defer(ephemeral=True)

            if not inter.user.guild_permissions.manage_channels:
                await inter.followup.send(f"{negativo} Você não tem permissão para gerenciar canais.", ephemeral=True)
                return

            if not inter.guild.me.guild_permissions.manage_channels:
                await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para bloquear este canal.", ephemeral=True)
                return

            channel = inter.channel
            guild = inter.guild

            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = False
            overwrite.create_public_threads = False
            overwrite.create_private_threads = False

            try:
                await channel.set_permissions(guild.default_role, overwrite=overwrite, reason=f"Canal bloqueado por {inter.user.name}")

                await inter.followup.send(f"{positivo} O canal `{channel.name}` foi bloqueado com sucesso.", ephemeral=True)
                await channel.send(f"Este canal foi bloqueado por `{inter.user.name}`. Enviar mensagens ou criar tópicos está desativado.")

            except disnake.Forbidden:
                await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para bloquear este canal.", ephemeral=True)
            except Exception as e:
                await inter.followup.send(f"{negativo} Ocorreu um erro ao tentar bloquear o canal: {e}", ephemeral=True)
        except:
            await inter.response.defer(with_message=False)

def setup(bot: commands.Bot):
    bot.add_cog(LockCommand(bot))
