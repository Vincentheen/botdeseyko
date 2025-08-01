"""
Bot Discord Unifié - Seykoofx
=============================

Ce bot combine toutes les fonctionnalités :
- Système de tickets
- Gestion du règlement
- API pour intégration web
- Vérification des rôles Discord
"""

import os
import discord
from discord.ext import commands
import requests
import json
from datetime import datetime, timedelta
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import secrets
from threading import Thread
import time

# Import des modules séparés
from tickets import (
    setup_ticket_system, 
    create_ticket_panel
)
from reglement import setup_reglement_system, create_reglement_panel
from verification import (
    setup_verification_system,
    create_verification_panel
)
from security import setup_security_system
from annonce import setup_announcement_system
from planning import (
    setup_planning_system,
    create_planning_panel
)
from logs import setup_logs_system
from moderation import setup_moderation_system

# =============================================================================
# CONFIGURATION
# =============================================================================

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'VOTRE_TOKEN_BOT')
DISCORD_GUILD_ID = '1005763703335034970'
REQUIRED_ROLE_ID = '1005763703335034975'
PREMIUM_ROLE_ID = '1400254347866144900'  # Rôle premium pour débloquer le contenu
API_SECRET_KEY = os.getenv('API_SECRET_KEY', '533d4a210d245708c0a1bae2db14036abeabc77b6faa457203a8758f5b2050d9')

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration Flask API
app = Flask(__name__)
CORS(app, origins=['https://seykoofx-shop.vercel.app', 'http://localhost:3000', 'http://localhost:5000'], 
      methods=['GET', 'POST', 'OPTIONS'], 
      allow_headers=['Content-Type', 'Authorization'])

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def generate_token(user_id, username):
    """Génère un token JWT pour l'utilisateur"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, API_SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Vérifie un token JWT"""
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

