import json
import disnake

def verificar_permissao(user_id):
    try:
        with open("Database/perms.json", "r") as perms_file:
            perms = json.load(perms_file)
    except FileNotFoundError:
        return False

    return str(user_id) in perms

def VerificarDM(inter: disnake.MessageInteraction):
    try:
        nome = inter.guild.name
    except:
        return False
    
    if not nome: return False
    return True

def verificar_owner(user_id):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    return str(user_id) == str(config["owner"])
