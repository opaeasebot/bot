import disnake
from disnake import *
import json
import os
import re
from datetime import *
import requests
import mercadopago
from efipay import EfiPay
from Functions.CarregarEmojis import *
import asyncio
import random
import string
import base64

def GerarString():
    caracteres = string.ascii_letters + string.digits
    id_devolucao = ''.join(random.choices(caracteres, k=33))

    return id_devolucao

def ObterCarrinho(carrinhoID):
    with open("Database/Vendas/carrinhos.json") as f:
        db = json.load(f)
        carrinho = db[carrinhoID]
        return carrinho

def ObterFormasPagamento():
    with open("Database/Vendas/pagamentos.json") as f:
        db = json.load(f)

    return db

def criar_qr_code(response):
    with open("Database/Vendas/vendas.json") as f:
        db = json.load(f)
        corMain = db["marca"]["cores"]["principal"]
        corSec = db["marca"]["cores"]["sec"]
        logoUrl = db["marca"]["url"]

    logo_id = None

    if logoUrl:
        try:
            logo_response = requests.get(logoUrl, stream=True)
            if logo_response.status_code == 200:
                with open("logo_temp.png", "wb") as file:
                    for chunk in logo_response.iter_content(1024):
                        file.write(chunk)

                with open("logo_temp.png", "rb") as image_file:
                    upload_response = requests.post(
                        url="https://api.qrcode-monkey.com/qr/uploadImage",
                        files={"file": ("logo_temp.png", image_file, "image/png")},
                        headers={
                            "Content-Type": "multipart/form-data"
                        }
                    )

                if upload_response.status_code == 200:
                    logo_id = upload_response.json().get("file")

        except Exception as e:
            print(f"Erro ao fazer upload da imagem: {e}")
        finally:
            if os.path.exists("logo_temp.png"):

                os.remove("logo_temp.png")

    payload = {
        "data": str(response),
        "config": {
            "body": "square",
            "eye": "frame0",
            "eyeBall": "ball0",
            "bodyColor": "#000000",
            "bgColor": "#FFFFFF",
            "eye1Color": "#000000",
            "eye2Color": "#000000",
            "eye3Color": "#000000",
            "eyeBall1Color": "#000000",
            "eyeBall2Color": "#000000",
            "eyeBall3Color": "#000000",
            "gradientColor1": f"#{corMain}",
            "gradientColor2": f"#{corSec}",
            "gradientType": "linear",
            "gradientOnEyes": "true",
            "logo": logo_id if logo_id else None,
            "logoMode": "default"
        },
        "size": 550,
        "download": "imageUrl",
        "file": "png"
    }

    qrCode = requests.post(url="https://api.qrcode-monkey.com/qr/custom", json=payload)

    if qrCode.status_code == 200:
        return f"https:{qrCode.json()['imageUrl']}"
    else:
        print(f"Erro ao gerar QR Code: {qrCode.status_code}, {qrCode.text}")
        return None

