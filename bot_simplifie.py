"""
Bot Discord Simplifié - Seykoofx
================================

Bot avec seulement les fonctionnalités essentielles :
- Système de tickets
- Système de règlement
- Système de vérification
- Création automatique des panels
"""

import os
import discord
from discord.ext import commands
from datetime import datetime
import asyncio

# Import des modules essentiels
from tickets import setup_ticket_system, create_ticket_panel, get_language
from reglement import setup_reglement_system, create_reglement_panel
from verification import setup_verification_system, create_verification_panel
from logs import setup_logs_system
from seykooteam import setup_seykooteam_system, create_seykooteam_panel, log_seykooteam_message

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'VOTRE_TOKEN_BOT')
DISCORD_GUILD_ID = '1005763703335034970'

# Configuration du canal d'arrivée/départ
WELCOME_CHANNEL_ID = 1400136710012014622

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Événement quand le bot est prêt"""
    print(f"🤖 Bot connecté: {bot.user.name}")
    print(f"📊 ID du bot: {bot.user.id}")
    print("------")
    
    # Configuration des systèmes essentiels
    await setup_ticket_system(bot)
    setup_reglement_system(bot)
    setup_verification_system(bot)
    setup_logs_system(bot)
    setup_seykooteam_system(bot)
    
    print("✅ Tous les systèmes configurés")
    
    # Créer les panels automatiquement
    await send_automatic_messages()
    
    print("🚀 Bot simplifié Seykoofx démarré avec succès!")

async def send_automatic_messages():
    """Crée automatiquement tous les panels"""
    print("🚀 Création automatique des panels...")
    
    try:
        guild = bot.get_guild(int(DISCORD_GUILD_ID))
        if not guild:
            print("❌ Serveur Discord non trouvé")
            return
        
        print(f"📡 Serveur trouvé: {guild.name}")
        
        # Panel de Tickets
        print("🎫 Création du panel de tickets...")
        ticket_channel = guild.get_channel(1399430693217505300)
        if ticket_channel:
            try:
                await create_ticket_panel(bot, guild)
                print(f"✅ Panel de tickets créé dans #{ticket_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel tickets: {e}")
        else:
            print("❌ Canal de tickets introuvable")
        
        # Panel de Règlement
        print("📜 Création du panel de règlement...")
        reglement_channel = guild.get_channel(1005763703750279183)
        if reglement_channel:
            try:
                await create_reglement_panel(bot, guild)
                print(f"✅ Panel de règlement créé dans #{reglement_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel règlement: {e}")
        else:
            print("❌ Canal de règlement introuvable")
        
        # Panel de Vérification
        print("🔐 Création du panel de vérification...")
        verification_channel = guild.get_channel(1400139457675661412)
        if verification_channel:
            try:
                await create_verification_panel(bot, guild)
                print(f"✅ Panel de vérification créé dans #{verification_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel vérification: {e}")
        else:
            print("❌ Canal de vérification introuvable")
        
        # Panel Seykooteam
        print("🎮 Création du panel Seykooteam...")
        seykooteam_channel = guild.get_channel(1435643776419889183)
        if seykooteam_channel:
            try:
                await create_seykooteam_panel(bot, guild)
                print(f"✅ Panel Seykooteam créé dans #{seykooteam_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel Seykooteam: {e}")
        else:
            print("❌ Canal Seykooteam introuvable")
        
        print("🎉 Création automatique de tous les panels terminée!")
        print("✅ Tous les systèmes sont maintenant opérationnels!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des panels: {e}")

@bot.event
async def on_member_join(member):
    """Événement quand un membre rejoint"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"👋 Nouveau membre: {member.name} ({member.id})")
        
        # Envoyer le message d'arrivée dans le canal spécifié
        try:
            welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            if welcome_channel:
                embed = discord.Embed(
                    title="🎉 Nouveau Membre !",
                    description=f"Bienvenue {member.mention} dans le serveur Seykoofx !",
                    color=0x00ff00,
                    timestamp=datetime.now()
                )
                embed.add_field(
                    name="👤 Membre",
                    value=f"{member.name}#{member.discriminator}",
                    inline=True
                )
                embed.add_field(
                    name="🆔 ID",
                    value=member.id,
                    inline=True
                )
                embed.add_field(
                    name="📅 Arrivée",
                    value=f"<t:{int(datetime.now().timestamp())}:R>",
                    inline=True
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Seykoofx - Système d'arrivée")
                
                await welcome_channel.send(embed=embed)
                print(f"✅ Message d'arrivée envoyé pour {member.name}")
        except Exception as e:
            print(f"❌ Erreur message d'arrivée: {e}")

@bot.event
async def on_member_remove(member):
    """Événement quand un membre quitte"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"👋 Membre parti: {member.name} ({member.id})")
        
        # Envoyer le message de départ dans le canal spécifié
        try:
            welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            if welcome_channel:
                embed = discord.Embed(
                    title="👋 Membre Parti",
                    description=f"{member.mention} a quitté le serveur Seykoofx.",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                embed.add_field(
                    name="👤 Membre",
                    value=f"{member.name}#{member.discriminator}",
                    inline=True
                )
                embed.add_field(
                    name="🆔 ID",
                    value=member.id,
                    inline=True
                )
                embed.add_field(
                    name="📅 Départ",
                    value=f"<t:{int(datetime.now().timestamp())}:R>",
                    inline=True
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text="Seykoofx - Système de départ")
                
                await welcome_channel.send(embed=embed)
                print(f"✅ Message de départ envoyé pour {member.name}")
        except Exception as e:
            print(f"❌ Erreur message de départ: {e}")

@bot.event
async def on_member_update(before, after):
    """Événement quand un membre est mis à jour"""
    if str(after.guild.id) == DISCORD_GUILD_ID:
        before_roles = set(role.id for role in before.roles)
        after_roles = set(role.id for role in after.roles)
        
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        
        for role_id in added_roles:
            print(f"➕ Rôle ajouté: {after.name} -> {role_id}")
        
        for role_id in removed_roles:
            print(f"➖ Rôle retiré: {after.name} -> {role_id}")

@bot.event
async def on_message(message):
    """Événement quand un message est envoyé"""
    # Logger les messages du compte Seykooteam (mais pas les messages du bot lui-même)
    if message.guild and str(message.guild.id) == DISCORD_GUILD_ID and message.author.id != bot.user.id:
        try:
            await log_seykooteam_message(message)
        except Exception as e:
            print(f"❌ Erreur log message Seykooteam: {e}")
    
    
    # Ne pas oublier de traiter les commandes
    await bot.process_commands(message)


# Commandes essentielles seulement
@bot.command(name='info')
async def info(ctx):
    """Informations du bot"""
    embed = discord.Embed(
        title="🤖 Bot Simplifié Seykoofx",
        description="Bot avec fonctionnalités essentielles",
        color=0x00ff00
    )
    embed.add_field(name="Nom", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Serveurs", value=len(bot.guilds), inline=True)
    embed.add_field(name="Latence", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='test_tickets')
@commands.has_permissions(manage_messages=True)
async def test_tickets_command(ctx):
    """Teste le système de tickets"""
    embed = discord.Embed(
        title="🎫 Test du Système de Tickets",
        description="Vérification du système de tickets",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    ticket_channel = ctx.guild.get_channel(1399430693217505300)
    if ticket_channel:
        embed.add_field(name="✅ Canal Tickets", value=f"#{ticket_channel.name}", inline=True)
    else:
        embed.add_field(name="❌ Canal Tickets", value="Introuvable", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='send_all')
@commands.has_permissions(manage_messages=True)
async def send_all_panels(ctx):
    """Recrée tous les panels"""
    await send_automatic_messages()
    await ctx.send("✅ Tous les panels ont été recréés !")

@bot.command(name='force_send')
@commands.has_permissions(manage_messages=True)
async def force_send_messages(ctx):
    """Force l'envoi des messages automatiques"""
    await send_automatic_messages()
    await ctx.send("✅ Messages automatiques envoyés !")

@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs de commandes"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas les permissions pour cette commande.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Commande introuvable. Utilisez `!info` pour voir les commandes disponibles.")
    else:
        await ctx.send(f"❌ Erreur: {error}")

# Démarrage du bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN) 