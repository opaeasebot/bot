import disnake
from disnake.ext import commands
from datetime import *
import json

from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
from Functions.GerenciarCargosCanais import *
from Functions.Config.FormasPagamentos import *

def ObterComponentsPainelInicial():
    components = [
        [
            disnake.ui.Button(label="Canais", emoji=canal, custom_id="PainelConfigurar_Canais"),
            disnake.ui.Button(label="Cargos", emoji=cargo, custom_id="PainelConfigurar_Cargos"),
        ],
        [
            disnake.ui.Button(label="Anti Fake", emoji=users, custom_id="PainelConfigurar_AntiFake"),
            disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Formas de Pagamento", emoji=dollar, custom_id="PainelConfigurar_FormasPagamento"),
        ],
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
    ]
    return components

class AlterarAntiFakeModal(disnake.ui.Modal):
    def __init__(self):
        with open("Database/Server/antifake.json") as f:
            antifake = json.load(f)

        components = [
            disnake.ui.TextInput(
                label="Quantidade mínima de dias para entrar",
                placeholder="Deixe em branco para desativar, serve para todos os campos.",
                custom_id="quantidademinima",
                style=TextInputStyle.short,
                required=False,
                value=antifake["quantidadeMinima"]
            ),
            disnake.ui.TextInput(
                label="Lista de nomes que deseja bloquear",
                placeholder="Separe por linhas cada nome que deseja punir (expulsar)",
                custom_id="nomesbloqueados",
                style=TextInputStyle.paragraph,
                required=False,
                value="\n".join(antifake["nomesBloqueados"])
            ),
        ]
        super().__init__(title="Configurar Anti Fake", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        quantidademinima = inter.text_values["quantidademinima"]
        nomesbloqueados = inter.text_values["nomesbloqueados"].splitlines()

        if quantidademinima:
            try:
                quantidademinima = int(quantidademinima)
            except:
                return await inter.response.send_message(f"{negativo} Você informou um número errado. Tente novamente!", ephemeral=True)

        antifake = {
            "quantidadeMinima": quantidademinima,
            "nomesBloqueados": nomesbloqueados
        }

        with open("Database/Server/antifake.json", "w", encoding="utf-8") as f:
            json.dump(antifake, f, indent=4, ensure_ascii=False)

        await inter.response.send_message(f"{positivo} As configurações foram salvas com sucesso.", ephemeral=True, delete_after=3)

############################ CANAIS ############################
class Canais():
    def ObterMensagemCanais(inter: disnake.MessageInteraction):
        canais = ObterCanais()

        canais_formatados = {
            key: f"<#{valor}>" if valor else f"{negativo} `Não definido`"
            for key, valor in canais.items()
        }

        embed = disnake.Embed(
            title="Configurar Canais",
            description=f"""
**Canal de logs gerais**: {canais_formatados["logs"]}
**Canal de vendas**: {canais_formatados["vendas"]}
**Canal de boas-vindas**: {canais_formatados["boasvindas"]}
**Canal de logs do sistema**: {canais_formatados["sistema"]}
**Canal de registro de auditoria**: {canais_formatados["registroauditoria"]}
**Canal de logs do Anti Fake**: {canais_formatados["antifake"]}
**Canal de logs de tickets**: {canais_formatados["tickets"]}
**Canal de feedbacks**: {canais_formatados["feedbacks"]}
        """,
        timestamp=datetime.now(),
        color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        options = [
            disnake.SelectOption(label="Canal de logs gerais", value="logs", emoji=editar),
            disnake.SelectOption(label="Canal de vendas", value="vendas", emoji=editar),
            disnake.SelectOption(label="Canal de boas-vindas", value="boasvindas", emoji=editar),
            disnake.SelectOption(label="Canal de logs do sistema", value="sistema", emoji=editar),
            disnake.SelectOption(label="Canal de registro de auditoria", value="registroauditoria", emoji=editar),
            disnake.SelectOption(label="Canal de logs do Anti Fake", value="antifake", emoji=editar),
            disnake.SelectOption(label="Canal de logs de tickets", value="tickets", emoji=editar),
            disnake.SelectOption(label="Canal de feedbacks", value="feedbacks", emoji=editar)
        ]

        select = disnake.ui.StringSelect(
            placeholder="Selecione um canal para configurar",
            custom_id="ConfigurarDropdown_Canais",
            options=options
        )

        components = [
            select,
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarPainelConfigurar"),
        ]

        return embed, components

    async def GerenciarCanal(inter: disnake.MessageInteraction, canal_selecionado: str):
        canais = ObterCanais()
        canal_atual_id = canais.get(canal_selecionado.replace("Canal", "").lower(), None)

        botao_remover = disnake.ui.Button(
            label="Remover",
            style=disnake.ButtonStyle.danger,
            emoji=apagar,
            custom_id=f"RemoverCanal_{canal_selecionado}",
            disabled=not canal_atual_id 
        )

        botao_criar = disnake.ui.Button(
            label="Crie pra mim",
            emoji=wand,
            style=disnake.ButtonStyle.primary,
            custom_id=f"CriarCanal_{canal_selecionado}"
        )

        botao_voltar = disnake.ui.Button(
            label="Voltar",
            emoji=voltar,
            style=disnake.ButtonStyle.secondary,
            custom_id="PainelConfigurar_Canais"
        )


        dropdown_canais = disnake.ui.ChannelSelect(
            placeholder="Selecione o novo canal desejado",
            custom_id=f"AlterarCanal_{canal_selecionado}",
            channel_types=[ChannelType.text]
        )

        components = [
            disnake.ui.ActionRow(botao_remover, botao_criar, botao_voltar),
            dropdown_canais
        ]

        await inter.response.edit_message(embed=None, components=components)
        
############################ CARGOS ############################
class Cargos():
    def ObterMensagemCargos(inter: disnake.MessageInteraction):
        cargos = ObterCargos()

        cargos_formatados = {
            key: f"<@&{valor}>" if valor else f"{negativo} `Não definido`"
            for key, valor in cargos.items()
        }

        embed = disnake.Embed(
            title="Configurar Cargos",
            description=f"""
        **Cargo de administrador**: {cargos_formatados["administrador"]}
        **Cargo de suporte**: {cargos_formatados["suporte"]}
        **Cargo de cliente**: {cargos_formatados["cliente"]}
        **Cargo de membro**: {cargos_formatados["membro"]}
        **Cargo verificado**: {cargos_formatados["verificado"]}
        """,
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        options = [
            disnake.SelectOption(label="Cargo de administrador", value="administrador", emoji=editar),
            disnake.SelectOption(label="Cargo de suporte", value="suporte", emoji=editar),
            disnake.SelectOption(label="Cargo de cliente", value="cliente", emoji=editar),
            disnake.SelectOption(label="Cargo de membro", value="membro", emoji=editar),
            disnake.SelectOption(label="Cargo de verificado", value="verificado", emoji=editar)
        ]

        select = disnake.ui.StringSelect(
            placeholder="Selecione um cargo para configurar",
            custom_id="ConfigurarDropdown_Cargos",
            options=options
        )

        components = [
            select,
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarPainelConfigurar"),
        ]

        return embed, components

    async def GerenciarCargo(inter: disnake.MessageInteraction, cargo_selecionado: str):
        cargos = ObterCargos()
        cargo_atual_id = cargos.get(cargo_selecionado.lower(), None)

        botao_remover = disnake.ui.Button(
            label="Remover",
            style=disnake.ButtonStyle.danger,
            emoji=apagar,
            custom_id=f"RemoverCargo_{cargo_selecionado}",
            disabled=not cargo_atual_id 
        )

        botao_criar = disnake.ui.Button(
            label="Crie pra mim",
            emoji=wand,
            style=disnake.ButtonStyle.primary,
            custom_id=f"CriarCargo_{cargo_selecionado}"
        )

        botao_voltar = disnake.ui.Button(
            label="Voltar",
            emoji=voltar,
            style=disnake.ButtonStyle.secondary,
            custom_id="PainelConfigurar_Cargos"
        )


        dropdown_canais = disnake.ui.RoleSelect(
            placeholder="Selecione o novo cargo desejado",
            custom_id=f"AlterarCargo_{cargo_selecionado}"
        )

        components = [
            disnake.ui.ActionRow(botao_remover, botao_criar, botao_voltar),
            dropdown_canais
        ]

        await inter.response.edit_message(embed=None, components=components)

############################ FORMAS PAGAMENTO ############################
class Pagamentos():
    def ObterPainelFormasPagamento(inter: disnake.MessageInteraction):
        FormasPagamento = ObterFormasPagamento()
        MercadoPago = FormasPagamento["mercadopago"]
        Efi = FormasPagamento["efi"]
        SemiAuto = FormasPagamento["semiauto"]

        embed = disnake.Embed(
            title="Configurar Formas de Pagamento",
            description="Configure, habilite e desabilite as formas de pagamento disponíveis por aqui.",
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )

        def formatar_forma_pagamento(nome, habilitado, configurado):
            status_habilitado = f"{positivo} ``Habilitado``" if habilitado else f"{negativo} ``Desabilitado``"
            status_configurado = f"{positivo} ``Configurado``" if configurado else f"{negativo} ``Não configurado``"
            
            return f"{status_habilitado}\n{status_configurado}"

        embed.add_field(name="Mercado Pago", value=formatar_forma_pagamento("Mercado Pago", MercadoPago["habilitado"], MercadoPago["configurado"]), inline=True)
        embed.add_field(name="Efí Bank", value=formatar_forma_pagamento("Efí Bank", Efi["habilitado"], Efi["configurado"]), inline=True)
        embed.add_field(name="Semi Automático", value=formatar_forma_pagamento("Semi Auto", SemiAuto["habilitado"], SemiAuto["configurado"]), inline=True)
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        components = [
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Mercado Pago", custom_id="GerenciarDefinicoesFormasPagamento_MercadoPago", emoji=mercadopagoE),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Efí Bank", custom_id="GerenciarDefinicoesFormasPagamento_Efi", emoji=efibankE),
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Semi Automático", custom_id="GerenciarDefinicoesFormasPagamento_SemiAuto", emoji=recibo),
            ],
            [
                disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="Bloquear Bancos", custom_id="GerenciarPainelBancosBloqueados", emoji=banco),
                disnake.ui.Button(label="Documentação", custom_id="VerDocumentacaoFormasPagamento", emoji=fields),
                disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="GerenciarPainelConfigurar"),
            ]
        ]

        return embed, components

