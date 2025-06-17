import disnake
import re
import requests
from disnake import *
from disnake.ext import commands
from datetime import *
from Functions.CarregarEmojis import *
from Functions.VerificarPerms import *
import asyncio

def ObterDatabase():
    with open("Database/Auth/oauth.json") as f:
        return json.load(f)

def ObterPainelPrincipal(inter: disnake.MessageInteraction):
    db = ObterDatabase()
    if db["url"] and db["authorization"]:
        try:
            url = f"{db["url"]}/verifyKey"
            headers = {
                "authorization": db["authorization"]
            }
            response = requests.get(url=url, headers=headers)

            if response.status_code == 200: verificada = True
            else: verificada = False

        except: verificada = False

        try:
            url = f"{db["url"]}/members"
            headers = {
                "authorization": db["authorization"]
            }

            response = requests.get(url=url, headers=headers)
            if response.status_code == 200: members = response.json()["message"]
            else: members = " - "

        except: members = " - "
    else:
        verificada = False
        members = " - "
    
    if db["url"]: url = f"{positivo} `{db["url"]}`"
    else: url = f"{negativo} `Não configurado`"

    with open("Database/Server/cargos.json") as f:
        cargos = json.load(f)

    embed = disnake.Embed(
        title="Meu eCloud Drive",
        description="Utilize este painel para gerenciar/configurar o OAuth2.\nUtilize as funções abaixo para fazer a personalização/configuração do seu painel.\n**Lembre-se**: É preciso ter um `Ease Auth Website`. Para mais detalhes, utilize o tutorial disponibilizado.",
        color=disnake.Color(0x00FFFF),
        timestamp=datetime.now()
    )
    embed.set_footer(text=inter.guild.name, icon_url="https://cdn.discordapp.com/attachments/1327815504865398854/1337943760490860554/discotools-xyz-icon_6.png?ex=67a948ba&is=67a7f73a&hm=33667c5f8fab6b56e15506facc40b28372a23a06872f3840921b9553643a7120&")

    embed.add_field(
        name=f"{cloud} Seu Bot OAuth2",
        value=f"{f"{positivo} `Configurado`" if verificada else f"{negativo} `Não configurado`"}",
        inline=True
    )
    embed.add_field(
        name=f"{users} Membros OAuth2",
        value=f"`{members}`",
        inline=True
    )
    embed.add_field(
        name=f"{cargo} Cargo de verificado",
        value=f"{f"<@&{cargos["verificado"]}>" if cargos["verificado"] else f"{negativo} `Não configurado`"}"
    )
    embed.add_field(
        name=f"{rotas} URL configurada",
        value=f"{url}",
        inline=False
    )

    components = [
        [
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="Personalizar Mensagem",
                custom_id="CustomizarMensagemOAuth2",
                emoji=mensagem
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Configurar OAuth2",
                custom_id="ConfigurarOAuth2",
                emoji=editar
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                label="Recuperar Membros",
                custom_id="RecuperarMembrosOAuth2",
                emoji=reload
            ),
        ],
        [
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="Enviar Mensagem",
                custom_id="EnviarMensagemOAuth2",
                emoji=arrow
            ),
            disnake.ui.Button(
                label="Configurar permissões dos membros",
                emoji=config3,
                custom_id="ConfigurarSistemaOAuth2"
            ),
        ],
        [
            disnake.ui.Button(
                label="Tutorial",
                emoji=attach,
                url="https://www.youtube.com/watch?v=7nWN0BWWucQ"
            ),
            disnake.ui.Button(
                label="Repositório",
                emoji=diretorio,
                url="https://github.com/gozeinasuacara/api"
            ),
            disnake.ui.Button(label="Voltar", emoji=voltar, custom_id="PainelInicial"),
        ]
    ]

    return embed, components

def ObterMensagemOAuth(inter: disnake.MessageInteraction):
    db = ObterDatabase()
    with open("Database/Server/cargos.json", "r", encoding="utf-8") as f:
        cargos = json.load(f)

    if not db.get("clientSecret") and not db.get("url") and not db.get("authorization") and not cargos.get("verificado"):
        return False

    content = db.get("mensagem", {}).get("content")
    if content == "":
        content = None

    embed_config = db.get("mensagem", {}).get("embed", {})

    title = embed_config.get("title") or None
    if not title:
        title = None

    description = embed_config.get("desc") if embed_config.get("desc") != "" else None

    color_str = embed_config.get("color")
    if color_str and color_str != "":
        try:
            if color_str.startswith("0x"):
                color_value = int(color_str, 16)
            elif color_str.startswith("#"):
                color_value = int(color_str[1:], 16)
            else:
                color_value = int(color_str)
        except Exception:
            color_value = 0x00FFFF
    else:
        color_value = 0x00FFFF

    if title and description and color_value:
        embed = disnake.Embed(
            title=title,
            description=description,
            color=color_value,
            timestamp=datetime.now()
        )

        iconURL = embed_config.get("iconURL")
        if iconURL == "":
            iconURL = None
        if iconURL:
            embed.set_thumbnail(url=iconURL)

        bannerURL = embed_config.get("bannerURL")
        if bannerURL == "":
            bannerURL = None
        if bannerURL:
            embed.set_image(url=bannerURL)
    else: embed = None
    return content, embed