class MercadoPagoPagamento():
    def GerarPagamento(valor: float):
        db = ObterFormasPagamento()
        mp = db["mercadopago"]

        sdk = mercadopago.SDK(str(mp["access_key"]))
        payment_data = {
            "transaction_amount": valor,
            "payment_method_id": "pix",
            "payer": {
                "email": "seu_email@example.com"
            }
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        if "point_of_interaction" in payment:
            qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
            payment = payment["id"]
        else:
            return False

        qrcodeURL = criar_qr_code(qr_code)

        return qr_code, qrcodeURL, payment
    
    def ReembolsarBanco(paymantData):
        db = ObterFormasPagamento()
        mp = db["mercadopago"]
        acesstoken = mp["access_key"]

        url = f"https://api.mercadopago.com/v1/payments/{paymantData["id"]}/refunds"
        headers = {
            "Authorization": f"Bearer {acesstoken}"
        }
        requests.post(url=url, headers=headers)

    def VerificarBancoBloqueado(paymentData):
        with open("Database/Vendas/bancosbloqueados.json") as f:
            db = json.load(f)
        
        for options in db["bancosbloqueados"]:
            if options == paymentData["point_of_interaction"]["transaction_data"]["bank_info"]["payer"]["long_name"]:
                MercadoPagoPagamento.ReembolsarBanco(paymentData)
                return True
        
        return False

    async def VerificarPagamento(carrinhoID: str):
        with open("Database/Vendas/pagamentos.json") as f:
            pagamentos = json.load(f)
            accesstoken = pagamentos["mercadopago"]["access_key"]

        sdk = mercadopago.SDK(str(accesstoken))
        tempo_maximo = 10 * 60
        intervalo = 5
        tempo_decorrido = 0
        carrinho = ObterCarrinho(carrinhoID)
        paymentID = carrinho["info"]["pagamento"]["paymentID"]

        while tempo_decorrido < tempo_maximo:
                payment_info_response = sdk.payment().get(paymentID)
                payment_info = payment_info_response["response"]

                if payment_info["status"] == "approved":
                    if MercadoPagoPagamento.VerificarBancoBloqueado(payment_info):
                        return "Bloqueado"
                    
                    return True
                else:
                    tempo_decorrido += intervalo
                    return False


        return "Cancelled"

class EfiBankPagamento():
    def EstornarPagamento(e2eId: str, valor):
        id = GerarString()

        url = f"https://pix.api.efipay.com.br/v2/pix/{e2eId}/devolucao/{id}"
        payload = {
            "valor": f"{valor:.2f}"
        }
        
        headers = {
            "Authorization": f"Bearer {EfiBankPagamento.ObterAccessToken()}",
            "certificate": "Database/Vendas/certificado.pem"
        }

        response = requests.put(url, json=payload, headers=headers)

    def VerificarBancoBloqueado(codigoBanco: str, txid: str, valor: float):
        def ExtrairCodigoBanco(codigo_completo):
            match = re.match(r'E(\d{8})', codigo_completo)
            
            if match:
                return match.group(1)
        
        codigo_banco = ExtrairCodigoBanco(codigoBanco)

        bancosEfi = {
            "Nu Pagamentos S.A.": "18236120",
            "Mercadopago.com Representações Ltda.": "10573521",
            "Banco do Brasil S.A.": "00000000",
            "Picpay Serviços S.A.": "22896431",
            "Caixa Econômica Federal": "00360305",
            "Banco Itaucard S.A.": "17192451",
            "Itaú Unibanco S.A.": "60701190",
            "Banco Bradesco S.A.": "60746948",
            "Banco Inter S.A.": "00416968",
            "Neon Pagamentos S.A.": "20855875",
            "Original S.A.": "92894922",
            "Next": "60746948",
            "Agibank": "10664513",
            "Santander (Brasil) S.A.": "90400888",
            "Banco C6 S.A.": "31872495",
            "PagSeguro Internet S.A.": "08561701",
            "NG CASH PAGAMENTOS LTDA.": "40710595"
        }
        
        for banco_bloqueado in db["bancosbloqueados"]:
            if banco_bloqueado in bancosEfi:
                banco_bloqueado_codigo = bancosEfi[banco_bloqueado]
                if codigo_banco == banco_bloqueado_codigo:
                    EfiBankPagamento.EstornarPagamento(codigoBanco, valor)
                    return True

        return False

    def GerarPagamento(valor: float):
        a = ObterFormasPagamento()
        db = a["efi"]

        credentials = {
            'client_id': db["clientID"],
            'client_secret': db["clientSecret"],
            'sandbox': False,
            'certificate': 'Database/Vendas/certificado.pem'
        }
        efi = EfiPay(credentials)

        body = {
            'calendario': {
                'expiracao': 600
            },
            'valor': {
                'original': f"{valor:.2f}"
            },
            "chave": f"{db["chavePix"]}",
            'solicitacaoPagador': 'Cobrança digital de produto.'
        }
        response =  efi.pix_create_immediate_charge(body=body)
        if "txid" in response:
            qrcodeURL = criar_qr_code(response["pixCopiaECola"])
            return response["pixCopiaECola"], qrcodeURL, response["txid"]
    
    def ObterAccessToken():
        a = ObterFormasPagamento()
        db = a["efi"]

        credentials = {
        "client_id": db["clientID"],
        "client_secret": db["clientSecret"],
        }

        certificado = 'Database/Vendas/certificado.pem'

        auth = base64.b64encode(
        (f"{credentials['client_id']}:{credentials['client_secret']}"
        ).encode()).decode()

        url = "https://pix.api.efipay.com.br/oauth/token"

        payload="{\r\n    \"grant_type\": \"client_credentials\"\r\n}"
        headers = {
        'Authorization': f"Basic {auth}",
        'Content-Type': 'application/json'
        }

        response = requests.request("POST",
                                url,
                                headers=headers,
                                data=payload,
                                cert=certificado)

        return response.json()["access_token"]

    def VerificarPagamento(txid: str, carrinhoID):
        a = ObterFormasPagamento()
        db = a["efi"]

        credentials = {
            'client_id': db["clientID"],
            'client_secret': db["clientSecret"],
            'sandbox': False,
            'certificate': 'Database/Vendas/certificado.pem'
        }
        efi = EfiPay(credentials)


        response = efi.pix_detail_charge(params={"txid": txid})
        status = response.get("status")

        if status == "CONCLUIDA":
            # vou deixar para a prox. atualização, a api ta mt bagunçada,
            # n entendi quase nada, mas deixei algumas coisas ja prontas
            # verificarBanco = EfiBankPagamento.VerificarBancoBloqueado(response["pix"]["endToEndId"], txid, carrinho["info"]["valorTotal"])
            # if verificarBanco:
            #     return "Bloqueado"
            # else:
                return True
            
        elif status == "ATIVA":
            return False
        else:
            return "Cancelled"

class SemiAutoPagamento():
    def GerarPagamento():
        db = ObterFormasPagamento()
        response = db["semiauto"]["chavePix"]
        qrcode = criar_qr_code(response)
        return response, qrcode