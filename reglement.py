"""
Système de Règlement - Seykoofx
===============================

Système de règlement avec bouton d'acceptation
"""

import discord
from discord.ext import commands
from datetime import datetime

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
        try:
            # Vérifier si l'utilisateur a déjà le rôle
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            if not member_role:
                await interaction.response.send_message("❌ Rôle membre introuvable.", ephemeral=True)
                return
            
            if member_role in interaction.user.roles:
                await interaction.response.send_message("✅ Vous avez déjà accepté le règlement.", ephemeral=True)
                return
            
            # Donner le rôle membre
            await interaction.user.add_roles(member_role)
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Règlement Accepté",
                description=f"Bienvenue {interaction.user.mention} ! Vous avez accepté le règlement officiel.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="🎯 Accès",
                value="Vous avez maintenant accès à tous les canaux du serveur.",
                inline=False
            )
            embed.add_field(
                name="📋 Règlement",
                value="N'oubliez pas de respecter le règlement en toutes circonstances.",
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
            await interaction.response.send_message(f"❌ Erreur lors de l'acceptation : {e}", ephemeral=True)

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
        
        # Créer l'embed du règlement
        embed = discord.Embed(
            title="📜 Règlement Officiel Seykoofx",
            description="Bienvenue ! Avant d'accéder au serveur, veuillez lire et accepter notre règlement officiel.",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📋 Règlement",
            value="https://drive.google.com/file/d/122Aw0dZTAfHs42lNXHGk71yyeN9pjkOa/view?usp=drive_link",
            inline=False
        )
        embed.add_field(
            name="✅ Acceptation",
            value="En cliquant sur le bouton ci-dessous, vous acceptez de respecter le règlement de l'entreprise.",
            inline=False
        )
        embed.add_field(
            name="🎯 Accès",
            value="Après acceptation, vous obtiendrez le rôle membre et l'accès à tous les canaux.",
            inline=False
        )
        embed.set_footer(text="Seykoofx - Règlement Officiel")
        
        # Créer la vue avec le bouton
        view = ReglementView()
        
        await reglement_channel.send(embed=embed, view=view)
        print(f"✅ Panel de règlement envoyé dans #{reglement_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel règlement: {e}")

def setup_reglement_system(bot):
    """Configure le système de règlement"""
    print("✅ Système de règlement configuré") 