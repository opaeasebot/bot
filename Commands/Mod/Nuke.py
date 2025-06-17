import disnake
from disnake.ext import commands
from Functions.CarregarEmojis import *

class NukeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Use to nuke the text channel")
    async def nuke(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        if not inter.user.guild_permissions.manage_channels:
            await inter.followup.send(f"{negativo} Você não tem permissão para gerenciar canais.", ephemeral=True)
            return

        if not inter.guild.me.guild_permissions.manage_channels:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para nukar este canal.", ephemeral=True)
            return

        old_channel = inter.channel
        guild = inter.guild

        overwrites = old_channel.overwrites
        category = old_channel.category
        position = old_channel.position

        try:
            new_channel = await guild.create_text_channel(
                name=old_channel.name,
                category=category,
                overwrites=overwrites,
                position=position,
                topic=old_channel.topic,
                slowmode_delay=old_channel.slowmode_delay,
                nsfw=old_channel.nsfw,
                reason=f"Nuke realizado por {inter.user.name}"
            )

            await old_channel.delete(reason=f"Nuke realizado por {inter.user.name}")

            await new_channel.send(f"Nuked by `{inter.user.name}`")

        except disnake.Forbidden:
            await inter.followup.send(f"{negativo} O bot não tem permissões suficientes para nukar este canal.", ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"{negativo} Ocorreu um erro ao tentar nukar o canal: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(NukeCommand(bot))