def puxar_membros(id):
    db = ObterDatabase()
    response = requests.post(
        url=f"{db['url']}/pullmembers/1",
        headers={"Authorization": db['authorization']},
        json={"guildID": id}
    )

class Personalizar():
    class PersonalizarEmbed(disnake.ui.Modal):
        def __init__(self):
            with open("Database/Auth/oauth.json") as f:
                oauth = json.load(f)
                name = oauth["mensagem"]["embed"]["title"]
                desc = oauth["mensagem"]["embed"]["desc"]
                color = oauth["mensagem"]["embed"]["color"]
                iconURL = oauth["mensagem"]["embed"]["iconURL"]
                bannerURL = oauth["mensagem"]["embed"]["bannerURL"]

            components = [
                disnake.ui.TextInput(
                    label="Título da Embed",
                    custom_id="title",
                    value=name,
                    style=TextInputStyle.short,
                    required=False
                ),
                disnake.ui.TextInput(
                    label="Descrição da Embed",
                    custom_id="desc",
                    required=False,
                    style=TextInputStyle.long,
                    value=desc
                ),
                disnake.ui.TextInput(
                    label="Cor da Embed (HEX COM #)",
                    custom_id="color",
                    required=False,
                    max_length=7,
                    style=TextInputStyle.short,
                    value=color
                ),
                disnake.ui.TextInput(
                    label="URL da Imagem",
                    custom_id="image",
                    required=False,
                    style=TextInputStyle.short,
                    value=iconURL
                ),
                disnake.ui.TextInput(
                    label="URL do Banner",
                    custom_id="banner",
                    required=False,
                    style=TextInputStyle.short,
                    value=bannerURL
                ),
            ]
            super().__init__(title="Personalizar OAuth2", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            db = ObterDatabase()
            hex = inter.text_values["color"] or None
            title = inter.text_values["title"] or None
            desc = inter.text_values["desc"] or None
            image = inter.text_values["image"] or None
            banner = inter.text_values["banner"] or None

            def verificar_hex(cor: str) -> str | None:
                if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", cor):
                    return None
                return "#" + cor[1:].upper()

            if hex:
                hex_formatado = verificar_hex(hex)
                if not hex_formatado:
                    await inter.response.send_message(
                        f"{negativo} O código hexadecimal fornecido é inválido. Use um formato como `#RRGGBB` ou `#RGB`.",
                        ephemeral=True
                    )
                    return
                hex = hex_formatado
            
            db["mensagem"]["embed"]["title"] = title
            db["mensagem"]["embed"]["color"] = hex
            db["mensagem"]["embed"]["desc"] = desc
            db["mensagem"]["embed"]["image"] = image
            db["mensagem"]["embed"]["banner"] = banner

            with open("Database/Auth/oauth.json", "w") as f:
                json.dump(db, f, indent=4)

            await inter.response.edit_message(f"{positivo} Informações alteradas com sucesso!", components=None)
    
    class PersonalizarMensagem(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="Conteúdo da mensagem",
                    custom_id="name",
                    style=TextInputStyle.long,
                    required=False
                ),
            ]
            super().__init__(title="Personalizar OAuth2", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            db = ObterDatabase()
            db["mensagem"]["content"] = inter.text_values["name"]

            with open("Database/Auth/oauth.json", "w") as f:
                json.dump(db, f, indent=4)
            
            await inter.response.edit_message(f"{positivo} Informações alteradas com sucesso!", components=None)

    def ObterComponentsPersonalizar():
        components = [
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="Personalizar Mensagem",
                custom_id="PersonalizarOAuth2_Mensagem",
                emoji=mensagem
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="Personalizar Embed",
                custom_id="PersonalizarOAuth2_Embed",
                emoji=embedE
            ),
        ]
        return components

