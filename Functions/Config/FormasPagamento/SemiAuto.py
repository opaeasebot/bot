import disnake
from disnake import *
from disnake.ext import commands
import json
import re
from datetime import *

from Functions.CarregarEmojis import *
from Functions.Config.FormasPagamentos import *

def salvarSemi(tipo_chave, chavePIX):
    try:
        caminho_arquivo = "Database/Vendas/pagamentos.json" # quiser alterar so mexer aq
        
        with open(caminho_arquivo, "r") as f:
            db = json.load(f)
        
        db["semiauto"] = {
            "habilitado": db["semiauto"]["habilitado"],
            "configurado": True,
            "chavePix": chavePIX,
            "tipoPix": tipo_chave
        }

        with open(caminho_arquivo, "w") as f:
            json.dump(db, f, indent=4)

        return True
    except Exception as e:
        print(f"Erro ao salvar as credenciais: {e}")
        return False

class AlterarChaveDeAcessoSemiModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Chave Pix",
                placeholder="E-Mail/Telefone/CPF/Chave Aleatória",
                custom_id="chavepix",
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(title="Editar Chave PIX", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
        chave_pix = inter.text_values.get("chavepix")

        # tmj aq chat gpt fortaleceu
        def identificar_tipo_chave(chave):
            if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", chave):  # E-mail
                return "E-Mail"
            elif re.match(r"^\+?[1-9]\d{1,14}$", chave):  # Telefone (E.164)
                return "Telefone"
            elif re.match(r"^\d{11}$", chave):  # CPF (11 dígitos)
                return "CPF"
            elif re.match(r"^[a-fA-F0-9]{32}$", chave):  # Chave Aleatória (32 caracteres hexadecimais)
                return "Chave Aleatória"
            else:
                return "Formato Inválido"

        tipo_chave = identificar_tipo_chave(chave_pix)

        if tipo_chave == "Formato Inválido":
            await GerenciarSemiAuto(inter)
            await inter.followup.send(
                f"{negativo} A chave PIX informada é inválida. Por favor, insira um formato válido (E-Mail, Telefone, CPF ou Chave Aleatória).",
                ephemeral=True,
                delete_after=7
            )
            return
        
        salvarSemi(tipo_chave=tipo_chave, chavePIX=chave_pix)
        await GerenciarSemiAuto(inter)

async def GerenciarSemiAuto(inter: disnake.MessageInteraction):
    FormasPagamento = ObterFormasPagamento()
    SemiAuto = FormasPagamento["semiauto"]

    ChavePIX = f"``{SemiAuto["chavePix"]}``" if SemiAuto["chavePix"] else f"{negativo} ``Não definido``"
    ChavePIXTipo = f"``{SemiAuto["tipoPix"]}``" if SemiAuto["tipoPix"] else f"{negativo} ``Não definido``"

    Button = {
        "label": "Desabilitar" if SemiAuto["habilitado"] else "Habilitar",
        "style": disnake.ButtonStyle.danger if SemiAuto["habilitado"] else disnake.ButtonStyle.success,
    }

    def formatar_forma_pagamento(nome, habilitado, configurado):
        status_habilitado = f"{positivo} ``Habilitado``" if habilitado else f"{negativo} ``Desabilitado``"
        status_configurado = f"{positivo} ``Configurado``" if configurado else f"{negativo} ``Não configurado``"
        
        return f"{status_habilitado}\n{status_configurado}"

    embed = disnake.Embed(
        title="Semi Automático | Formas de Pagamento",
        description='Aqui, você pode definir uma chave Pix e uma mensagem para o seu Ease Bot enviar quando a forma de pagamento "Pix" for selecionada. Ele irá gerar um QR Code com o valor exato do carrinho para essa chave. Lembre-se de que ele não consegue verificar se o pagamento foi aprovado, então você precisará clicar em "Confirmar pagamento" para iniciar o processo de entrega.',
        timestamp=datetime.now(),
        color=disnake.Color(0x00FFFF)
    )

    embed.add_field(name="Sistema", value=formatar_forma_pagamento("Semi Auto", SemiAuto["habilitado"], SemiAuto["configurado"]), inline=False)
    embed.add_field(name="Informações", value=f"**Chave PIX**\n{ChavePIX}\n**Tipo Chave PIX**\n{ChavePIXTipo}", inline=False)
    embed.add_field(name="Mensagem de auxílio", value="Após o pagamento, envie o comprovante aqui", inline=False)
    embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

    components = [
        [
            disnake.ui.Button(label="Configurar Credenciais", style=disnake.ButtonStyle.blurple, custom_id=f"ConfigurarSistemaSemiAuto", emoji=attach),
            disnake.ui.Button(label=Button["label"], style=Button["style"], custom_id=f"HabilitarDesabilitarSistemaPagamento_SemiAuto", emoji=reload),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelConfigurar_FormasPagamento"),
        ]
    ]

    await inter.edit_original_message(content="", embed=embed, components=components)

class SemiAutoPagamentosPlugin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def SemiAutoButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarDefinicoesFormasPagamento_SemiAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            await GerenciarSemiAuto(inter)
        
        elif inter.component.custom_id == "HabilitarDesabilitarSistemaPagamento_SemiAuto":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            with open("Database/Vendas/pagamentos.json") as f:
                db = json.load(f)

            if db["semiauto"]["configurado"] == True:
                db["semiauto"]["habilitado"] = not db["semiauto"]["habilitado"]
                
                with open("Database/Vendas/pagamentos.json", "w") as f:
                    json.dump(db, f, indent=4)

                if db["semiauto"]["habilitado"]:
                    await GerenciarSemiAuto(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento Semi Automático foi habilitado.", ephemeral=True, delete_after=5)
                else:
                    await GerenciarSemiAuto(inter)
                    await inter.followup.send(f"{positivo} O sistema de pagamento Semi Automático foi desabilitado.", ephemeral=True, delete_after=5)
            else:
                await GerenciarSemiAuto(inter)
                await inter.followup.send(f"{negativo} As credenciais não estão configuradas.", ephemeral=True, delete_after=3)

        elif inter.component.custom_id == "ConfigurarSistemaSemiAuto":
            await inter.response.send_modal(AlterarChaveDeAcessoSemiModal())


def setup(bot: commands.Bot):
    bot.add_cog(SemiAutoPagamentosPlugin(bot))