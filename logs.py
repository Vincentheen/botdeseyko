"""
Système de Logs Simplifié - Seykoofx
====================================

Système de logs uniquement pour les tickets
"""

import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration des canaux de logs
TICKET_LOG_CHANNEL_ID = 1400115679775948963  # Canal des logs de tickets

class LogManager:
    """Gestionnaire centralisé des logs"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def log_ticket_action(self, guild, action: str, user: discord.Member, ticket_id: str, **kwargs):
        """Log une action de ticket"""
        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if not log_channel:
            print(f"❌ Canal ticket introuvable (ID: {TICKET_LOG_CHANNEL_ID})")
            return
        
        # Couleurs selon l'action
        colors = {
            "créé": 0x00ff00,      # Vert
            "fermé": 0xff0000,      # Rouge
            "réouvert": 0x0099ff,   # Bleu
            "supprimé": 0xff8800,   # Orange
        }
        
        embed = discord.Embed(
            title="🎫 Log Ticket",
            description=f"**Action:** {action}",
            color=colors.get(action.lower(), 0x0099ff),
            timestamp=datetime.now()
        )
        embed.add_field(name="Utilisateur", value=user.mention, inline=True)
        embed.add_field(name="ID Ticket", value=ticket_id, inline=True)
        embed.add_field(name="ID Utilisateur", value=user.id, inline=True)
        
        # Ajouter des champs supplémentaires selon l'action
        if "reason" in kwargs:
            embed.add_field(name="Raison", value=kwargs["reason"], inline=False)
        
        if "channel" in kwargs:
            embed.add_field(name="Canal", value=kwargs["channel"].mention, inline=True)
        
        if "duration" in kwargs:
            embed.add_field(name="Durée", value=kwargs["duration"], inline=True)
        
        try:
            await log_channel.send(embed=embed)
            print(f"✅ Log ticket envoyé: {action} pour {user.name}")
        except Exception as e:
            print(f"❌ Erreur envoi log ticket: {e}")

# Instance globale du gestionnaire de logs
log_manager = None

def setup_logs_system(bot):
    """Configure le système de logs"""
    global log_manager
    log_manager = LogManager(bot)
    print("📊 Système de logs configuré")

# Fonctions utilitaires pour les logs
async def log_ticket_action(guild, action: str, user: discord.Member, ticket_id: str, **kwargs):
    """Log une action de ticket"""
    if log_manager:
        await log_manager.log_ticket_action(guild, action, user, ticket_id, **kwargs) 