class Configurar():
    def VerificarWebsite(url: str, authorization: str):
        try:
            headers = {
                "authorization": authorization
            }

            response1 = requests.get(url=url, headers=headers)
            if not response1.status_code == 200 and not response1.json()["message"] == "EaseAPI_Website":
                return False
            
            response2 = requests.get(url=f"{url}/verifyKey", headers=headers)
            if not response2.status_code == 200:
                return False
            
            return True
        except: return False

    def RegistrarCallback(url: str, token: str):
            
            headers = { "Authorization": f"Bot {token}" }
            response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
            if response.status_code != 200: return False
            data = response.json()
            bot_id = data["id"]

            response2 = requests.get(f"https://discord.com/api/v9/applications/{bot_id}", headers=headers)
            if response2.status_code != 200: 
                return False

            redirect_urls = response2.json()["redirect_uris"] # ["url1", "url2", ...]
            redirect_urls.append(f"{url}auth/callback") # https://seuurl.squareweb.app/auth/callback

            response3 = requests.patch(f"https://discord.com/api/v9/applications/{bot_id}", headers=headers, json={
                "redirect_uris": redirect_urls,
                "flags": 19439872,
                "rpc_origins": []
            })
            if response3.status_code != 200: return False

            return True

    class PuxarMembrosModal(disnake.ui.Modal):
        def __init__(self):
            components = [
                disnake.ui.TextInput(
                    label="ID do Servidor",
                    custom_id="id",
                    style=TextInputStyle.short,
                ),
            ]
            super().__init__(title="Personalizar OAuth2", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            id = inter.text_values["id"]
            try:
              int(id)
            except:
                return await inter.response.send_message(f"{negativo} O bot não está no servidor.",
                ephemeral=True,
                components=[
                    disnake.ui.Button(
                        label="Adicionar",
                        url=f"https://discord.com/api/oauth2/authorize?client_id={inter.bot.id}&permissions=8&scope=bot"
                    )
                ])
              
            if not inter.bot.get_guild(int(id)):
                return await inter.response.send_message(f"{negativo} O bot não está no servidor.",
                ephemeral=True,
                components=[
                    disnake.ui.Button(
                        label="Adicionar",
                        url=f"https://discord.com/api/oauth2/authorize?client_id={inter.bot.id}&permissions=8&scope=bot"
                    )
                ])

            await inter.response.send_message(f"{carregarAnimado} Aguarde um momento...", ephemeral=True)
            db = ObterDatabase()
            with open("Database/Server/cargos.json") as f:
                cargos = json.load(f)
            if db["clientSecret"] == "" or db["url"] == "" or db["authorization"] == "" or cargos["verificado"] == "":
                return await inter.edit_original_message(f"{negativo} Você precisa configurar seu eAuth primeiro!")
            
            await inter.edit_original_message(f"{carregarAnimado} O processo de puxar membros foi iniciado.\n`❓` O processo pode demorar conforme a quantiade de membros.")

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, puxar_membros, id)

            await inter.edit_original_message(f"{positivo} Membros puxados com sucesso!")

    class ConfigurarAuthModal(disnake.ui.Modal):
        def __init__(self):
            db = ObterDatabase()
            components = [
                disnake.ui.TextInput(
                    label="Client Secret",
                    custom_id="secret",
                    value=f"{db["clientSecret"]}",
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="URL da API",
                    placeholder="https://",
                    value=f"{db["url"]}",
                    custom_id="url",
                    style=TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="Autorização",
                    value=f"{db["authorization"]}",
                    custom_id="authorization",
                    style=TextInputStyle.paragraph,
                ),
            ]
            super().__init__(title="Configurar OAuth2", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.edit_message(f"{carregarAnimado} Aguarde um momento", embed=None, components=None)
            secret = inter.text_values["secret"]
            url = inter.text_values["url"]
            if not url.endswith("/"): url = url+"/"
            authorization = inter.text_values["authorization"]
            
            status = Configurar.VerificarWebsite(url, authorization)

            if not status:
                embed, components = ObterPainelPrincipal(inter)
                await inter.edit_original_message("", embed=embed, components=components)
                return await inter.followup.send(f"{negativo} Os dados informados estão errados", ephemeral=True)

            with open("Database/Server/cargos.json") as f:
                cargos = json.load(f)

            if not cargos["verificado"]:
                embed, components = ObterPainelPrincipal(inter)
                await inter.edit_original_message("", embed=embed, components=components)
                return await inter.followup.send(f"{negativo} Você precisa configurar o cargo de verificado primeiro.", ephemeral=True)

            with open("config.json") as f:
                config = json.load(f)

            headers = { "authorization": authorization }
            payload = {
                "clientid": f"{inter.bot.user.id}",
                "secret": secret,
                "url": url,
                "guild_id": f"{inter.guild.id}",
                "role": cargos["verificado"],
                "token": config["token"]
            }
            response = requests.post(url=f"{url}/config", headers=headers, json=payload)
            if not response.status_code == 200:
                embed, components = ObterPainelPrincipal(inter)
                await inter.edit_original_message("", embed=embed, components=components)
                return await inter.followup.send(f"{negativo} Não foi possível salvar as informações na API", ephemeral=True)

            Configurar.RegistrarCallback(url, config["token"]) # não funcionando!!!

            db = ObterDatabase()
            db["clientSecret"] = secret
            db["url"] = url
            db["authorization"] = authorization

            with open("Database/Auth/oauth.json", "w") as f:
                json.dump(db, f, indent=4)
            
            embed, components = ObterPainelPrincipal(inter)
            await inter.edit_original_message("", embed=embed, components=components)

class ECloudCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def ECloudButtonListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "GerenciarPainelECloud":
            await inter.response.edit_message(f"{carregarAnimado} Carregando informações", embed=None, components=None)
            embed, components = ObterPainelPrincipal(inter)
            await inter.edit_original_message("", embed=embed, components=components)

        elif inter.component.custom_id == "CustomizarMensagemOAuth2":
            await inter.response.defer(with_message=True, ephemeral=True)
            components = Personalizar.ObterComponentsPersonalizar()
            await inter.followup.send(components=components)
        
        elif inter.component.custom_id == "ConfigurarOAuth2":
            await inter.response.send_modal(Configurar.ConfigurarAuthModal())
        
        elif inter.component.custom_id == "PersonalizarOAuth2_Mensagem":
            await inter.response.send_modal(Personalizar.PersonalizarMensagem())
        
        elif inter.component.custom_id == "PersonalizarOAuth2_Embed":
            await inter.response.send_modal(Personalizar.PersonalizarEmbed())

        elif inter.component.custom_id == "VerificarOAuth2":
            await inter.response.send_message(f"{carregarAnimado} Aguarde enquanto carrego as informações.", ephemeral=True)
            db = ObterDatabase()

            try:
                response = requests.get(url=f"{db["url"]}login")
                if not response.json()["authUrl"]:
                    return await inter.edit_original_message(f"{negativo} O site não está configurado corretamente.")
                
                components = [
                    disnake.ui.Button(
                        label="Verificar",
                        url=response.json()["authUrl"]
                    )
                ]

                await inter.edit_original_message("Prossiga com sua verificação, clique no botão abaixo.", components=components)

            except:
                return await inter.edit_original_message(f"{negativo} O site não está configurado corretamente.")  

        elif inter.component.custom_id == "EnviarMensagemOAuth2":
            dropdown = disnake.ui.ChannelSelect(
                placeholder="Selecione o canal desejado",
                custom_id="EnviarDropdownMensagemOAuth2",
                channel_types=[ChannelType.text]
            )
            await inter.response.send_message(components=dropdown, ephemeral=True)
    
        elif inter.component.custom_id == "RecuperarMembrosOAuth2":
            await inter.response.send_modal(Configurar.PuxarMembrosModal())


    @commands.Cog.listener("on_dropdown")
    async def ECloudDropdownListener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "EnviarDropdownMensagemOAuth2":
            await inter.response.edit_message(f"{carregarAnimado} Aguarde um momento.", components=None)

            db = ObterDatabase()
            with open("Database/Server/cargos.json") as f:
                cargos = json.load(f)
            if db["clientSecret"] == "" or db["url"] == "" or db["authorization"] == "" or cargos["verificado"] == "":
                return await inter.edit_original_message(f"{negativo} Você precisa configurar seu eAuth primeiro!")

            try:
                channel = inter.guild.get_channel(int(inter.values[0]))
                resultado = ObterMensagemOAuth(inter)
                if not resultado:
                    await inter.edit_original_message(
                        f"{negativo} Configurações inválidas para gerar a mensagem OAuth.",
                    )
                    return

                content, embed = resultado

                components = [
                    disnake.ui.Button(
                        label="Verificar",
                        emoji="<:check:1362202428174368938>", # emoji de verificar dahorinha
                        custom_id="VerificarOAuth2",
                        style=disnake.ButtonStyle.blurple
                    )
                ]

                msg = await channel.send(content=content, embed=embed, components=components)
                await inter.edit_original_message(f"{positivo} Enviei a mensagem: {msg.jump_url}")
            except Exception as e:
                await inter.edit_original_message(f"{negativo} Um erro ocorreu ao tentar executar a ação:\n```{e}```")
                return

def setup(bot: commands.Bot):
    bot.add_cog(ECloudCommand(bot))