from disnake import *
from datetime import *
from Functions.Database import Database

####################################################################################

def ObterCanais():
    db = Database.Obter("Database/Server/canais.json")
    return db

def ObterCargos():
    db = Database.Obter("Database/Server/cargos.json")
    return db

####################################################################################

def salvarCanaisDatabase(canais):
    Database.Salvar("Database/Server/canais.json", canais)

async def removerCanal(canal: str):
    canais = ObterCanais()
    canal_chave = canal.lower()

    if canal_chave in canais:
        canais[canal_chave] = None
        salvarCanaisDatabase(canais)


####################################################################################

def salvarCargosDatabase(cargos):
    Database.Salvar("Database/Server/cargos.json", cargos)

async def removerCargo(cargo: str):
    cargos = ObterCargos()
    cargo_chave = cargo.lower()

    if cargo_chave in cargos:
        cargos[cargo_chave] = None
        salvarCargosDatabase(cargos)