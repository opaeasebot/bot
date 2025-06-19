import disnake
from disnake import *
from disnake.ext import commands
from datetime import datetime
import requests
import base64
import os
import json
import asyncio
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from Functions.CarregarEmojis import *
from Functions.FormasPagamentos import *

diretorio_atual = os.getcwd()
caminho_p12 = os.path.join(diretorio_atual, "Database", "Vendas", "certificado.p12")
caminho_pem = os.path.join(diretorio_atual, "Database", "Vendas", "certificado.pem")

def converter_p12_para_pem(caminho_p12, caminho_pem, senha=None):
    try:
        with open(caminho_p12, "rb") as arquivo_p12:
            p12_data = arquivo_p12.read()

        chave_privada, certificado, cadeias_certificados = load_key_and_certificates(
            p12_data, senha.encode() if senha else None
        )

        pem_chave_privada = chave_privada.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            NoEncryption()
        )
        pem_certificado = certificado.public_bytes(Encoding.PEM)

        with open(caminho_pem, "wb") as arquivo_pem:
            arquivo_pem.write(pem_chave_privada)
            arquivo_pem.write(pem_certificado)

        return True
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        return False

def salvarEfi(client_id, client_secret):
    try:
        caminho_arquivo = "Database/Vendas/pagamentos.json"
        a = ObterFormasPagamento()
        db = a["efi"]

        def ObterAccessToken():
            credentials = {
                "client_id": client_id,
                "client_secret": client_secret,
            }
            certificado = caminho_pem
            auth = base64.b64encode(f"{credentials['client_id']}:{credentials['client_secret']}".encode()).decode()
            url = "https://pix.api.efipay.com.br/oauth/token"
            payload = "{\r\n    \"grant_type\": \"client_credentials\"\r\n}"
            headers = {
                'Authorization': f"Basic {auth}",
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload, cert=certificado)
            return response.json()["access_token"]

        def CriarChavePix():
            pix_url = 'https://pix.api.efipay.com.br/v2/gn/evp'
            access_token = ObterAccessToken()
            headers = {
                'Authorization': f'Bearer {access_token}',
                "certificate": caminho_pem
            }
            response = requests.post(pix_url, headers=headers)
            return response.json().get("chave")

        chavePix = CriarChavePix()

        with open(caminho_arquivo, "r") as f:
            db = json.load(f)
        
        db["efi"] = {
            "habilitado": db["efi"]["habilitado"],
            "configurado": True,
            "clientID": client_id,
            "clientSecret": client_secret,
            "chavePix": chavePix
        }

        with open(caminho_arquivo, "w") as f:
            json.dump(db, f, indent=4)

        return True
    except Exception as e:
        print(f"Erro ao salvar as credenciais: {e}")
        return False

async def GerenciarEfi(inter: disnake.MessageInteraction):
    FormasPagamento = ObterFormasPagamento()
    Efi = FormasPagamento["efi"]

    Button = {
        "label": "Desabilitar" if Efi["habilitado"] else "Habilitar",
        "style": disnake.ButtonStyle.danger if Efi["habilitado"] else disnake.ButtonStyle.success,
    }

    def formatar_forma_pagamento(nome, habilitado, configurado):
        status_habilitado = f"{positivo} ``Habilitado``" if habilitado else f"{negativo} ``Desabilitado``"
        status_configurado = f"{positivo} ``Configurado``" if configurado else f"{negativo} ``Não configurado``"
        return f"{status_habilitado}\n{status_configurado}"

    embed = disnake.Embed(
        title="Efí Bank | Formas de Pagamento",
        description="Aqui, você pode configurar tudo referente ao Efi Bank.",
        timestamp=datetime.now(),
        color=disnake.Color(0x00FFFF)
    )
    embed.add_field(name="Sistema", value=formatar_forma_pagamento("Efi", Efi["habilitado"], Efi["configurado"]), inline=False)
    embed.add_field(name="Chave PIX", value=f"`{Efi['chavePix']}`" if Efi["chavePix"] else f"{negativo} Não configurada")
    embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

    components = [
        [
            disnake.ui.Button(label="Configurar Credenciais", style=disnake.ButtonStyle.blurple, custom_id="ConfigurarSistemaEFI", emoji=attach),
            disnake.ui.Button(label=Button["label"], style=Button["style"], custom_id="HabilitarDesabilitarSistemaPagamento_Efi", emoji=reload),
        ],
        [
            disnake.ui.Button(label="Conferir Tutorial", url="https://www.youtube.com/watch?v=DKyFF65McYQ"),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelConfigurar_FormasPagamento"),
        ]
    ]

    await inter.edit_original_message(content="", embed=embed, components=components)

class ConfigurarEfiBankModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Client ID",
                placeholder="Client_Id_XxxXxXx",
                custom_id="clientID",
                style=disnake.TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Client Secret",
                placeholder="Client_Secret_XxxXxXx",
                custom_id="clientSecret",
                style=disnake.TextInputStyle.short,
            ),
        ]
        super().__init__(title="Credenciais Efi Bank", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        clientID = inter.text_values["clientID"]
        clientSecret = inter.text_values["clientSecret"]

        def valida_chave(chave):
            partes = chave.split("_")
            return len(partes) == 3 and all(partes)

        if not valida_chave(clientID) or not valida_chave(clientSecret):
            await inter.response.edit_message(
                f"{negativo} Não foi possível verificar suas chaves.\nVeja o formato e tente novamente:\n``Client_Id_XxxXxXx``\n``Client_Secret_XxxXxXx``",
                embed=None,
                components=[disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarDefinicoesFormasPagamento_Efi")]
            )
            return

        await inter.response.edit_message(
            "Agora, por favor, envie o arquivo `.p12` (certificado EFI) dentro de 1 minuto.",
            embed=None,
            components=None
        )

        def check(message):
            return message.author == inter.author and isinstance(message, disnake.Message) and message.attachments

        try:
            msg = await inter.bot.wait_for("message", check=check, timeout=60.0)
            for attachment in msg.attachments:
                if attachment.filename.endswith(".p12"):
                    await inter.edit_original_message(f"{carregarAnimado} Aguarde um momento", components=None, embed=None)
                    await attachment.save(caminho_p12)
                    await msg.delete()

                    if converter_p12_para_pem(caminho_p12, caminho_pem):
                        os.remove(caminho_p12)
                        salvarEfi(client_id=clientID, client_secret=clientSecret)
                        await GerenciarEfi(inter)

                    else:
                        await inter.edit_original_message(
                            f"{negativo} Ocorreu um erro ao converter o certificado. Tente novamente.",
                            components=[disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarDefinicoesFormasPagamento_Efi")]
                        )
                    return

            await inter.edit_original_message(
                f"{negativo} O arquivo enviado não é válido. Por favor, envie um arquivo com a extensão .p12.",
                components=[disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarDefinicoesFormasPagamento_Efi")]
            )
        except asyncio.TimeoutError:
            await inter.edit_original_message(
                f"{negativo} O tempo para enviar o arquivo expirou. Tente novamente.",
                components=[disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarDefinicoesFormasPagamento_Efi")]
            )

class EfiPagamentosPlugin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def EFIExtensionButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarDefinicoesFormasPagamento_Efi":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            await GerenciarEfi(inter)
        elif inter.component.custom_id == "HabilitarDesabilitarSistemaPagamento_Efi":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            with open("Database/Vendas/pagamentos.json") as f:
                db = json.load(f)
            if db["efi"]["configurado"] == True:
                db["efi"]["habilitado"] = not db["efi"]["habilitado"]
                with open("Database/Vendas/pagamentos.json", "w") as f:
                    json.dump(db, f, indent=4)
                if db["efi"]["habilitado"]:
                    await GerenciarEfi(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento EFI foi habilitado.", ephemeral=True, delete_after=5)
                else:
                    await GerenciarEfi(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento EFI foi desabilitado.", ephemeral=True, delete_after=5)
            else:
                await GerenciarEfi(inter)
                await inter.followup.send(f"{negativo} As credenciais não estão configuradas.", ephemeral=True, delete_after=3)
        elif inter.component.custom_id == "ConfigurarSistemaEFI":
            await inter.response.send_modal(ConfigurarEfiBankModal())

def setup(bot: commands.Bot):
    bot.add_cog(EfiPagamentosPlugin(bot))
