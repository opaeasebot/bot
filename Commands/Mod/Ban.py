import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

class BanCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(name="member", description="Selecione o membro para banir"),
        reason: str = commands.Param(name="reason", default="Não especificado", description="Motivo do banimento"),
        delete_days: int = commands.Param(name="delete_days", default=0, description="Dias de mensagens a apagar (0-7)")
    ):
        """
        Use to ban an user from your server
        """
        await inter.response.defer(ephemeral=True)

        if not inter.user.guild_permissions.ban_members:
            await inter.followup.send(f"{negativo} Você não tem permissão para banir membros.", ephemeral=True)
            return

        if not inter.guild.me.guild_permissions.ban_members:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para banir membros.", ephemeral=True)
            return

        if member == inter.user:
            await inter.followup.send(f"{negativo} Você não pode se banir!", ephemeral=True)
            return

        if member == self.bot.user:
            await inter.followup.send(f"{negativo} Você não pode banir o bot!", ephemeral=True)
            return

        if member.top_role >= inter.user.top_role:
            await inter.followup.send(f"{negativo} Você não pode banir um membro com um cargo igual ou superior ao seu.", ephemeral=True)
            return

        if not 0 <= delete_days <= 7:
            await inter.followup.send(f"{negativo} O número de dias para apagar mensagens deve estar entre 0 e 7.", ephemeral=True)
            return

        try:
            await member.ban(reason=f"Banido por {inter.user} - Motivo: {reason}", delete_message_days=delete_days)
            await inter.followup.send(f"{positivo} `{member}` foi banido com sucesso! Motivo: `{reason}`.", ephemeral=True)

        except disnake.Forbidden:
            await inter.followup.send(f"{negativo} Não consegui banir este membro. Verifique minhas permissões.", ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"{negativo} Ocorreu um erro: {e}", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(BanCommand(bot))
