import json
import disnake

from Functions.Database import Database

class Perms:
    @staticmethod
    def VerificarPerms(user_id) -> bool:
        perms = Database.Obter("Database/perms.json")
        return str(user_id) in perms

    @staticmethod
    def VerificarDM(inter: disnake.MessageInteraction) -> bool:
        return inter.guild is not None and inter.guild.name is not None

    @staticmethod
    def VerificarOwner(user_id) -> bool:
        config = Database.Obter("config.json")
        return str(user_id) == str(config["owner"])
