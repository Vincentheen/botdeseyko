"""
Système de Vérification - Seykoofx
==================================

Système de vérification avec bouton "Je suis un humain"
Version bilingue (Français/English)
"""

import discord
from discord.ext import commands
from datetime import datetime

# Messages bilingues
MESSAGES = {
    "fr": {
        "role_not_found": "❌ Rôle membre introuvable.",
        "already_verified": "✅ Vous êtes déjà vérifié.",
        "verification_success": "✅ Vérification Réussie",
        "verification_success_desc": "Bienvenue {user} ! Votre vérification a été confirmée.",
        "next_steps": "📋 Prochaines étapes",
        "next_steps_desc": "1. Allez dans le canal règlement\n2. Acceptez le règlement officiel\n3. Accédez à tous les canaux",
        "access": "🎯 Accès",
        "access_desc": "Vous pouvez maintenant accéder au canal règlement pour continuer.",
        "verification_error": "❌ Erreur lors de la vérification : {error}",
        "panel_title": "🔐 Vérification Humaine",
        "panel_desc": "Pour accéder au serveur, vous devez confirmer que vous êtes un humain.",
        "instructions": "📋 Instructions",
        "instructions_desc": "1. Cliquez sur le bouton ci-dessous\n2. Allez dans le canal règlement\n3. Acceptez le règlement officiel",
        "important": "⚠️ Important",
        "important_desc": "Seuls les humains peuvent accéder à ce serveur. Les bots ne sont pas autorisés.",
        "footer": "Seykoofx - Vérification de sécurité",
        "button_label": "✅ Je suis un humain"
    },
    "en": {
        "role_not_found": "❌ Member role not found.",
        "already_verified": "✅ You are already verified.",
        "verification_success": "✅ Verification Successful",
        "verification_success_desc": "Welcome {user}! Your verification has been confirmed.",
        "next_steps": "📋 Next Steps",
        "next_steps_desc": "1. Go to the rules channel\n2. Accept the official rules\n3. Access all channels",
        "access": "🎯 Access",
        "access_desc": "You can now access the rules channel to continue.",
        "verification_error": "❌ Error during verification: {error}",
        "panel_title": "🔐 Human Verification",
        "panel_desc": "To access the server, you must confirm that you are human.",
        "instructions": "📋 Instructions",
        "instructions_desc": "1. Click the button below\n2. Go to the rules channel\n3. Accept the official rules",
        "important": "⚠️ Important",
        "important_desc": "Only humans can access this server. Bots are not allowed.",
        "footer": "Seykoofx - Security Verification",
        "button_label": "✅ I am human"
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

# Configuration du canal de vérification
VERIFICATION_CHANNEL_ID = 1400139457675661412

# Rôle membre à donner après vérification
MEMBER_ROLE_ID = 1005763703335034975

class VerificationView(discord.ui.View):
    """Vue avec le bouton de vérification"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Je suis un humain", style=discord.ButtonStyle.success, custom_id="verify_human")
    async def verify_human(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_language(interaction.user)
        
        try:
            # Vérifier si l'utilisateur a déjà le rôle
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            if not member_role:
                await interaction.response.send_message(get_message("role_not_found", lang), ephemeral=True)
                return
            
            if member_role in interaction.user.roles:
                await interaction.response.send_message(get_message("already_verified", lang), ephemeral=True)
                return
            
            # Créer l'embed de vérification
            embed = discord.Embed(
                title=get_message("verification_success", lang),
                description=get_message("verification_success_desc", lang, user=interaction.user.mention),
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name=get_message("next_steps", lang),
                value=get_message("next_steps_desc", lang),
                inline=False
            )
            embed.add_field(
                name=get_message("access", lang),
                value=get_message("access_desc", lang),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log la vérification
            try:
                from logs import log_ticket_action
                await log_ticket_action(
                    interaction.guild,
                    "vérifié",
                    interaction.user,
                    f"user-{interaction.user.id}"
                )
            except Exception as e:
                print(f"❌ Erreur log vérification: {e}")
            
        except Exception as e:
            await interaction.response.send_message(get_message("verification_error", lang, error=e), ephemeral=True)

async def create_verification_panel(bot, guild):
    """Crée le panel de vérification"""
    try:
        # Récupérer le canal de vérification
        verification_channel = guild.get_channel(VERIFICATION_CHANNEL_ID)
        if not verification_channel:
            print("❌ Canal de vérification introuvable")
            return
        
        # Supprimer les anciens messages
        try:
            await verification_channel.purge()
        except:
            pass
        
        # Créer l'embed de vérification (version française par défaut)
        embed = discord.Embed(
            title=get_message("panel_title", "fr"),
            description=get_message("panel_desc", "fr"),
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name=get_message("instructions", "fr"),
            value=get_message("instructions_desc", "fr"),
            inline=False
        )
        embed.add_field(
            name=get_message("important", "fr"),
            value=get_message("important_desc", "fr"),
            inline=False
        )
        embed.set_footer(text=get_message("footer", "fr"))
        
        # Créer la vue avec le bouton
        view = VerificationView()
        
        await verification_channel.send(embed=embed, view=view)
        print(f"✅ Panel de vérification envoyé dans #{verification_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel vérification: {e}")

def setup_verification_system(bot):
    """Configure le système de vérification"""
    print("✅ Système de vérification configuré") 