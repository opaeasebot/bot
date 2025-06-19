import disnake
from disnake import *
from disnake.ext import commands
from Events.OnBotStart import OnBotStart

import json
import os

with open("config.json") as file:
    config = json.load(file)
    token = config["token"]
    owner = config["owner"]
    status = config["status"]
    try:
        server = int(config["server"])
    except:
        print("O servidor configurado em config.json precisa ser um número inteiro dentro de uma string.")
        exit()

    bot = commands.Bot(command_prefix=commands.when_mentioned ,intents=disnake.Intents.all(), test_guilds=[server])

@bot.event
async def on_ready():
    await OnBotStart.StartBot(bot)

bot.load_extension("Commands.Admin.Perms")
bot.load_extension("Commands.Admin.Painel")

bot.load_extension("Commands.Admin.Plugins.BoasVindas")
bot.load_extension("Commands.Admin.Plugins.Ticket")
bot.load_extension("Commands.Admin.Plugins.Definicoes")
bot.load_extension("Commands.Admin.Plugins.Personalizacao")
bot.load_extension("Commands.Admin.Plugins.AcoesAutomaticas")
bot.load_extension("Commands.Admin.Plugins.Vendas")
bot.load_extension("Commands.Admin.Plugins.Carrinho")
bot.load_extension("Commands.Admin.Plugins.ECloud")
bot.load_extension("Commands.Admin.Rendimentos")

bot.load_extension("Functions.FormasPagamento.EFIBank")
bot.load_extension("Functions.FormasPagamento.MercadoPago")
bot.load_extension("Functions.FormasPagamento.SemiAuto")

bot.load_extension("Events.OnMemberJoin")
bot.load_extension("Events.OnRegister")
bot.load_extension("Events.OnMessage")

bot.load_extension("Commands.Mod.Ban")
bot.load_extension("Commands.Mod.Kick")
bot.load_extension("Commands.Mod.Lock")
bot.load_extension("Commands.Mod.Unlock")
bot.load_extension("Commands.Mod.Nuke")
bot.load_extension("Commands.Mod.Cls")
bot.load_extension("Commands.Mod.ClsDM")
bot.load_extension("Commands.Mod.BotInfo")
bot.load_extension("Commands.Mod.Product")
bot.load_extension("Commands.Mod.CreateEmojis")

if __name__ == "__main__":
    if not token or not owner or not server:
        print(f"Alguma informação NECESSÁRIA para o funcionamento do Bot não foi encontrada.\nConfigure o necessário em config.json e tente novamente.")
        exit()

    try:
        bot.run(token)
    except KeyboardInterrupt:
        exit()