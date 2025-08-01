"""
Système de Règlement - Seykoofx
===============================

Système de règlement avec bouton d'acceptation
Version bilingue (Français/English)
"""

import discord
from discord.ext import commands
from datetime import datetime

# Messages bilingues
MESSAGES = {
    "fr": {
        "role_not_found": "❌ Rôle membre introuvable.",
        "already_accepted": "✅ Vous avez déjà accepté le règlement.",
        "reglement_accepted": "✅ Règlement Accepté",
        "reglement_accepted_desc": "Bienvenue {user} ! Vous avez accepté le règlement officiel.",
        "access": "🎯 Accès",
        "access_desc": "Vous avez maintenant accès à tous les canaux du serveur.",
        "reglement_reminder": "📋 Règlement",
        "reglement_reminder_desc": "N'oubliez pas de respecter le règlement en toutes circonstances.",
        "accept_error": "❌ Erreur lors de l'acceptation : {error}",
        "panel_title": "📜 Règlement Officiel Seykoofx",
        "panel_desc": "Bienvenue ! Avant d'accéder au serveur, veuillez lire et accepter notre règlement officiel.",
        "reglement_link": "📋 Règlement",
        "reglement_link_desc": "https://drive.google.com/file/d/122Aw0dZTAfHs42lNXHGk71yyeN9pjkOa/view?usp=drive_link",
        "acceptance": "✅ Acceptation",
        "acceptance_desc": "En cliquant sur le bouton ci-dessous, vous acceptez de respecter le règlement de l'entreprise.",
        "access_info": "🎯 Accès",
        "access_info_desc": "Après acceptation, vous obtiendrez le rôle membre et l'accès à tous les canaux.",
        "footer": "Seykoofx - Règlement Officiel",
        "button_label": "✅ Accepter le Règlement"
    },
    "en": {
        "role_not_found": "❌ Member role not found.",
        "already_accepted": "✅ You have already accepted the rules.",
        "reglement_accepted": "✅ Rules Accepted",
        "reglement_accepted_desc": "Welcome {user}! You have accepted the official rules.",
        "access": "🎯 Access",
        "access_desc": "You now have access to all server channels.",
        "reglement_reminder": "📋 Rules",
        "reglement_reminder_desc": "Remember to respect the rules at all times.",
        "accept_error": "❌ Error during acceptance: {error}",
        "panel_title": "📜 Official Seykoofx Rules",
        "panel_desc": "Welcome! Before accessing the server, please read and accept our official rules.",
        "reglement_link": "📋 Rules",
        "reglement_link_desc": "https://drive.google.com/file/d/122Aw0dZTAfHs42lNXHGk71yyeN9pjkOa/view?usp=drive_link",
        "acceptance": "✅ Acceptance",
        "acceptance_desc": "By clicking the button below, you agree to respect the company's rules.",
        "access_info": "🎯 Access",
        "access_info_desc": "After acceptance, you will receive the member role and access to all channels.",
        "footer": "Seykoofx - Official Rules",
        "button_label": "✅ Accept Rules"
    }
}

def get_language(user: discord.Member) -> str:
    """Détecte la langue de l'utilisateur (simplifié)"""
    # Pour l'instant, on utilise français par défaut
    return "fr"

def get_message(key: str, lang: str = "fr", **kwargs) -> str:
    """Récupère un message dans la langue spécifiée"""
    message = MESSAGES[lang].get(key, key)
    return message.format(**kwargs) if kwargs else message

# Configuration du canal de règlement
REGLEMENT_CHANNEL_ID = 1005763703750279183

# Rôle membre à donner après acceptation
MEMBER_ROLE_ID = 1005763703335034975

class ReglementView(discord.ui.View):
    """Vue avec le bouton d'acceptation du règlement"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Accepter le Règlement", style=discord.ButtonStyle.success, custom_id="accept_reglement")
    async def accept_reglement(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_language(interaction.user)
        
        try:
            # Vérifier si l'utilisateur a déjà le rôle
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            if not member_role:
                await interaction.response.send_message(get_message("role_not_found", lang), ephemeral=True)
                return
            
            if member_role in interaction.user.roles:
                await interaction.response.send_message(get_message("already_accepted", lang), ephemeral=True)
                return
            
            # Donner le rôle membre
            await interaction.user.add_roles(member_role)
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title=get_message("reglement_accepted", lang),
                description=get_message("reglement_accepted_desc", lang, user=interaction.user.mention),
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name=get_message("access", lang),
                value=get_message("access_desc", lang),
                inline=False
            )
            embed.add_field(
                name=get_message("reglement_reminder", lang),
                value=get_message("reglement_reminder_desc", lang),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log l'acceptation
            try:
                from logs import log_ticket_action
                await log_ticket_action(
                    interaction.guild,
                    "règlement_accepté",
                    interaction.user,
                    f"user-{interaction.user.id}"
                )
            except Exception as e:
                print(f"❌ Erreur log règlement: {e}")
            
        except Exception as e:
            await interaction.response.send_message(get_message("accept_error", lang, error=e), ephemeral=True)

async def create_reglement_panel(bot, guild):
    """Crée le panel de règlement"""
    try:
        # Récupérer le canal de règlement
        reglement_channel = guild.get_channel(REGLEMENT_CHANNEL_ID)
        if not reglement_channel:
            print("❌ Canal de règlement introuvable")
            return
        
        # Supprimer les anciens messages
        try:
            await reglement_channel.purge()
        except:
            pass
        
        # Créer l'embed du règlement (version française par défaut)
        embed = discord.Embed(
            title=get_message("panel_title", "fr"),
            description=get_message("panel_desc", "fr"),
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name=get_message("reglement_link", "fr"),
            value=get_message("reglement_link_desc", "fr"),
            inline=False
        )
        embed.add_field(
            name=get_message("acceptance", "fr"),
            value=get_message("acceptance_desc", "fr"),
            inline=False
        )
        embed.add_field(
            name=get_message("access_info", "fr"),
            value=get_message("access_info_desc", "fr"),
            inline=False
        )
        embed.set_footer(text=get_message("footer", "fr"))
        
        # Créer la vue avec le bouton
        view = ReglementView()
        
        await reglement_channel.send(embed=embed, view=view)
        print(f"✅ Panel de règlement envoyé dans #{reglement_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel règlement: {e}")

def setup_reglement_system(bot):
    """Configure le système de règlement"""
    print("✅ Système de règlement configuré") 