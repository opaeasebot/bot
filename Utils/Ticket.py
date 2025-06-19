import random, string
from Functions.Database import Database

def ObterDatabase():
    db = Database.Obter("Database/Tickets/ticket.json")
    return db

def ObterTicket(ticketID: str):
    db = ObterDatabase()
    try:
        return db[ticketID]
    except:
        return None

def ObterCategoria(ticketID: str, categoriaID: str):
    ticket = ObterTicket(ticketID)
    if not ticket: return None

    try:
        return ticket["categorias"][categoriaID]
    except: return None

def ObterTicketAberto(ticketID: str):
    ticket = Database.Obter("Database/Tickets/ticketsAbertos.json")
    
    try:
        if ticket[ticketID]: return ticket[ticketID]
        else: return None
    except: return None

def GerarString():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=13))