"""
Système de Tickets - Seykoofx
=============================

Système de tickets avec 3 boutons et catégories spécifiques
Version bilingue (Français/English)
"""

import discord
from discord.ext import commands
from datetime import datetime
import asyncio

# Messages bilingues
MESSAGES = {
    "fr": {
        "no_permission": "❌ Vous n'avez pas les permissions pour fermer ce ticket.",
        "closing_ticket": "🔒 Fermeture du ticket en cours...",
        "ticket_closed": "🎫 Ticket Fermé",
        "ticket_closed_desc": "Ce ticket a été fermé. Merci de votre patience !",
        "satisfaction_form": "📝 Formulaire de Satisfaction",
        "satisfaction_form_desc": "Veuillez remplir notre formulaire de satisfaction :\nhttps://docs.google.com/forms/d/e/1FAIpQLSem2wEBEZzpx8-tjU4RIJHWHrYOuiOGE4qzRF_oH_qM4JqyeA/viewform?usp=header",
        "closing_time": "⏰ Fermeture",
        "closing_time_desc": "Ce canal sera supprimé dans 10 secondes.",
        "already_ticket": "❌ Vous avez déjà un ticket ouvert : {ticket}",
        "invalid_type": "❌ Type de ticket invalide.",
        "category_not_found": "❌ Catégorie de tickets introuvable.",
        "ticket_created": "✅ Votre ticket a été créé : {channel}",
        "ticket_created_title": "🎫 Ticket Créé",
        "ticket_created_desc": "Bienvenue {user} ! Votre ticket a été créé.",
        "type": "Type",
        "created_by": "Créé par",
        "ticket_id": "ID Ticket",
        "panel_title": "🎫 Système de Tickets Seykoofx",
        "panel_desc": "Bienvenue ! Créez un ticket en cliquant sur l'un des boutons ci-dessous.",
        "commande_desc": "Pour passer une commande ou demander un devis",
        "service_desc": "Pour toute question ou problème technique",
        "rejoindre_desc": "Pour postuler ou rejoindre l'équipe",
        "info": "📋 Informations",
        "info_desc": "Un membre de l'équipe vous répondra dans les plus brefs délais."
    },
    "en": {
        "no_permission": "❌ You don't have permission to close this ticket.",
        "closing_ticket": "🔒 Closing ticket in progress...",
        "ticket_closed": "🎫 Ticket Closed",
        "ticket_closed_desc": "This ticket has been closed. Thank you for your patience!",
        "satisfaction_form": "📝 Satisfaction Form",
        "satisfaction_form_desc": "Please fill out our satisfaction form:\nhttps://docs.google.com/forms/d/e/1FAIpQLSem2wEBEZzpx8-tjU4RIJHWHrYOuiOGE4qzRF_oH_qM4JqyeA/viewform?usp=header",
        "closing_time": "⏰ Closing",
        "closing_time_desc": "This channel will be deleted in 10 seconds.",
        "already_ticket": "❌ You already have an open ticket: {ticket}",
        "invalid_type": "❌ Invalid ticket type.",
        "category_not_found": "❌ Ticket category not found.",
        "ticket_created": "✅ Your ticket has been created: {channel}",
        "ticket_created_title": "🎫 Ticket Created",
        "ticket_created_desc": "Welcome {user}! Your ticket has been created.",
        "type": "Type",
        "created_by": "Created by",
        "ticket_id": "Ticket ID",
        "panel_title": "🎫 Seykoofx Ticket System",
        "panel_desc": "Welcome! Create a ticket by clicking one of the buttons below.",
        "commande_desc": "To place an order or request a quote",
        "service_desc": "For any questions or technical issues",
        "rejoindre_desc": "To apply or join the team",
        "info": "📋 Information",
        "info_desc": "A team member will respond to you as soon as possible."
    }
}

def get_language(user: discord.Member) -> str:
    """Détecte la langue de l'utilisateur (simplifié)"""
    # Pour l'instant, on utilise français par défaut
    # Vous pouvez ajouter une logique de détection plus sophistiquée
    return "fr"

def get_message(key: str, lang: str = "fr", **kwargs) -> str:
    """Récupère un message dans la langue spécifiée"""
    message = MESSAGES[lang].get(key, key)
    return message.format(**kwargs) if kwargs else message

# Configuration des catégories de tickets
TICKET_CATEGORIES = {
    "commande": 1399437778189553744,
    "service_client": 1399438065591910516,
    "nous_rejoindre": 1399438265047715981
}

# Configuration du canal de logs
TICKET_LOG_CHANNEL_ID = 1399430693217505300

# Rôles autorisés pour la gestion des tickets
TICKET_MANAGER_ROLES = [
    1335705793697288213,  # 『👤』Responsable Support
    1335706767908405432,  # 『👤』Relation Clients
    1335707516352331949,  # 『👤』Responsable Commercial
    1113214565619085424,  # 𝐀𝐝𝐦𝐢𝐧 technique
    1399517642884124702,  # 『👤』Moderateur technique
    1096054762862026833   # Directeur Général
]

