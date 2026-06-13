import discord
from discord import app_commands
import random
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

def tabela_bloqueio(resultado: int) -> int:
    if resultado <= 9:    return 0
    elif resultado <= 15: return 1
    elif resultado <= 18: return 2
    elif resultado <= 19: return 3
    else:                 return 4

def rolar_com_nivel(nivel: int) -> tuple[int, list[int], int]:
    if nivel == 0:
        dados = [random.randint(1, 20)]
        return max(dados), dados, 0
    elif nivel == 1:
        dados = [random.randint(1, 20), random.randint(1, 20)]
        return max(dados), dados, 0
    elif nivel == 2:
        dados = [random.randint(1, 20), random.randint(1, 20)]
        return max(dados), dados, 1
    elif nivel == 3:
        dados = [random.randint(1, 20), random.randint(1, 20)]
        return max(dados), dados, 2
    elif nivel == 4:
        dados = [random.randint(1, 20), random.randint(1, 20), random.randint(1, 20)]
        return max(dados), dados, 0
    else:
        dados = [random.randint(1, 20), random.randint(1, 20), random.randint(1, 20)]
        return max(dados), dados, 2

def desc_nivel(nivel: int) -> str:
    nomes = {
        0: "Nv0 - sem vantagem",
        1: "Nv1 - 2 dados, maior",
        2: "Nv2 - 2 dados, maior +1",
        3: "Nv3 - 2 dados, maior +2",
        4: "Nv4 - 3 dados, maior",
        5: "Nv5 - 3 dados, maior +2",
    }
    return nomes.get(nivel, "Nv0")

def emoji_dados(dados: list[int]) -> str:
    return " | ".join([f"`{d}`" for d in dados])

def rolar_dado_dano(expr: str) -> tuple[int, str]:
    expr = expr.strip().lower()
    if "d" not in expr:
        return int(expr), expr
    partes = expr.split("d")
    qtd = int(partes[0]) if partes[0] else 1
    faces = int(partes[1])
    resultados = [random.randint(1, faces) for _ in range(qtd)]
    return sum(resultados), " + ".join([str(r) for r in resultados])

class BatalhaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Ataque Fisico", style=discord.ButtonStyle.red, row=0)
    async def ataque(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AtaqueModal())

    @discord.ui.button(label="Habilidade Magica", style=discord.ButtonStyle.blurple, row=0)
    async def magia(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MagiaModal())

    @discord.ui.button(label="Ritual", style=discord.ButtonStyle.grey, row=0)
    async def ritual(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RitualModal())

    @discord.ui.button(label="Esquivar", style=discord.ButtonStyle.green, row=1)
    async def esquivar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EsquivarModal())

    @discord.ui.button(label="Bloquear", style=discord.ButtonStyle.blurple, row=1)
    async def bloquear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BloquearModal())

