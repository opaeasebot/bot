from disnake import *
import json
from datetime import *

####################################################################################

def ObterCanais():
    with open("Database/Server/canais.json") as canais:
        db = json.load(canais)
        return db

def ObterCargos():
    with open("Database/Server/cargos.json") as canais:
        db = json.load(canais)
        return db

####################################################################################

def salvarCanaisDatabase(canais):
    with open("Database/Server/canais.json", "w", encoding="utf-8") as arquivo:
        json.dump(canais, arquivo, indent=4, ensure_ascii=False)

async def removerCanal(canal: str):
    canais = ObterCanais()
    canal_chave = canal.lower()

    if canal_chave in canais:
        canais[canal_chave] = None
        salvarCanaisDatabase(canais)


####################################################################################

def salvarCargosDatabase(cargos):
    with open("Database/Server/cargos.json", "w", encoding="utf-8") as arquivo:
        json.dump(cargos, arquivo, indent=4, ensure_ascii=False)

async def removerCargo(cargo: str):
    cargos = ObterCargos()
    cargo_chave = cargo.lower()

    if cargo_chave in cargos:
        cargos[cargo_chave] = None
        salvarCargosDatabase(cargos)