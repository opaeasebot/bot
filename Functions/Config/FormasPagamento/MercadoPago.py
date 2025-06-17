import disnake
from disnake import *
from disnake.ext import commands
import json
import requests
import mercadopago
from datetime import *

from Functions.CarregarEmojis import *
from Functions.Config.FormasPagamentos import *

class ConfigurarMercadoPagoModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Chave SDK da API (Mercado Pago)",
                placeholder="APP_USR-000000000000000-XXXXXXX-XXXXXXXXX",
                custom_id="accesskey",
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(title="Credenciais Mercado Pago", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)

        accessKey = inter.text_values["accesskey"]
        status = verificarMercadoPago(accessKey)

        if status == True:
            salvarMP(access_key=accessKey)
            await GerenciarMercadoPago(inter)
            await inter.followup.send(f"{positivo} Chave salva com sucesso.", ephemeral=True, delete_after=2)
        else:
            await GerenciarMercadoPago(inter)
            msg = f"""
{negativo} Access Token inválida! Caso precise de ajuda, olhe o tutorial abaixo de como obter.
1. Acesse o [painel de desenvolvedores do Mercado Pago](https://www.mercadopago.com.br/developers/pt)
2. Acesse **Suas Interações** no canto superior direito
3. Selecione uma aplicação ou crie uma com a opção **Checkout Transparente**
4. Acesse **Credenciais de produção**
5. Copie o Access Key mostrado e registre no Bot novamente
            """
            components = [
                disnake.ui.Button(label="Painel de desenvolvedores", url="https://www.mercadopago.com.br/developers/pt"),
            ]
            await inter.followup.send(content=msg, components=components, ephemeral=True)

def verificarMercadoPago(accesskey: str) -> bool:
    headers = {
        "Authorization": f"Bearer {accesskey}"
    }
    verificar = requests.get(url="https://api.mercadopago.com/users/me", headers=headers)
    if verificar.status_code == 200:
        return True
    else:
        return False

def salvarMP(access_key):
    try:
        caminho_arquivo = "Database/Vendas/pagamentos.json" # quiser alterar so mexer aq
        
        with open(caminho_arquivo, "r") as f:
            db = json.load(f)
        
        db["mercadopago"] = {
            "habilitado": db["mercadopago"]["habilitado"],
            "configurado": True,
            "access_key": access_key
        }

        with open(caminho_arquivo, "w") as f:
            json.dump(db, f, indent=4)

        return True
    except Exception as e:
        print(f"Erro ao salvar as credenciais: {e}")
        return False

async def GerenciarMercadoPago(inter: disnake.MessageInteraction):
    FormasPagamento = ObterFormasPagamento()
    MercadoPago = FormasPagamento["mercadopago"]
    access_key = MercadoPago["access_key"]

    Button = {
        "label": "Desabilitar" if MercadoPago["habilitado"] else "Habilitar",
        "style": disnake.ButtonStyle.danger if MercadoPago["habilitado"] else disnake.ButtonStyle.success,
    }

    def formatar_forma_pagamento(nome, habilitado, configurado):
        status_habilitado = f"{positivo} ``Habilitado``" if habilitado else f"{negativo} ``Desabilitado``"
        status_configurado = f"{positivo} ``Configurado``" if configurado else f"{negativo} ``Não configurado``"
        
        return f"{status_habilitado}\n{status_configurado}"

    embed = disnake.Embed(
        title="Mercado Pago | Formas de Pagamento",
        description="Aqui, você pode configurar tudo referente ao Mercado Pago.",
        timestamp=datetime.now(),
        color=disnake.Color(0x00FFFF)
    )

    embed.add_field(name="Sistema", value=formatar_forma_pagamento("Mercado Pago", MercadoPago["habilitado"], MercadoPago["configurado"]), inline=False)

    if access_key:
        visible_start = access_key[:10]
        visible_end = access_key[-10:]
        hidden = "*" * 20
        formatted_key = f"```{visible_start}{hidden}{visible_end}```"
        embed.add_field(name="Access Key", value=formatted_key)
    else:
        embed.add_field(name="Access Key", value=f"{negativo} `Não definido`")

    embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

    components = [
        [
            disnake.ui.Button(label="Configurar Credenciais", style=disnake.ButtonStyle.blurple, custom_id=f"ConfigurarSistemaMP", emoji=attach),
            disnake.ui.Button(label=Button["label"], style=Button["style"], custom_id=f"HabilitarDesabilitarSistemaPagamento_MP", emoji=reload),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelConfigurar_FormasPagamento"),
        ]
    ]

    await inter.edit_original_message(content="", embed=embed, components=components)

class MPPagamentosPlugin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def MPExtensionButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarDefinicoesFormasPagamento_MercadoPago":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            await GerenciarMercadoPago(inter)
    
        elif inter.component.custom_id == "HabilitarDesabilitarSistemaPagamento_MP":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            with open("Database/Vendas/pagamentos.json") as f:
                db = json.load(f)

            if db["mercadopago"]["configurado"] == True:
                db["mercadopago"]["habilitado"] = not db["mercadopago"]["habilitado"]
                
                with open("Database/Vendas/pagamentos.json", "w") as f:
                    json.dump(db, f, indent=4)

                if db["mercadopago"]["habilitado"]:
                    await GerenciarMercadoPago(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento Mercado Pago foi habilitado.", ephemeral=True, delete_after=2)
                else:
                    await GerenciarMercadoPago(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento Mercado Pago foi desabilitado.", ephemeral=True, delete_after=2)
            else:
                await GerenciarMercadoPago(inter)
                await inter.followup.send(f"{negativo} As credenciais não estão configuradas.", ephemeral=True, delete_after=3)

        elif inter.component.custom_id == "ConfigurarSistemaMP":
            await inter.response.send_modal(ConfigurarMercadoPagoModal())

def setup(bot: commands.Bot):
    bot.add_cog(MPPagamentosPlugin(bot))