class AtaqueModal(discord.ui.Modal, title="Ataque Fisico"):
    bonus = discord.ui.TextInput(label="Bonus de ataque (Prof + Atributo)", placeholder="Ex: 6", required=True)
    nivel = discord.ui.TextInput(label="Nivel de treino na pericia (0 a 5)", placeholder="Ex: 2", required=True)
    defesa = discord.ui.TextInput(label="Defesa do alvo", placeholder="Ex: 14", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            nivel_val = int(self.nivel.value)
            defesa_val = int(self.defesa.value)
            if not (0 <= nivel_val <= 5):
                await interaction.response.send_message("Nivel deve ser entre 0 e 5!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Digite apenas numeros!", ephemeral=True)
            return

        base, dados, bonus_nivel = rolar_com_nivel(nivel_val)
        total = base + bonus_nivel + bonus_val
        acertou = total >= defesa_val
        critico = 20 in dados
        falha_critica = all(d == 1 for d in dados)

        calculo = f"`{base}` (dado)"
        if bonus_nivel > 0:
            calculo += f" + `{bonus_nivel}` (treino Nv{nivel_val})"
        calculo += f" + `{bonus_val}` (bonus) = **{total}**"

        if falha_critica:
            cor = discord.Color.dark_red()
            resultado = "FALHA CRITICA! Voce errou e o inimigo tem direito a um CONTRA-ATAQUE garantido!"
        elif critico:
            cor = discord.Color.gold()
            resultado = "CRITICO! Multiplique o dano pelo multiplicador de critico da sua arma!"
        elif acertou:
            cor = discord.Color.orange()
            resultado = "ACERTO! Role o dado de dano da sua arma."
        else:
            cor = discord.Color.greyple()
            resultado = "ERROU! Seu ataque nao superou a defesa do alvo."

        embed = discord.Embed(title="Ataque Fisico", color=cor)
        embed.add_field(name="Dados rolados", value=emoji_dados(dados), inline=False)
        embed.add_field(name="Treino", value=desc_nivel(nivel_val), inline=True)
        embed.add_field(name="Defesa do alvo", value=f"`{defesa_val}`", inline=True)
        embed.add_field(name="Calculo", value=calculo, inline=False)
        embed.add_field(name="Resultado", value=resultado, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

class MagiaModal(discord.ui.Modal, title="Habilidade Magica"):
    bonus = discord.ui.TextInput(label="Bonus em Poder (Prof + MAG)", placeholder="Ex: 5", required=True)
    nivel = discord.ui.TextInput(label="Nivel de treino em Poder (0 a 5)", placeholder="Ex: 1", required=True)
    energia = discord.ui.TextInput(label="Custo de energia da habilidade", placeholder="Ex: 3", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            nivel_val = int(self.nivel.value)
            energia_val = int(self.energia.value)
            if not (0 <= nivel_val <= 5):
                await interaction.response.send_message("Nivel deve ser entre 0 e 5!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Digite apenas numeros!", ephemeral=True)
            return

        base, dados, bonus_nivel = rolar_com_nivel(nivel_val)
        total = base + bonus_nivel + bonus_val
        DIFICULDADE = 12
        sucesso = total >= DIFICULDADE
        critico = 20 in dados
        falha_critica = all(d == 1 for d in dados)

        calculo = f"`{base}` (dado)"
        if bonus_nivel > 0:
            calculo += f" + `{bonus_nivel}` (treino Nv{nivel_val})"
        calculo += f" + `{bonus_val}` (bonus) = **{total}** vs dificuldade `{DIFICULDADE}`"

        if falha_critica:
            cor = discord.Color.dark_red()
            resultado = "FALHA CRITICA! A habilidade falhou e voce ficou Atordoado por 1 turno! Gasta a energia mesmo assim."
        elif critico:
            cor = discord.Color.gold()
            resultado = f"CRITICO! Habilidade conjurada com sucesso! O efeito e multiplicado por 2!\nGasta {energia_val} de energia."
        elif sucesso:
            cor = discord.Color.purple()
            resultado = f"SUCESSO! Habilidade conjurada!\nGasta {energia_val} de energia."
        else:
            cor = discord.Color.dark_grey()
            resultado = f"FALHOU! A conjuracao falhou. Voce perde sua acao principal.\nGasta {energia_val} de energia mesmo assim."

        embed = discord.Embed(title="Habilidade Magica - Poder + MAG", color=cor)
        embed.add_field(name="Dados rolados", value=emoji_dados(dados), inline=False)
        embed.add_field(name="Treino", value=desc_nivel(nivel_val), inline=True)
        embed.add_field(name="Dificuldade", value="`12`", inline=True)
        embed.add_field(name="Calculo", value=calculo, inline=False)
        embed.add_field(name="Resultado", value=resultado, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

class RitualModal(discord.ui.Modal, title="Ritual Espectrum"):
    bonus = discord.ui.TextInput(label="Bonus em Ocultismo (Prof + MAG)", placeholder="Ex: 7", required=True)
    nivel = discord.ui.TextInput(label="Nivel de treino em Ocultismo (0 a 5)", placeholder="Ex: 3", required=True)
    energia = discord.ui.TextInput(label="Custo de energia do ritual", placeholder="Ex: 5", required=True)
    falha_teste = discord.ui.TextInput(
        label="Falha Teste do ritual (ex: 1d4 ou 1/1d4)",
        placeholder="1d4 = so falha | 1/1d4 = falha e sucesso",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            nivel_val = int(self.nivel.value)
            energia_val = int(self.energia.value)
            falha_str = self.falha_teste.value.strip()
            if not (0 <= nivel_val <= 5):
                await interaction.response.send_message("Nivel deve ser entre 0 e 5!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Digite apenas numeros nos campos numericos!", ephemeral=True)
            return

        base, dados, bonus_nivel = rolar_com_nivel(nivel_val)
        total = base + bonus_nivel + bonus_val
        DIFICULDADE = 12
        sucesso_teste = total >= DIFICULDADE
        critico = 20 in dados
        falha_critica = all(d == 1 for d in dados)

        tem_dano_sucesso = "/" in falha_str
        if tem_dano_sucesso:
            partes = falha_str.split("/")
            dano_sucesso_expr = partes[0].strip()
            dano_falha_expr = partes[1].strip()
        else:
            dano_sucesso_expr = None
            dano_falha_expr = falha_str

        calculo = f"`{base}` (dado)"
        if bonus_nivel > 0:
            calculo += f" + `{bonus_nivel}` (treino Nv{nivel_val})"
        calculo += f" + `{bonus_val}` (bonus) = **{total}** vs dificuldade `{DIFICULDADE}`"

        if falha_critica:
            try:
                partes_dado = dano_falha_expr.lower().split("d")
                dano_max = int(partes_dado[0]) * int(partes_dado[1])
            except:
                dano_max = 0
            cor = discord.Color.dark_red()
            resultado = (
                f"O ritual E BEM SUCEDIDO!\n"
                f"FALHA CRITICA no teste! Voce toma {dano_max} de dano psicologico (maximo)!\n"
                f"Gasta {energia_val} de energia."
            )
        elif critico:
            cor = discord.Color.gold()
            dano_sucesso_txt = ""
            if tem_dano_sucesso:
                ds, ds_desc = rolar_dado_dano(dano_sucesso_expr)
                dano_sucesso_txt = f"\nDano psicologico de sucesso: {ds_desc} = {ds}"
            resultado = f"CRITICO! O ritual E BEM SUCEDIDO com efeito multiplicado por 2!{dano_sucesso_txt}\nGasta {energia_val} de energia."
        elif sucesso_teste:
            cor = discord.Color.purple()
            dano_sucesso_txt = ""
            if tem_dano_sucesso:
                ds, ds_desc = rolar_dado_dano(dano_sucesso_expr)
                dano_sucesso_txt = f"\nDano psicologico de sucesso: {ds_desc} = {ds}"
            resultado = f"SUCESSO! O ritual E BEM SUCEDIDO!{dano_sucesso_txt}\nGasta {energia_val} de energia."
        else:
            df, df_desc = rolar_dado_dano(dano_falha_expr)
            cor = discord.Color.dark_orange()
            dano_sucesso_txt = ""
            if tem_dano_sucesso:
                ds, ds_desc = rolar_dado_dano(dano_sucesso_expr)
                dano_sucesso_txt = f"\nDano psicologico de sucesso: {ds_desc} = {ds}"
            resultado = f"O ritual E BEM SUCEDIDO mesmo com falha no teste!\nDano psicologico de falha: {df_desc} = {df}{dano_sucesso_txt}\nGasta {energia_val} de energia."

        embed = discord.Embed(title="Ritual - Ocultismo + MAG", color=cor)
        embed.add_field(name="Dados rolados", value=emoji_dados(dados), inline=False)
        embed.add_field(name="Treino", value=desc_nivel(nivel_val), inline=True)
        embed.add_field(name="Dificuldade", value="`12`", inline=True)
        embed.add_field(name="Calculo", value=calculo, inline=False)
        embed.add_field(name="Resultado", value=resultado, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

class EsquivarModal(discord.ui.Modal, title="Esquivar"):
    bonus = discord.ui.TextInput(label="Bonus em Reflexo (Prof + AGI)", placeholder="Ex: 5", required=True)
    nivel = discord.ui.TextInput(label="Nivel de treino em Reflexo (0 a 5)", placeholder="Ex: 2", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            nivel_val = int(self.nivel.value)
            if not (0 <= nivel_val <= 5):
                await interaction.response.send_message("Nivel deve ser entre 0 e 5!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Digite apenas numeros!", ephemeral=True)
            return

        base, dados, bonus_nivel = rolar_com_nivel(nivel_val)
        total = base + bonus_nivel + bonus_val
        critico = 20 in dados
        falha_critica = all(d == 1 for d in dados)

        calculo = f"`{base}` (dado)"
        if bonus_nivel > 0:
            calculo += f" + `{bonus_nivel}` (treino Nv{nivel_val})"
        calculo += f" + `{bonus_val}` (bonus) = **{total}**"

        if falha_critica:
            cor = discord.Color.dark_red()
            status = "FALHA CRITICA! Voce nao esquivou e o inimigo ganha um CONTRA-ATAQUE garantido!"
        elif critico:
            cor = discord.Color.gold()
            status = "CRITICO! Esquiva perfeita - voce tem direito a um CONTRA-ATAQUE!"
        else:
            cor = discord.Color.green()
            status = "Compare com o ataque do inimigo.\nSe seu total for MAIOR - esquiva + CONTRA-ATAQUE!"

        embed = discord.Embed(title="Esquiva - Reflexo + AGI", color=cor)
        embed.add_field(name="Dados rolados", value=emoji_dados(dados), inline=False)
        embed.add_field(name="Treino", value=desc_nivel(nivel_val), inline=True)
        embed.add_field(name="Calculo", value=calculo, inline=False)
        embed.add_field(name="Resultado", value=status, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

class BloquearModal(discord.ui.Modal, title="Bloquear"):
    bonus = discord.ui.TextInput(label="Bonus em Constituicao (Prof + VIG)", placeholder="Ex: 7", required=True)
    nivel = discord.ui.TextInput(label="Nivel de treino em Constituicao (0 a 5)", placeholder="Ex: 1", required=True)
    armadura = discord.ui.TextInput(label="Bonus de armadura/escudo (0 se nao tiver)", placeholder="Ex: 2", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            nivel_val = int(self.nivel.value)
            armadura_val = int(self.armadura.value)
            if not (0 <= nivel_val <= 5):
                await interaction.response.send_message("Nivel deve ser entre 0 e 5!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Digite apenas numeros!", ephemeral=True)
            return

        base, dados, bonus_nivel = rolar_com_nivel(nivel_val)
        total = base + bonus_nivel + bonus_val
        bloqueio_dado = tabela_bloqueio(total)
        bloqueio_total = bloqueio_dado + armadura_val
        critico = 20 in dados
        falha_critica = all(d == 1 for d in dados)

        calculo = f"`{base}` (dado)"
        if bonus_nivel > 0:
            calculo += f" + `{bonus_nivel}` (treino Nv{nivel_val})"
        calculo += f" + `{bonus_val}` (bonus) = **{total}**"

        if falha_critica:
            cor = discord.Color.dark_red()
            obs = "FALHA CRITICA! Voce nao bloqueou nada."
        elif critico:
            cor = discord.Color.gold()
            obs = "CRITICO! Bloqueio maximo!"
        else:
            cor = discord.Color.blue()
            obs = ""

        embed = discord.Embed(title="Bloqueio - Constituicao + VIG", color=cor)
        embed.add_field(name="Dados rolados", value=emoji_dados(dados), inline=False)
        embed.add_field(name="Treino", value=desc_nivel(nivel_val), inline=True)
        embed.add_field(name="Calculo", value=calculo, inline=False)
        embed.add_field(name="Bloqueio pelo dado", value=f"`{bloqueio_dado}` ponto(s)", inline=True)
        embed.add_field(name="Bonus armadura/escudo", value=f"`+{armadura_val}` ponto(s)", inline=True)
        embed.add_field(name="Total Bloqueado", value=f"**{bloqueio_total} ponto(s) de dano**", inline=False)
        if obs:
            embed.add_field(name="Atencao", value=obs, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

@tree.command(name="batalha", description="Abre o painel de batalha do RPG Uniao dos Guerreiros")
async def batalha(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Painel de Batalha - Uniao dos Guerreiros",
        description="Escolha sua acao:",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="Ataque Fisico", value="Pericia + Atributo vs Defesa", inline=True)
    embed.add_field(name="Habilidade Magica", value="Poder + MAG vs dificuldade 12", inline=True)
    embed.add_field(name="Ritual", value="Ocultismo + MAG vs dificuldade 12", inline=True)
    embed.add_field(name="Esquivar", value="Reflexo + AGI vs ataque do inimigo", inline=True)
    embed.add_field(name="Bloquear", value="Constituicao + VIG - reduz dano", inline=True)
    embed.set_footer(text="Clique no botao da acao desejada!")
    await interaction.response.send_message(embed=embed, view=BatalhaView())

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot de Batalha {bot.user} online - Comandos sincronizados!")

bot.run(TOKEN)
    
