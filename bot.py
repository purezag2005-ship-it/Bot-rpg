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

# ── TABELA DE BLOQUEIO ────────────────────────────────────────────────────────
def tabela_bloqueio(resultado: int) -> int:
    if resultado <= 9:   return 0
    elif resultado <= 15: return 1
    elif resultado <= 18: return 2
    elif resultado <= 19: return 3
    else:                 return 4

# ── VIEW COM BOTÕES ───────────────────────────────────────────────────────────
class BatalhaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="💨 Esquivar", style=discord.ButtonStyle.green)
    async def esquivar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EsquivarModal())

    @discord.ui.button(label="🛡️ Bloquear", style=discord.ButtonStyle.blurple)
    async def bloquear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BloquearModal())

# ── MODAL: ESQUIVAR ───────────────────────────────────────────────────────────
class EsquivarModal(discord.ui.Modal, title="💨 Esquivar"):
    bonus = discord.ui.TextInput(
        label="Bônus total em Reflexo (Prof + AGI)",
        placeholder="Ex: 5  →  significa que você soma +5 no d20",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
        except ValueError:
            await interaction.response.send_message("❌ Digite apenas números!", ephemeral=True)
            return

        dado = random.randint(1, 20)
        total = dado + bonus_val

        # Crítico e falha crítica
        if dado == 20:
            status = "✨ **CRÍTICO!** Esquiva perfeita — você tem direito a um **CONTRA-ATAQUE**!"
            cor = discord.Color.gold()
        elif dado == 1:
            status = "💀 **FALHA CRÍTICA!** Você não conseguiu esquivar e o inimigo ganha um **CONTRA-ATAQUE** garantido!"
            cor = discord.Color.dark_red()
        else:
            status = "🎯 Resultado obtido! Compare com o teste de ataque do inimigo.\nSe o seu total for **MAIOR** que o dele → esquiva bem-sucedida + **CONTRA-ATAQUE**!"
            cor = discord.Color.green()

        embed = discord.Embed(title="💨 Esquiva — Reflexo + AGI", color=cor)
        embed.add_field(name="🎲 Dado (d20)", value=f"`{dado}`", inline=True)
        embed.add_field(name="➕ Bônus", value=f"`+{bonus_val}`", inline=True)
        embed.add_field(name="📊 Total", value=f"**{total}**", inline=True)
        embed.add_field(name="📋 Resultado", value=status, inline=False)
        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

# ── MODAL: BLOQUEAR ───────────────────────────────────────────────────────────
class BloquearModal(discord.ui.Modal, title="🛡️ Bloquear"):
    bonus = discord.ui.TextInput(
        label="Bônus total em Constituição (Prof + VIG)",
        placeholder="Ex: 7  →  significa que você soma +7 no d20",
        required=True
    )
    armadura = discord.ui.TextInput(
        label="Bônus de armadura/escudo (0 se não tiver)",
        placeholder="Ex: 2 (escudo) | 0 (sem armadura)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bonus_val = int(self.bonus.value)
            armadura_val = int(self.armadura.value)
        except ValueError:
            await interaction.response.send_message("❌ Digite apenas números!", ephemeral=True)
            return

        dado = random.randint(1, 20)
        total = dado + bonus_val
        bloqueio_dado = tabela_bloqueio(total)
        bloqueio_total = bloqueio_dado + armadura_val

        # Crítico e falha crítica
        if dado == 20:
            cor = discord.Color.gold()
            obs = "✨ **CRÍTICO!** Bloqueio máximo!"
        elif dado == 1:
            cor = discord.Color.dark_red()
            obs = "💀 **FALHA CRÍTICA!** Você não conseguiu bloquear nada."
        else:
            cor = discord.Color.blue()
            obs = ""

        embed = discord.Embed(title="🛡️ Bloqueio — Constituição + VIG", color=cor)
        embed.add_field(name="🎲 Dado (d20)", value=f"`{dado}`", inline=True)
        embed.add_field(name="➕ Bônus", value=f"`+{bonus_val}`", inline=True)
        embed.add_field(name="📊 Total no dado", value=f"**{total}**", inline=True)
        embed.add_field(name="🛡️ Bloqueio pelo dado", value=f"`{bloqueio_dado}` ponto(s)", inline=True)
        embed.add_field(name="⚔️ Bônus armadura/escudo", value=f"`+{armadura_val}` ponto(s)", inline=True)
        embed.add_field(name="✅ Total Bloqueado", value=f"**{bloqueio_total} ponto(s) de dano**", inline=True)

        if obs:
            embed.add_field(name="⚡", value=obs, inline=False)

        embed.set_footer(text=f"Jogador: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

# ── COMANDO /batalha ──────────────────────────────────────────────────────────
@tree.command(name="batalha", description="Abre o painel de batalha com opções de Esquivar e Bloquear")
async def batalha(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ Painel de Batalha",
        description="Você foi atacado! O que deseja fazer?",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="💨 Esquivar", value="Reflexo + AGI vs ataque do inimigo", inline=True)
    embed.add_field(name="🛡️ Bloquear", value="Constituição + VIG → reduz dano pela tabela", inline=True)
    embed.set_footer(text="Escolha sua reação abaixo!")

    await interaction.response.send_message(embed=embed, view=BatalhaView())

# ── INICIAR ───────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ {bot.user} online — Comandos sincronizados!")

bot.run(TOKEN)
