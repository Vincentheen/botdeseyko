"""
Système de Vérification - Seykoofx
==================================

Système de vérification avec bouton "Je suis un humain"
"""

import discord
from discord.ext import commands
from datetime import datetime

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
        try:
            # Vérifier si l'utilisateur a déjà le rôle
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            if not member_role:
                await interaction.response.send_message("❌ Rôle membre introuvable.", ephemeral=True)
                return
            
            if member_role in interaction.user.roles:
                await interaction.response.send_message("✅ Vous êtes déjà vérifié.", ephemeral=True)
                return
            
            # Créer l'embed de vérification
            embed = discord.Embed(
                title="✅ Vérification Réussie",
                description=f"Bienvenue {interaction.user.mention} ! Votre vérification a été confirmée.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📋 Prochaines étapes",
                value="1. Allez dans le canal règlement\n2. Acceptez le règlement officiel\n3. Accédez à tous les canaux",
                inline=False
            )
            embed.add_field(
                name="🎯 Accès",
                value="Vous pouvez maintenant accéder au canal règlement pour continuer.",
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
            await interaction.response.send_message(f"❌ Erreur lors de la vérification : {e}", ephemeral=True)

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
        
        # Créer l'embed de vérification
        embed = discord.Embed(
            title="🔐 Vérification Humaine",
            description="Pour accéder au serveur, vous devez confirmer que vous êtes un humain.",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📋 Instructions",
            value="1. Cliquez sur le bouton ci-dessous\n2. Allez dans le canal règlement\n3. Acceptez le règlement officiel",
            inline=False
        )
        embed.add_field(
            name="⚠️ Important",
            value="Seuls les humains peuvent accéder à ce serveur. Les bots ne sont pas autorisés.",
            inline=False
        )
        embed.set_footer(text="Seykoofx - Vérification de sécurité")
        
        # Créer la vue avec le bouton
        view = VerificationView()
        
        await verification_channel.send(embed=embed, view=view)
        print(f"✅ Panel de vérification envoyé dans #{verification_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel vérification: {e}")

def setup_verification_system(bot):
    """Configure le système de vérification"""
    print("✅ Système de vérification configuré") 