############################ BLOQUEAR BANCOS ############################
class BloquearBancos():
    def ObterPainelBloquearBancos(inter: disnake.MessageInteraction):
        with open("Database/Vendas/bancosbloqueados.json", encoding="utf-8") as vendasfile:
            vendasdb = json.load(vendasfile)

        bancos = vendasdb.get("bancosdisponiveis", [])
        bancos_bloqueados = vendasdb.get("bancosbloqueados", [])

        if not bancos:
            bancos = ["Nenhum banco disponível"]
        if not bancos_bloqueados:
            bancos_bloqueados = []

        desc = "\n".join(banco for banco in bancos_bloqueados) if bancos_bloqueados else "❌ Nenhum banco bloqueado"

        embed = disnake.Embed(
            title="Bloquear Bancos | Formas de Pagamento",
            description=f"Aqui você pode bloquear ou desbloquear bancos que não deseja aceitar pagamentos e editar as formas de pagamento que serão aceitas por ele.\n\n**Lista de Bancos Bloqueados**\n```\n{desc}\n```",
            timestamp=datetime.now(),
            color=disnake.Color(0x00FFFF)
        )
        embed.set_footer(text=inter.guild.name, icon_url=inter.guild.icon)

        options = []
        for banco in bancos:
            options.append(disnake.SelectOption(
                label=banco,
                value=banco,
                default=banco in bancos_bloqueados
            ))

        if not options:
            options = [disnake.SelectOption(label="Não disponível")]

        select = disnake.ui.StringSelect(
            custom_id="select_bancos_bloqueados",
            placeholder="🔒 Selecione os bancos para bloquear",
            options=options,
            disabled=not options,
            max_values=17 if options else 1,
            min_values=0
        )

        components = [
            select,
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelConfigurar_FormasPagamento"),
        ]

        return embed, components

    def registrar_remover_bancos(inter):
        with open("Database/Vendas/bancosbloqueados.json", encoding="utf-8") as vendasfile:
            vendasdb = json.load(vendasfile)

        bancos_bloqueados = set(vendasdb.get("bancosbloqueados", []))
        bancos_selecionados = set(inter.values) if inter.values else set()

        bancos_para_remover = bancos_bloqueados - bancos_selecionados
        bancos_para_adicionar = bancos_selecionados - bancos_bloqueados

        bancos_bloqueados.update(bancos_para_adicionar)
        bancos_bloqueados.difference_update(bancos_para_remover)

        vendasdb["bancosbloqueados"] = list(bancos_bloqueados)
        
        with open("Database/Vendas/bancosbloqueados.json", "w", encoding="utf-8") as vendasfile:
            json.dump(vendasdb, vendasfile, indent=4)