def discord_api_request(endpoint, method='GET', data=None):
    """Fait une requête à l'API Discord"""
    headers = {
        'Authorization': f'Bot {DISCORD_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://discord.com/api/v10{endpoint}'
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    return response

def check_user_has_role(user_id, role_id):
    """Vérifie si un utilisateur a un rôle spécifique"""
    try:
        member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
        
        if member_response.status_code != 200:
            print(f"Erreur vérification membre {user_id}: {member_response.status_code}")
            return False
        
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        
        # Debug: afficher les rôles de l'utilisateur
        print(f"Rôles de l'utilisateur {user_id}: {user_roles}")
        print(f"Rôle requis: {role_id}")
        
        has_role = role_id in user_roles
        print(f"L'utilisateur a le rôle requis: {has_role}")
        
        return has_role
        
    except Exception as e:
        print(f"Erreur lors de la vérification du rôle: {e}")
        return False

def check_user_has_access(user_id):
    """Vérifie si un utilisateur a accès au site (rôle membre OU premium)"""
    try:
        member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
        
        if member_response.status_code != 200:
            print(f"Erreur vérification membre {user_id}: {member_response.status_code}")
            return False
        
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        
        # Vérifier si l'utilisateur a le rôle membre OU premium
        has_member_role = REQUIRED_ROLE_ID in user_roles
        has_premium_role = PREMIUM_ROLE_ID in user_roles
        
        print(f"Rôles de l'utilisateur {user_id}: {user_roles}")
        print(f"Rôle membre ({REQUIRED_ROLE_ID}): {has_member_role}")
        print(f"Rôle premium ({PREMIUM_ROLE_ID}): {has_premium_role}")
        
        has_access = has_member_role or has_premium_role
        print(f"L'utilisateur a accès au site: {has_access}")
        
        return has_access
        
    except Exception as e:
        print(f"Erreur lors de la vérification d'accès: {e}")
        return False

def check_user_premium_status(user_id):
    """Vérifie si un utilisateur a le rôle premium"""
    return check_user_has_role(user_id, PREMIUM_ROLE_ID)

# =============================================================================
# ÉVÉNEMENTS DISCORD
# =============================================================================

@bot.event
async def on_ready():
    """Événement quand le bot est prêt"""
    print(f"✅ Bot connecté en tant que {bot.user.name}")
    print(f"🆔 ID du bot: {bot.user.id}")
    print(f"📊 Nombre de serveurs: {len(bot.guilds)}")
    
    # Vérifier la configuration
    if DISCORD_TOKEN == 'VOTRE_TOKEN_BOT':
        print("⚠️  ATTENTION: DISCORD_TOKEN non configuré!")
    
    # Afficher les serveurs
    for guild in bot.guilds:
        print(f"📡 Serveur: {guild.name} (ID: {guild.id})")
        if str(guild.id) == DISCORD_GUILD_ID:
            print(f"✅ Serveur cible trouvé: {guild.name}")
    
    # Configuration du système de tickets
    await setup_ticket_system(bot)
    
    # Configuration du système de vérification
    await setup_verification_system(bot)
    
    # Configuration du système de sécurité extrême
    security_manager = setup_security_system(bot)
    print("🔒 Système de sécurité extrême activé")
    
    # Configuration du système d'annonces
    setup_announcement_system(bot)
    print("📢 Système d'annonces activé")
    
    # Configuration du système de planning
    await setup_planning_system(bot)
    print("📅 Système de planning activé")
    
    # Configuration du système de logs
    setup_logs_system(bot)
    print("📊 Système de logs activé")
    
    # Configuration du système de modération
    await setup_moderation_system(bot)
    print("🛡️ Système de modération activé")
    
    # Nettoyer toutes les commandes slash existantes
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print("🧹 Commandes slash nettoyées")
    except Exception as e:
        print(f"❌ Erreur nettoyage commandes slash: {e}")
    
    # Pas de commandes slash - uniquement les commandes avec !
    print("✅ Système de commandes avec ! activé")
    
    # Attendre un peu pour s'assurer que le bot est complètement connecté
    await asyncio.sleep(3)
    
    # Envoyer les messages automatiques dans les channels
    await send_automatic_messages()
    
    print("🚀 Bot unifié Seykoofx démarré avec succès!")
    print("✅ Tous les panels ont été créés automatiquement!")

async def send_automatic_messages():
    """Envoie les messages automatiques dans les channels spécifiés"""
    print("🚀 Démarrage de l'envoi automatique des messages...")
    
    try:
        guild = bot.get_guild(int(DISCORD_GUILD_ID))
        if not guild:
            print("❌ Serveur Discord non trouvé")
            return
        
        print(f"📡 Serveur trouvé: {guild.name}")
        
        # Channel Tickets - ID: 1399430693217505300
        print("🎫 Création du panel de tickets...")
        ticket_channel = guild.get_channel(1399430693217505300)
        if ticket_channel:
            try:
                from tickets import create_ticket_panel
                await create_ticket_panel(bot, guild)
                print(f"✅ Panel de tickets créé dans #{ticket_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel tickets: {e}")
        else:
            print("❌ Canal de tickets introuvable (ID: 1399430693217505300)")
        
        # Channel Règlement - ID: 1005763703750279183
        print("📜 Création du panel de règlement...")
        reglement_channel = guild.get_channel(1005763703750279183)
        if reglement_channel:
            try:
                from reglement import create_reglement_panel
                await create_reglement_panel(bot, guild)
                print(f"✅ Panel de règlement créé dans #{reglement_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel règlement: {e}")
        else:
            print("❌ Canal de règlement introuvable (ID: 1005763703750279183)")
        
        # Channel Vérification - ID: 1400139457675661412
        print("🔐 Création du panel de vérification...")
        verification_channel = guild.get_channel(1400139457675661412)
        if verification_channel:
            try:
                from verification import create_verification_panel
                await create_verification_panel(bot, guild)
                print(f"✅ Panel de vérification créé dans #{verification_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel vérification: {e}")
        else:
            print("❌ Canal de vérification introuvable (ID: 1400139457675661412)")
        
        # Channel Planning - ID: 1400608607002820770
        print("📅 Création du panel de planning...")
        planning_channel = guild.get_channel(1400608607002820770)
        if planning_channel:
            try:
                from planning import create_planning_panel
                await create_planning_panel(bot, guild)
                print(f"✅ Panel de planning créé dans #{planning_channel.name}")
            except Exception as e:
                print(f"❌ Erreur création panel planning: {e}")
        else:
            print("❌ Canal de planning introuvable (ID: 1400608607002820770)")
        
        print("🎉 Création automatique de tous les panels terminée!")
        print("✅ Tous les systèmes sont maintenant opérationnels!")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi des messages automatiques: {e}")

@bot.event
async def on_member_join(member):
    """Événement quand un membre rejoint"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"👋 Nouveau membre: {member.name} ({member.id})")

@bot.event
async def on_member_remove(member):
    """Événement quand un membre quitte"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"👋 Membre parti: {member.name} ({member.id})")

@bot.event
async def on_member_update(before, after):
    """Événement quand un membre est mis à jour (rôles, etc.)"""
    if str(after.guild.id) == DISCORD_GUILD_ID:
        # Vérifier les changements de rôles
        before_roles = set(role.id for role in before.roles)
        after_roles = set(role.id for role in after.roles)
        
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        
        for role_id in added_roles:
            print(f"➕ Rôle ajouté: {after.name} -> {role_id}")
        
        for role_id in removed_roles:
            print(f"➖ Rôle retiré: {after.name} -> {role_id}")

# =============================================================================
# COMMANDES BOT
# =============================================================================

@bot.command(name='info')
async def info(ctx):
    """Affiche les informations du bot"""
    embed = discord.Embed(
        title="🤖 Informations Bot Unifié",
        description="Bot Discord Seykoofx avec toutes les fonctionnalités",
        color=0x00ff00
    )
    embed.add_field(name="Nom", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Serveurs", value=len(bot.guilds), inline=True)
    embed.add_field(name="Latence", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Serveur cible", value=DISCORD_GUILD_ID, inline=True)
    embed.add_field(name="Rôle requis", value=REQUIRED_ROLE_ID, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='roles')
async def roles(ctx):
    """Affiche les rôles du serveur"""
    guild = ctx.guild
    roles_list = []
    
    for role in guild.roles:
        if not role.managed and role.name != "@everyone":
            roles_list.append(f"• {role.name} (ID: {role.id})")
    
    embed = discord.Embed(
        title="📋 Rôles du serveur",
        description="\n".join(roles_list[:20]),  # Limiter à 20 rôles
        color=0x0099ff
    )
    
    await ctx.send(embed=embed)

@bot.command(name='addrole')
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Ajoute un rôle à un membre"""
    try:
        await member.add_roles(role)
        await ctx.send(f"✅ Rôle {role.name} ajouté à {member.name}")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour ajouter ce rôle")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")

@bot.command(name='removerole')
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    """Retire un rôle d'un membre"""
    try:
        await member.remove_roles(role)
        await ctx.send(f"✅ Rôle {role.name} retiré de {member.name}")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions pour retirer ce rôle")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")

@bot.command(name='premium')
async def premium(ctx):
    """Informations sur le système Premium"""
    embed = discord.Embed(
        title="⭐ Système Premium",
        description="Système de rôles Premium pour le contenu exclusif",
        color=0xffd700
    )
    embed.add_field(name="Rôle Premium ID", value=PREMIUM_ROLE_ID, inline=True)
    embed.add_field(name="Rôle requis ID", value=REQUIRED_ROLE_ID, inline=True)
    embed.add_field(name="Serveur ID", value=DISCORD_GUILD_ID, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='checkroles')
@commands.has_permissions(manage_roles=True)
async def check_roles_command(ctx, member: discord.Member = None):
    """Vérifie les rôles d'un utilisateur (admin seulement)"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title="🔍 Diagnostic des Rôles",
        description=f"Rôles de {member.mention}",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Rôles de l'utilisateur
    roles_list = []
    for role in member.roles:
        if role.name != "@everyone":
            roles_list.append(f"{role.mention} (ID: {role.id})")
    
    embed.add_field(
        name="📋 Rôles actuels",
        value="\n".join(roles_list) if roles_list else "Aucun rôle",
        inline=False
    )
    
    # Vérifier les rôles spécifiques
    required_role = ctx.guild.get_role(int(REQUIRED_ROLE_ID))
    premium_role = ctx.guild.get_role(int(PREMIUM_ROLE_ID))
    
    embed.add_field(
        name="🎯 Rôles requis",
        value=f"Rôle membre: {'✅' if required_role in member.roles else '❌'} ({REQUIRED_ROLE_ID})\n"
              f"Rôle premium: {'✅' if premium_role in member.roles else '❌'} ({PREMIUM_ROLE_ID})",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='testauth')
@commands.has_permissions(manage_roles=True)
async def test_auth_command(ctx, user_id: str = None):
    """Teste l'authentification d'un utilisateur (admin seulement)"""
    if user_id is None:
        user_id = str(ctx.author.id)
    
    embed = discord.Embed(
        title="🧪 Test d'Authentification",
        description=f"Test pour l'utilisateur <@{user_id}>",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    try:
        # Vérifier si l'utilisateur est dans le serveur
        member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
        
        if member_response.status_code != 200:
            embed.add_field(
                name="❌ Résultat",
                value="L'utilisateur n'est pas membre du serveur",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Vérifier les rôles
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        
        has_member_role = REQUIRED_ROLE_ID in user_roles
        has_premium_role = PREMIUM_ROLE_ID in user_roles
        has_access = has_member_role or has_premium_role
        
        embed.add_field(
            name="📋 Rôles",
            value=f"Rôle membre: {'✅' if has_member_role else '❌'}\n"
                  f"Rôle premium: {'✅' if has_premium_role else '❌'}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Accès",
            value=f"Accès au site: {'✅' if has_access else '❌'}\n"
                  f"Type d'accès: {'Premium' if has_premium_role else ('Membre' if has_member_role else 'Aucun')}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 IDs",
            value=f"Membre: {REQUIRED_ROLE_ID}\n"
                  f"Premium: {PREMIUM_ROLE_ID}",
            inline=False
        )
        
        if has_access:
            embed.color = 0x00ff00
            embed.title = "✅ Test d'Authentification - SUCCÈS"
        else:
            embed.color = 0xff0000
            embed.title = "❌ Test d'Authentification - ÉCHEC"
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed.add_field(
            name="❌ Erreur",
            value=f"Erreur lors du test: {str(e)}",
            inline=False
        )
        await ctx.send(embed=embed)

# =============================================================================
# SYSTÈME DE TICKETS (importé depuis tickets.py)
# =============================================================================

# =============================================================================
# COMMANDES DE TICKETS (avec !)
# =============================================================================

@bot.command(name='statue')
async def statue_command(ctx):
    """Affiche le statut d'un ticket"""
    await check_ticket_status(ctx)

@bot.command(name='statue1')
async def statue1_command(ctx):
    """Met le ticket en attente"""
    await change_ticket_status_command(ctx, 1)

@bot.command(name='statue2')
async def statue2_command(ctx):
    """Met le ticket en cours"""
    await change_ticket_status_command(ctx, 2)

@bot.command(name='statue3')
async def statue3_command(ctx):
    """Met le ticket comme terminé"""
    await change_ticket_status_command(ctx, 3)

# =============================================================================
# GESTION DU RÈGLEMENT (importé depuis reglement.py)
# =============================================================================

@bot.command(name='reglement')
async def reglement_command(ctx):
    """Commande pour afficher le règlement"""
    await reglement(ctx)

@bot.command(name='update_reglement')
@commands.has_permissions(manage_messages=True)
async def update_reglement_command(ctx):
    """Commande pour mettre à jour le règlement"""
    await update_reglement(ctx, bot)

@bot.command(name='clean_slash')
@commands.is_owner()
async def clean_slash_commands(ctx):
    """Nettoie toutes les commandes slash (propriétaire uniquement)"""
    try:
        # Supprimer toutes les commandes slash
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        
        embed = discord.Embed(
            title="🧹 Nettoyage Terminé",
            description="Toutes les commandes slash ont été supprimées.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Statut", value="✅ Commandes slash supprimées", inline=True)
        embed.add_field(name="Système", value="Uniquement les commandes avec !", inline=True)
        
        await ctx.send(embed=embed)
        print("🧹 Commandes slash nettoyées manuellement")
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Erreur lors du nettoyage: {str(e)}",
            color=0xff0000,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)

# =============================================================================
# COMMANDES POUR ENVOYER LES MESSAGES MANUELLEMENT
# =============================================================================

@bot.command(name='send_reglement')
@commands.has_permissions(manage_messages=True)
async def send_reglement_here(ctx):
    """Envoie le panel de règlement dans le canal actuel"""
    try:
        from verification import create_reglement_panel
        await create_reglement_panel(bot, ctx.guild)
        await ctx.send("✅ Panel de règlement envoyé avec succès!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'envoi du panel règlement: {e}")

@bot.command(name='send_tickets')
@commands.has_permissions(manage_messages=True)
async def send_tickets_here(ctx):
    """Envoie le panel de tickets dans le canal actuel"""
    try:
        from tickets import create_ticket_panel
        await create_ticket_panel(bot, ctx.guild)
        await ctx.send("✅ Panel de tickets envoyé avec succès!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'envoi du panel tickets: {e}")

@bot.command(name='send_verification')
@commands.has_permissions(manage_messages=True)
async def send_verification_here(ctx):
    """Envoie le panel de vérification dans le canal actuel"""
    try:
        from verification import create_verification_panel
        await create_verification_panel(bot, ctx.guild)
        await ctx.send("✅ Panel de vérification envoyé avec succès!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'envoi du panel vérification: {e}")

@bot.command(name='send_all')
@commands.has_permissions(manage_messages=True)
async def send_all_panels(ctx):
    """Envoie tous les panels dans le canal actuel"""
    try:
        # Règlement
        from reglement import reglement
        await reglement(ctx)
        
        # Tickets
        from tickets import create_ticket_panel
        await create_ticket_panel(bot, ctx.guild)
        
        # Vérification
        from verification import create_verification_panel
        await create_verification_panel(bot, ctx.guild)
        
        # Planning
        embed = discord.Embed(
            title="📅 Système de Planning Pro",
            description="Gérez le planning des trailers et vidéos avec les boutons ci-dessous",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📅 Ajouter Date",
            value="Créez une nouvelle entrée dans le planning",
            inline=True
        )
        embed.add_field(
            name="✏️ Modifier Date",
            value="Modifiez une date existante",
            inline=True
        )
        embed.add_field(
            name="🗑️ Supprimer Date",
            value="Supprimez une date du planning",
            inline=True
        )
        embed.add_field(
            name="📋 Voir Planning",
            value="Consultez le planning complet",
            inline=True
        )
        embed.set_footer(text="Seykoofx - Planning Pro")
        
        view = PlanningView()
        await ctx.send(embed=embed, view=view)
        
        # Modération
        embed = discord.Embed(
            title="🛡️ Système de Modération",
            description="Gérez la modération avec les boutons ci-dessous",
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="🛡️ Kick",
            value="Expulse un utilisateur du serveur",
            inline=True
        )
        embed.add_field(
            name="🔨 Ban",
            value="Bannit un utilisateur du serveur",
            inline=True
        )
        embed.add_field(
            name="⏰ Timeout",
            value="Timeoute un utilisateur temporairement",
            inline=True
        )
        embed.add_field(
            name="➕ Ajouter Rôle",
            value="Ajoute un rôle à un utilisateur",
            inline=True
        )
        embed.set_footer(text="Seykoofx - Modération")
        
        view = ModerationView()
        await ctx.send(embed=embed, view=view)
        
        await ctx.send("✅ Tous les panels ont été envoyés avec succès!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'envoi des panels: {e}")

@bot.command(name='check_channels')
@commands.has_permissions(manage_messages=True)
async def check_channels_command(ctx):
    """Vérifie les canaux configurés dans le bot"""
    embed = discord.Embed(
        title="🔍 Vérification des Canaux",
        description="Statut des canaux configurés dans le bot",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Canaux de tickets
    ticket_channel = ctx.guild.get_channel(1399430693217505300)
    embed.add_field(
        name="🎫 Canal Tickets",
        value=f"{'✅ Trouvé' if ticket_channel else '❌ Introuvable'} - ID: 1399430693217505300",
        inline=True
    )
    
    # Canaux de logs
    planning_log_channel = ctx.guild.get_channel(1400613991851491379)
    embed.add_field(
        name="📅 Logs Planning",
        value=f"{'✅ Trouvé' if planning_log_channel else '❌ Introuvable'} - ID: 1400613991851491379",
        inline=True
    )
    
    voice_log_channel = ctx.guild.get_channel(1400614430336614511)
    embed.add_field(
        name="🎤 Logs Vocal",
        value=f"{'✅ Trouvé' if voice_log_channel else '❌ Introuvable'} - ID: 1400614430336614511",
        inline=True
    )
    
    moderation_log_channel = ctx.guild.get_channel(1400614542538707097)
    embed.add_field(
        name="🛡️ Logs Modération",
        value=f"{'✅ Trouvé' if moderation_log_channel else '❌ Introuvable'} - ID: 1400614542538707097",
        inline=True
    )
    
    # Canal de vérification
    verification_channel = ctx.guild.get_channel(1400139457675661412)
    embed.add_field(
        name="🔐 Canal Vérification",
        value=f"{'✅ Trouvé' if verification_channel else '❌ Introuvable'} - ID: 1400139457675661412",
        inline=True
    )
    
    # Canal de règlement
    reglement_channel = ctx.guild.get_channel(1005763703750279183)
    embed.add_field(
        name="📜 Canal Règlement",
        value=f"{'✅ Trouvé' if reglement_channel else '❌ Introuvable'} - ID: 1005763703750279183",
        inline=True
    )
    
    # Canal de planning
    planning_channel = ctx.guild.get_channel(1400608607002820770)
    embed.add_field(
        name="📅 Canal Planning",
        value=f"{'✅ Trouvé' if planning_channel else '❌ Introuvable'} - ID: 1400608607002820770",
        inline=True
    )
    
    embed.add_field(
        name="💡 Solution",
        value="Utilisez `!send_all` dans le canal où vous voulez les messages",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='force_send')
@commands.has_permissions(manage_messages=True)
async def force_send_messages(ctx):
    """Force l'envoi des messages dans les canaux configurés"""
    try:
        await send_automatic_messages()
        await ctx.send("✅ Messages envoyés dans les canaux configurés!")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de l'envoi: {e}")

@bot.command(name='help_messages')
async def help_messages_command(ctx):
    """Affiche l'aide pour les commandes de messages"""
    embed = discord.Embed(
        title="📋 Commandes de Messages",
        description="Commandes pour gérer les messages automatiques",
        color=0x0099ff
    )
    
    commands_list = [
        ("`!check_channels`", "Vérifie les canaux configurés"),
        ("`!force_send`", "Force l'envoi des messages dans les canaux configurés"),
        ("`!send_all`", "Envoie tous les panels dans le canal actuel"),
        ("`!send_reglement`", "Envoie le règlement dans le canal actuel"),
        ("`!send_tickets`", "Envoie le panel de tickets dans le canal actuel"),
        ("`!send_verification`", "Envoie le panel de vérification dans le canal actuel"),
        ("`!send_planning`", "Envoie le panel de planning dans le canal actuel"),
        ("`!clear`", "Supprime les derniers messages du canal"),
        ("`!annonce`", "Envoie une annonce avec bannière"),
        ("`!annonce_titre`", "Envoie une annonce avec titre personnalisé")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="📊 Canaux Configurés",
        value="• Tickets: 1399430693217505300\n• Règlement: 1005763703750279183\n• Vérification: 1400139457675661412\n• Planning: 1400608607002820770\n• Logs Planning: 1400613991851491379\n• Logs Vocal: 1400614430336614511\n• Logs Modération: 1400614542538707097",
        inline=False
    )
    
    # Ajouter les commandes de planning
    planning_commands = [
        ("`!planning`", "Affiche le planning complet"),
        ("`!addplanning`", "Ajoute une date au planning"),
        ("`!editplanning`", "Modifie une date du planning"),
        ("`!deleteplanning`", "Supprime une date du planning")
    ]
    
    planning_text = "\n".join([f"• {cmd}: {desc}" for cmd, desc in planning_commands])
    embed.add_field(
        name="📅 Commandes de Planning",
        value=planning_text,
        inline=False
    )
    
    # Ajouter les commandes de modération
    moderation_commands = [
        ("`!moderation`", "Affiche le panel de modération"),
        ("`!kick`", "Kick un utilisateur"),
        ("`!ban`", "Ban un utilisateur"),
        ("`!timeout`", "Timeout un utilisateur"),
        ("`!addrole`", "Ajoute un rôle à un utilisateur")
    ]
    
    moderation_text = "\n".join([f"• {cmd}: {desc}" for cmd, desc in moderation_commands])
    embed.add_field(
        name="🛡️ Commandes de Modération",
        value=moderation_text,
        inline=False
    )
    
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
    
    # Vérifier le canal de tickets
    ticket_channel = ctx.guild.get_channel(1399430693217505300)
    
    if ticket_channel:
        embed.add_field(name="✅ Canal Tickets", value=f"#{ticket_channel.name}", inline=True)
    else:
        embed.add_field(name="❌ Canal Tickets", value="Introuvable", inline=True)
    
    await ctx.send(embed=embed)

# =============================================================================
# COMMANDES DE PLANNING
# =============================================================================

@bot.command(name='planning')
async def planning_command(ctx):
    """Affiche le planning"""
    await ctx.send("📅 Utilisez les boutons dans le canal planning pour gérer le planning.")

@bot.command(name='send_planning')
@commands.has_permissions(manage_messages=True)
async def send_planning_here(ctx):
    """Envoie le panel de planning dans le canal actuel"""
    try:
        from planning import create_planning_panel
        await create_planning_panel(bot, ctx.guild)
        await ctx.send("✅ Panel de planning envoyé !")
    except Exception as e:
        await ctx.send(f"❌ Erreur envoi panel planning: {e}")

# =============================================================================
# COMMANDES DE MODÉRATION
# =============================================================================

@bot.command(name='moderation')
async def moderation_command(ctx):
    """Affiche le panel de modération"""
    await ctx.send("🛡️ Système de modération disponible via les permissions Discord.")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_command(ctx):
    """Affiche le modal pour kick un utilisateur"""
    await show_kick_modal(ctx)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_command(ctx):
    """Affiche le modal pour ban un utilisateur"""
    await show_ban_modal(ctx)

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout_command(ctx):
    """Affiche le modal pour timeout un utilisateur"""
    await show_timeout_modal(ctx)



# =============================================================================
# GESTION D'ERREURS
# =============================================================================

@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs de commandes"""
    try:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions pour cette commande")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Argument manquant. Utilisez `!help` pour voir la syntaxe")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide")
        elif isinstance(error, discord.NotFound):
            # Canal ou message introuvable, on ignore silencieusement
            pass
        else:
            await ctx.send(f"❌ Erreur: {error}")
    except discord.NotFound:
        # Si le canal n'existe plus, on ne peut rien faire
        pass
    except Exception as e:
        # En cas d'erreur dans le gestionnaire d'erreur lui-même, on log mais on ne fait rien
        print(f"Erreur dans le gestionnaire d'erreur: {e}")

# =============================================================================
# API FLASK (pour l'intégration web)
# =============================================================================

@app.route('/api/auth/verify', methods=['POST'])
def verify_discord_user():
    """Vérifie un utilisateur Discord et génère un token"""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({'error': 'Code Discord manquant'}), 400
    
    code = data['code']
    
    # Échange du code contre un token d'accès
    token_data = {
        'client_id': '1399410242617475132',
        'client_secret': os.getenv('DISCORD_CLIENT_SECRET', 'VOTRE_CLIENT_SECRET'),
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://seykoofx-shop.vercel.app/auth/callback'
    }
    
    # Essayer d'abord avec l'URL de production
    token_response = requests.post('https://discord.com/api/oauth2/token', data=token_data)
    
    # Si ça échoue, essayer avec l'URL de développement
    if token_response.status_code != 200:
        token_data['redirect_uri'] = 'http://localhost:3000/auth/callback'
        token_response = requests.post('https://discord.com/api/oauth2/token', data=token_data)
    
    if token_response.status_code != 200:
        print(f"Erreur échange token: {token_response.text}")
        return jsonify({'error': 'Erreur lors de l\'échange du code'}), 400
    
    token_data = token_response.json()
    access_token = token_data['access_token']
    
    # Récupération des informations utilisateur depuis Discord
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
    
    if user_response.status_code != 200:
        return jsonify({'error': 'Token Discord invalide'}), 401
    
    user_data = user_response.json()
    user_id = user_data['id']
    username = user_data['username']
    
    print(f"Vérification de l'utilisateur Discord: {username} (ID: {user_id})")
    
    # Vérification si l'utilisateur est dans le serveur
    member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
    
    if member_response.status_code != 200:
        print(f"Utilisateur {username} n'est pas membre du serveur")
        return jsonify({
            'error': 'Vous n\'êtes pas membre du serveur Discord Seykoofx',
            'discord_invite': 'https://discord.gg/2Fg7mW7wKg',
            'message': 'Rejoignez notre serveur Discord pour accéder au site'
        }), 403
    
    print(f"Utilisateur {username} est membre du serveur")
    
    # Vérification si l'utilisateur a accès au site
    has_access = check_user_has_access(user_id)
    
    if not has_access:
        print(f"Utilisateur {username} n'a pas accès au site (rôle membre OU premium)")
        return jsonify({
            'error': 'Vous n\'avez pas les permissions nécessaires pour accéder à ce site',
            'discord_invite': 'https://discord.gg/2Fg7mW7wKg',
            'message': 'Contactez un administrateur pour obtenir les permissions nécessaires'
        }), 403
    
    print(f"Utilisateur {username} a accès au site - authentification réussie")
    
    # Récupérer les informations détaillées sur les rôles
    member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
    member_data = member_response.json()
    user_roles = member_data.get('roles', [])
    
    # Déterminer le type d'accès
    has_member_role = REQUIRED_ROLE_ID in user_roles
    has_premium_role = PREMIUM_ROLE_ID in user_roles
    
    access_type = "premium" if has_premium_role else "member"
    
    # Génération du token API
    api_token = generate_token(user_id, username)
    
    return jsonify({
        'success': True,
        'token': api_token,
        'user': {
            'id': user_id,
            'username': username,
            'avatar': user_data.get('avatar'),
            'email': user_data.get('email'),
            'roles': user_roles,
            'has_member_role': has_member_role,
            'has_premium_role': has_premium_role,
            'access_type': access_type
        }
    })

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """Récupère les informations de l'utilisateur"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Token manquant'}), 401
    
    token = token.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Token invalide'}), 401
    
    user_id = payload['user_id']
    
    # Récupération des informations du membre
    member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
    
    if member_response.status_code != 200:
        return jsonify({'error': 'Membre non trouvé'}), 404
    
    member_data = member_response.json()
    
    # Récupération des rôles
    roles = []
    for role_id in member_data.get('roles', []):
        role_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/roles/{role_id}')
        if role_response.status_code == 200:
            role_data = role_response.json()
            roles.append({
                'id': role_data['id'],
                'name': role_data['name'],
                'color': role_data['color']
            })
    
    return jsonify({
        'user_id': user_id,
        'username': payload['username'],
        'nickname': member_data.get('nick'),
        'joined_at': member_data.get('joined_at'),
        'roles': roles
    })

