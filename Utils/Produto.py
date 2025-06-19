from Functions.Database import Database

def ObterProduto(produtoID):
    db = Database.Obter("Database/Vendas/produtos.json")
    try:
        produto = db[produtoID]
    except:
        produto = None
    return produto

def ObterCampo(produtoID, campoID):
    db = Database.Obter("Database/Vendas/produtos.json")
    try:
        produto = db[produtoID]
        campo = produto["campos"][campoID]
    except:
        campo = None
    return campo

def ObterCarrinho(carrinhoID):
    db = Database.Obter("Database/Vendas/carrinhos.json")
    carrinho = db[carrinhoID]
    return carrinho