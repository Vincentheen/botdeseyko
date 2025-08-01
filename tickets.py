"""
Système de Tickets - Seykoofx
=============================

Système de tickets avec 3 boutons et catégories spécifiques
"""

import discord
from discord.ext import commands
from datetime import datetime
import asyncio

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
        if not has_ticket_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour fermer ce ticket.", ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Fermeture du ticket en cours...", ephemeral=True)
        
        # Créer l'embed de fermeture avec le formulaire
        embed = discord.Embed(
            title="🎫 Ticket Fermé",
            description="Ce ticket a été fermé. Merci de votre patience !",
            color=0xff0000,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📝 Formulaire de Satisfaction",
            value="Veuillez remplir notre formulaire de satisfaction :\nhttps://docs.google.com/forms/d/e/1FAIpQLSem2wEBEZzpx8-tjU4RIJHWHrYOuiOGE4qzRF_oH_qM4JqyeA/viewform?usp=header",
            inline=False
        )
        embed.add_field(
            name="⏰ Fermeture",
            value="Ce canal sera supprimé dans 10 secondes.",
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
    try:
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        existing_ticket = discord.utils.get(interaction.guild.channels, 
                                         name=f"ticket-{interaction.user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(
                f"❌ Vous avez déjà un ticket ouvert : {existing_ticket.mention}",
                ephemeral=True
            )
            return
        
        # Récupérer la catégorie
        category_id = TICKET_CATEGORIES.get(ticket_type)
        if not category_id:
            await interaction.response.send_message("❌ Type de ticket invalide.", ephemeral=True)
            return
        
        category = interaction.guild.get_channel(category_id)
        if not category:
            await interaction.response.send_message("❌ Catégorie de tickets introuvable.", ephemeral=True)
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
            title="🎫 Ticket Créé",
            description=f"Bienvenue {interaction.user.mention} ! Votre ticket a été créé.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Type", value=ticket_type.replace("_", " ").title(), inline=True)
        embed.add_field(name="Créé par", value=interaction.user.mention, inline=True)
        embed.add_field(name="ID Ticket", value=f"ticket-{ticket_channel.id}", inline=True)
        
        # Créer la vue de contrôle
        control_view = TicketControlView()
        
        await ticket_channel.send(embed=embed, view=control_view)
        await interaction.response.send_message(
            f"✅ Votre ticket a été créé : {ticket_channel.mention}",
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
        
        # Créer l'embed du panel
        embed = discord.Embed(
            title="🎫 Système de Tickets Seykoofx",
            description="Bienvenue ! Créez un ticket en cliquant sur l'un des boutons ci-dessous.",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="🛒 Commande",
            value="Pour passer une commande ou demander un devis",
            inline=True
        )
        embed.add_field(
            name="🎧 Service Client",
            value="Pour toute question ou problème technique",
            inline=True
        )
        embed.add_field(
            name="👥 Nous Rejoindre",
            value="Pour postuler ou rejoindre l'équipe",
            inline=True
        )
        embed.add_field(
            name="📋 Informations",
            value="Un membre de l'équipe vous répondra dans les plus brefs délais.",
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