import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

class KickCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def kick(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="member", description="Selecione o membro para expulsar."),
        reason: str = commands.Param(default="Não especificado", name="reason", description="Motivo da expulsão.")
    ):
        """
        Use to kick from your server
        """
        try:
            await inter.response.defer(ephemeral=True)


            if not inter.user.guild_permissions.kick_members:
                await inter.followup.send(f"{negativo} Você não tem permissão para expulsar membros.", ephemeral=True)
                return

            if member == inter.user:
                await inter.followup.send(f"{negativo} Você não pode se expulsar!", ephemeral=True)
                return

            if member == self.bot.user:
                await inter.followup.send(f"{negativo} Você não pode expulsar o bot.", ephemeral=True)
                return

            if member.top_role >= inter.user.top_role:
                await inter.followup.send(f"{negativo} Você não pode expulsar um membro com um cargo igual ou superior ao seu.", ephemeral=True)
                return

            try:
                await member.kick(reason=f"Expulso por {inter.user} - Motivo: {reason}")

                await inter.followup.send(f"{positivo} `{member}` foi expulso com sucesso! Motivo: `{reason}`.", ephemeral=True)

            except disnake.Forbidden or commands.errors.MissingPermissions:
                await inter.followup.send(f"{negativo} Não consegui expulsar este membro. Verifique minhas permissões.", ephemeral=True)
            except Exception as e:
                await inter.followup.send(f"{negativo} Ocorreu um erro: {e}", ephemeral=True)

        except:
            await inter.response.defer(with_message=False)

def setup(bot: commands.Bot):
    bot.add_cog(KickCommand(bot))