def has_ticket_permission(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur a les permissions de gestion des tickets"""
    user_roles = [role.id for role in user.roles]
    return any(role_id in user_roles for role_id in TICKET_MANAGER_ROLES)

class TicketView(discord.ui.View):
    """Vue avec les boutons pour créer des tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🛒 Commande", style=discord.ButtonStyle.primary, custom_id="ticket_commande")
    async def ticket_commande(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "commande")
    
    @discord.ui.button(label="🎧 Service Client", style=discord.ButtonStyle.success, custom_id="ticket_service")
    async def ticket_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "service_client")
    
    @discord.ui.button(label="👥 Nous Rejoindre", style=discord.ButtonStyle.secondary, custom_id="ticket_rejoindre")
    async def ticket_rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "nous_rejoindre")

class TicketControlView(discord.ui.View):
    """Vue pour contrôler les tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_language(interaction.user)
        
        if not has_ticket_permission(interaction.user):
            await interaction.response.send_message(get_message("no_permission", lang), ephemeral=True)
            return
        
        await interaction.response.send_message(get_message("closing_ticket", lang), ephemeral=True)
        
        # Créer l'embed de fermeture avec le formulaire
        embed = discord.Embed(
            title=get_message("ticket_closed", lang),
            description=get_message("ticket_closed_desc", lang),
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.add_field(
            name=get_message("satisfaction_form", lang),
            value=get_message("satisfaction_form_desc", lang),
            inline=False
        )
        embed.add_field(
            name=get_message("closing_time", lang),
            value=get_message("closing_time_desc", lang),
            inline=False
        )
        
        await interaction.channel.send(embed=embed)
        
        # Log la fermeture
        try:
            from logs import log_ticket_action
            await log_ticket_action(
                interaction.guild,
                "fermé",
                interaction.user,
                f"ticket-{interaction.channel.id}",
                channel=interaction.channel
            )
        except Exception as e:
            print(f"❌ Erreur log ticket: {e}")
        
        # Attendre 10 secondes puis supprimer le canal
        await asyncio.sleep(10)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"❌ Erreur suppression canal: {e}")

async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    """Crée un ticket"""
    lang = get_language(interaction.user)
    
    try:
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        existing_ticket = discord.utils.get(interaction.guild.channels, 
                                         name=f"ticket-{interaction.user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(
                get_message("already_ticket", lang, ticket=existing_ticket.mention),
                ephemeral=True
            )
            return
        
        # Récupérer la catégorie
        category_id = TICKET_CATEGORIES.get(ticket_type)
        if not category_id:
            await interaction.response.send_message(get_message("invalid_type", lang), ephemeral=True)
            return
        
        category = interaction.guild.get_channel(category_id)
        if not category:
            await interaction.response.send_message(get_message("category_not_found", lang), ephemeral=True)
            return
        
        # Créer le canal du ticket
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Ajouter les permissions pour les rôles de gestion
        for role_id in TICKET_MANAGER_ROLES:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        ticket_channel = await interaction.guild.create_text_channel(
            f"ticket-{interaction.user.name.lower()}",
            category=category,
            overwrites=overwrites
        )
        
        # Créer l'embed de bienvenue
        embed = discord.Embed(
            title=get_message("ticket_created_title", lang),
            description=get_message("ticket_created_desc", lang, user=interaction.user.mention),
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name=get_message("type", lang), value=ticket_type.replace("_", " ").title(), inline=True)
        embed.add_field(name=get_message("created_by", lang), value=interaction.user.mention, inline=True)
        embed.add_field(name=get_message("ticket_id", lang), value=f"ticket-{ticket_channel.id}", inline=True)
        
        # Créer la vue de contrôle
        control_view = TicketControlView()
        
        await ticket_channel.send(embed=embed, view=control_view)
        await interaction.response.send_message(
            get_message("ticket_created", lang, channel=ticket_channel.mention),
            ephemeral=True
        )
        
        # Log la création
        try:
            from logs import log_ticket_action
            await log_ticket_action(
                interaction.guild,
                "créé",
                interaction.user,
                f"ticket-{ticket_channel.id}",
                channel=ticket_channel
            )
        except Exception as e:
            print(f"❌ Erreur log ticket: {e}")
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur lors de la création du ticket: {e}", ephemeral=True)

async def create_ticket_panel(bot, guild):
    """Crée le panel de tickets"""
    try:
        # Récupérer le canal de tickets
        ticket_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if not ticket_channel:
            print("❌ Canal de tickets introuvable")
            return
        
        # Supprimer les anciens messages
        try:
            await ticket_channel.purge()
        except:
            pass
        
        # Créer l'embed du panel (version française par défaut)
        embed = discord.Embed(
            title=get_message("panel_title", "fr"),
            description=get_message("panel_desc", "fr"),
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="🛒 Commande",
            value=get_message("commande_desc", "fr"),
            inline=True
        )
        embed.add_field(
            name="🎧 Service Client",
            value=get_message("service_desc", "fr"),
            inline=True
        )
        embed.add_field(
            name="👥 Nous Rejoindre",
            value=get_message("rejoindre_desc", "fr"),
            inline=True
        )
        embed.add_field(
            name=get_message("info", "fr"),
            value=get_message("info_desc", "fr"),
            inline=False
        )
        
        # Créer la vue avec les boutons
        view = TicketView()
        
        await ticket_channel.send(embed=embed, view=view)
        print(f"✅ Panel de tickets envoyé dans #{ticket_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel tickets: {e}")

def setup_ticket_system(bot):
    """Configure le système de tickets"""
    print("✅ Système de tickets configuré") 