############################ INICIO ############################
class DefiniçõesCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def ConfigurarButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelConfigurar":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
 
            components = ObterComponentsPainelInicial()
            content = "O que precisa configurar?"
            await inter.edit_original_message(content=content, components=components)
        
        elif inter.component.custom_id.startswith("PainelConfigurar_"):
            tipo = inter.component.custom_id.replace("PainelConfigurar_", "")

            if tipo == "AntiFake":
                await inter.response.send_modal(AlterarAntiFakeModal())
                return

            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)

            if tipo == "Canais":
                embed, components = Canais.ObterMensagemCanais(inter)
            
            elif tipo == "Cargos":
                embed, components = Cargos.ObterMensagemCargos(inter)
            
            elif tipo == "FormasPagamento":
                embed, components = Pagamentos.ObterPainelFormasPagamento(inter)

            await inter.edit_original_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id.startswith("RemoverCanal_"):
            canal = inter.component.custom_id.replace("RemoverCanal_", "")
            await removerCanal(canal)
            embed, components = Canais.ObterMensagemCanais(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id.startswith("CriarCanal_"):
            canal = inter.component.custom_id.replace("CriarCanal_", "")
            novo_canal = await inter.guild.create_text_channel(name=canal.lower(), overwrites={
                inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False)
            })

            await novo_canal.send(f"||{inter.user.mention}|| `First! ;)`")
            
            canais = ObterCanais()
            canais[canal] = novo_canal.id
            salvarCanaisDatabase(canais)

            embed, components = Canais.ObterMensagemCanais(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)
        
        elif inter.component.custom_id.startswith("RemoverCargo_"):
            cargo = inter.component.custom_id.replace("RemoverCargo_", "")
            await removerCargo(cargo)
            embed, components = Cargos.ObterMensagemCargos(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id.startswith("CriarCargo_"):
            cargo = inter.component.custom_id.replace("CriarCargo_", "")
            
            if cargo == "administrador": 
                cargoNome = "Administrador"
                cargoColor = disnake.Colour(0x010101)

            elif cargo == "suporte": 
                cargoNome = "Suporte"
                cargoColor = disnake.Colour(0x00FFFF)

            elif cargo == "cliente": 
                cargoNome = "Cliente"
                cargoColor = disnake.Colour(0xFFFF00)

            elif cargo == "membro": 
                cargoNome = "Membro"
                cargoColor = disnake.Colour(0x00FF00)

            elif cargo == "verificado": 
                cargoNome = "Verificado"
                cargoColor = disnake.Colour(0x006400)

            novo_cargo = await inter.guild.create_role(
                reason=f"[Ease Bot] Configurar o cargo: {cargoNome}", 
                name=cargoNome, 
                hoist=True, 
                colour=cargoColor
            )

            await novo_cargo.edit(colour=cargoColor)

            cargos = ObterCargos()
            cargos[cargo] = novo_cargo.id
            salvarCargosDatabase(cargos)

            embed, components = Cargos.ObterMensagemCargos(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "VerDocumentacaoFormasPagamento":
            await inter.response.defer(ephemeral=True, with_message=True)
            mensagem = """
# Documentação | Formas de Pagamento
Esta documentação fornece uma visão geral das formas de pagamento que o bot pode utilizar. Cada forma de pagamento possui uma configuração independente, e a ordem de prioridade será seguida da seguinte maneira:
## Ordem de Prioridade:
1. **Mercado Pago**  
   Quando habilitado e configurado, o Mercado Pago será a forma de pagamento prioritária.
2. **Efi**  
   Caso o Mercado Pago não esteja habilitado ou configurado, o Efi será a segunda opção.
3. **Semi Auto**  
   Se nenhuma das opções anteriores estiver disponível, o Semi Auto será a última forma a ser utilizada.
    """
            await inter.followup.send(content=mensagem)

        elif inter.component.custom_id == "GerenciarPainelBancosBloqueados":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = BloquearBancos.ObterPainelBloquearBancos(inter)
            await inter.edit_original_message("", embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def ConfigurarDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "ConfigurarDropdown_Canais":
            canal_selecionado = inter.values[0]
            await Canais.GerenciarCanal(inter, canal_selecionado)

        elif inter.component.custom_id.startswith("AlterarCanal_"):
            canal_selecionado = inter.component.custom_id.replace("AlterarCanal_", "")
            novo_canal_id = inter.values[0]

            canais = ObterCanais()
            canais[canal_selecionado] = novo_canal_id
            salvarCanaisDatabase(canais)

            embed, components = Canais.ObterMensagemCanais(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "ConfigurarDropdown_Cargos":
            cargo_selecionado = inter.values[0]
            await Cargos.GerenciarCargo(inter, cargo_selecionado)

        elif inter.component.custom_id.startswith("AlterarCargo_"):
            cargo_selecionado = inter.component.custom_id.replace("AlterarCargo_", "")
            novo_cargo_id = inter.values[0]

            cargos = ObterCargos()
            cargos[cargo_selecionado] = novo_cargo_id
            salvarCargosDatabase(cargos)

            embed, components = Cargos.ObterMensagemCargos(inter)
            await inter.response.edit_message(content=None, embed=embed, components=components)

        elif inter.component.custom_id == "select_bancos_bloqueados":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            BloquearBancos.registrar_remover_bancos(inter)
            embed, components = BloquearBancos.ObterPainelBloquearBancos(inter)
            await inter.edit_original_message("", embed=embed, components=components)

def setup(bot: commands.Bot):
    bot.add_cog(DefiniçõesCommand(bot))