@app.route('/api/user/premium-status', methods=['GET'])
def get_premium_status():
    """Vérifie le statut premium de l'utilisateur"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Token manquant'}), 401
    
    token = token.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Token invalide'}), 401
    
    user_id = payload['user_id']
    
    try:
        # Vérifier les rôles de l'utilisateur
        member_response = discord_api_request(f'/guilds/{DISCORD_GUILD_ID}/members/{user_id}')
        
        if member_response.status_code != 200:
            return jsonify({'error': 'Membre non trouvé'}), 404
        
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        
        # Vérifier les rôles spécifiques
        has_member_role = REQUIRED_ROLE_ID in user_roles
        has_premium_role = PREMIUM_ROLE_ID in user_roles
        
        return jsonify({
            'success': True,
            'has_member_role': has_member_role,
            'has_premium_role': has_premium_role,
            'has_access': has_member_role or has_premium_role,
            'access_type': 'premium' if has_premium_role else ('member' if has_member_role else 'none'),
            'roles': user_roles
        })
        
    except Exception as e:
        print(f"Erreur vérification statut premium: {e}")
        return jsonify({'error': 'Erreur lors de la vérification du statut'}), 500

@app.route('/api/user/has-role', methods=['POST'])
def check_user_role():
    """Vérifie si un utilisateur a un rôle spécifique"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Token manquant'}), 401
    
    token = token.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Token invalide'}), 401
    
    user_id = payload['user_id']
    data = request.get_json()
    role_id = data.get('role_id')
    
    if not role_id:
        return jsonify({'error': 'ID du rôle manquant'}), 400
    
    # Vérifier si l'utilisateur a le rôle
    has_role = check_user_has_role(user_id, role_id)
    
    return jsonify({
        'has_role': has_role,
        'user_id': user_id,
        'role_id': role_id,
        'message': 'Rôle vérifié avec succès'
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de la santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_connected': bool(DISCORD_TOKEN != 'VOTRE_TOKEN_BOT'),
        'guild_id': DISCORD_GUILD_ID,
        'required_role': REQUIRED_ROLE_ID,
        'premium_role': PREMIUM_ROLE_ID
    })

# =============================================================================
# DÉMARRAGE DU BOT ET DE L'API
# =============================================================================

def run_flask():
    """Démarre le serveur Flask dans un thread séparé"""
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

def start_api():
    """Démarre l'API Flask"""
    print("🚀 Démarrage de l'API Flask...")
    run_flask()

if __name__ == '__main__':
    print("🚀 Démarrage du bot Discord unifié...")
    print(f"📡 Serveur Discord: {DISCORD_GUILD_ID}")
    print(f"🔑 Rôle requis: {REQUIRED_ROLE_ID}")
    print(f"👑 Rôle Premium: {PREMIUM_ROLE_ID}")
    
    # Démarrer l'API Flask dans un thread séparé
    api_thread = Thread(target=start_api)
    api_thread.daemon = True
    api_thread.start()
    
    # Démarrer le bot Discord
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Token Discord invalide")
    except Exception as e:
        print(f"❌ Erreur démarrage bot: {e}") 