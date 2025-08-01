"""
Correction des événements de logs - Seykoofx
===========================================

Script pour corriger le problème des événements de logs qui ne se déclenchent pas
"""

import discord
from discord.ext import commands
import os
from datetime import datetime

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'VOTRE_TOKEN_BOT')
DISCORD_GUILD_ID = '1005763703335034970'

# Configuration des canaux de logs
VOICE_LOG_CHANNEL_ID = 1400614430336614511
MODERATION_LOG_CHANNEL_ID = 1400614542538707097

# Configuration du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Instance globale du gestionnaire de logs
log_manager = None

class LogManager:
    """Gestionnaire centralisé des logs"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def log_voice_action(self, guild, action: str, user: discord.Member, details: str = "", **kwargs):
        """Log une action vocale"""
        log_channel = guild.get_channel(VOICE_LOG_CHANNEL_ID)
        if not log_channel:
            print(f"❌ Canal vocal introuvable (ID: {VOICE_LOG_CHANNEL_ID})")
            return
        
        # Couleurs selon l'action
        colors = {
            "rejoint": 0x00ff00,  # Vert
            "quitté": 0xff0000,   # Rouge
            "mute": 0xffff00,     # Jaune
            "unmute": 0x00ff00,   # Vert
            "deaf": 0xff8800,     # Orange
            "undeaf": 0x00ff00,   # Vert
            "déplacé": 0x0099ff,  # Bleu
            "stream": 0x9932cc,   # Violet
            "stop_stream": 0x9932cc,  # Violet
        }
        
        embed = discord.Embed(
            title="🎤 Log Vocal",
            description=f"**Action:** {action}",
            color=colors.get(action.lower(), 0x0099ff),
            timestamp=datetime.now()
        )
        embed.add_field(name="Utilisateur", value=user.mention, inline=True)
        embed.add_field(name="ID Utilisateur", value=user.id, inline=True)
        
        if details:
            embed.add_field(name="Détails", value=details, inline=False)
        
        # Ajouter des champs supplémentaires selon l'action
        if "channel" in kwargs:
            embed.add_field(name="Canal", value=kwargs["channel"].mention, inline=True)
        
        if "duration" in kwargs:
            embed.add_field(name="Durée", value=kwargs["duration"], inline=True)
        
        if "reason" in kwargs:
            embed.add_field(name="Raison", value=kwargs["reason"], inline=True)
        
        try:
            await log_channel.send(embed=embed)
            print(f"✅ Log vocal envoyé: {action}")
        except Exception as e:
            print(f"❌ Erreur envoi log vocal: {e}")
    
    async def log_moderation_action(self, guild, action: str, moderator: discord.Member, target: discord.Member, **kwargs):
        """Log une action de modération"""
        log_channel = guild.get_channel(MODERATION_LOG_CHANNEL_ID)
        if not log_channel:
            print(f"❌ Canal modération introuvable (ID: {MODERATION_LOG_CHANNEL_ID})")
            return
        
        # Couleurs selon l'action
        colors = {
            "kick": 0xff8800,     # Orange
            "ban": 0xff0000,       # Rouge
            "unban": 0x00ff00,     # Vert
            "timeout": 0xffff00,   # Jaune
            "role_add": 0x00ff00,  # Vert
            "role_remove": 0xff8800,  # Orange
            "message_delete": 0xff0000,  # Rouge
            "message_edit": 0xffff00,    # Jaune
            "channel_create": 0x00ff00,  # Vert
            "channel_delete": 0xff0000,  # Rouge
            "channel_edit": 0xffff00,    # Jaune
        }
        
        embed = discord.Embed(
            title="🛡️ Log Modération",
            description=f"**Action:** {action}",
            color=colors.get(action.lower(), 0x0099ff),
            timestamp=datetime.now()
        )
        embed.add_field(name="Modérateur", value=moderator.mention, inline=True)
        embed.add_field(name="Cible", value=target.mention, inline=True)
        embed.add_field(name="ID Modérateur", value=moderator.id, inline=True)
        embed.add_field(name="ID Cible", value=target.id, inline=True)
        
        # Ajouter des champs supplémentaires selon l'action
        if "reason" in kwargs:
            embed.add_field(name="Raison", value=kwargs["reason"], inline=False)
        
        if "duration" in kwargs:
            embed.add_field(name="Durée", value=kwargs["duration"], inline=True)
        
        if "role" in kwargs:
            embed.add_field(name="Rôle", value=kwargs["role"].mention, inline=True)
        
        if "channel" in kwargs:
            embed.add_field(name="Canal", value=kwargs["channel"].mention, inline=True)
        
        if "message_content" in kwargs:
            embed.add_field(name="Contenu", value=kwargs["message_content"][:1000], inline=False)
        
        if "old_content" in kwargs:
            embed.add_field(name="Ancien contenu", value=kwargs["old_content"][:1000], inline=False)
        
        if "new_content" in kwargs:
            embed.add_field(name="Nouveau contenu", value=kwargs["new_content"][:1000], inline=False)
        
        try:
            await log_channel.send(embed=embed)
            print(f"✅ Log modération envoyé: {action}")
        except Exception as e:
            print(f"❌ Erreur envoi log modération: {e}")

def setup_logs_system(bot):
    """Configure le système de logs"""
    global log_manager
    log_manager = LogManager(bot)
    print("📊 Système de logs configuré")

@bot.event
async def on_ready():
    """Événement quand le bot est prêt"""
    print(f"🤖 Bot connecté en tant que {bot.user}")
    
    # Récupérer le serveur
    guild = bot.get_guild(int(DISCORD_GUILD_ID))
    if not guild:
        print("❌ Serveur Discord non trouvé")
        return
    
    print(f"📡 Serveur trouvé: {guild.name}")
    
    # Configuration du système de logs
    setup_logs_system(bot)
    
    print("\n🔍 Test des événements de logs...")
    print("Pour tester les événements:")
    print("1. Rejoignez un canal vocal")
    print("2. Quittez le canal vocal")
    print("3. Mutez-vous dans le vocal")
    print("4. Supprimez un message")
    print("5. Éditez un message")
    print("6. Ajoutez un rôle à quelqu'un")

@bot.event
async def on_member_join(member):
    """Événement quand un membre rejoint"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"🎉 Membre rejoint: {member.name}")
        if log_manager:
            await log_manager.log_moderation_action(
                member.guild,
                "join_server",
                member.guild.me,
                member,
                reason="Membre a rejoint le serveur"
            )

@bot.event
async def on_member_remove(member):
    """Événement quand un membre quitte"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"👋 Membre parti: {member.name}")
        if log_manager:
            await log_manager.log_moderation_action(
                member.guild,
                "quit_server",
                member.guild.me,
                member,
                reason="Membre a quitté le serveur"
            )

@bot.event
async def on_member_update(before, after):
    """Événement quand un membre est mis à jour"""
    if str(after.guild.id) == DISCORD_GUILD_ID:
        print(f"👤 Membre mis à jour: {after.name}")
        
        # Vérifier les changements de rôles
        before_roles = set(role.id for role in before.roles)
        after_roles = set(role.id for role in after.roles)
        
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles
        
        if added_roles:
            print(f"➕ Rôles ajoutés: {added_roles}")
            if log_manager:
                for role_id in added_roles:
                    role = after.guild.get_role(role_id)
                    if role:
                        await log_manager.log_moderation_action(
                            after.guild,
                            "role_add",
                            after.guild.me,
                            after,
                            role=role,
                            reason="Rôle ajouté"
                        )
        
        if removed_roles:
            print(f"➖ Rôles retirés: {removed_roles}")
            if log_manager:
                for role_id in removed_roles:
                    role = after.guild.get_role(role_id)
                    if role:
                        await log_manager.log_moderation_action(
                            after.guild,
                            "role_remove",
                            after.guild.me,
                            after,
                            role=role,
                            reason="Rôle retiré"
                        )
        
        # Vérifier les changements vocaux
        if before.voice and after.voice:
            if before.voice.mute != after.voice.mute:
                action = "unmute" if after.voice.mute else "mute"
                if log_manager:
                    await log_manager.log_voice_action(
                        after.guild,
                        action,
                        after,
                        f"État mute changé: {before.voice.mute} → {after.voice.mute}"
                    )
            
            if before.voice.deaf != after.voice.deaf:
                action = "undeaf" if after.voice.deaf else "deaf"
                if log_manager:
                    await log_manager.log_voice_action(
                        after.guild,
                        action,
                        after,
                        f"État deaf changé: {before.voice.deaf} → {after.voice.deaf}"
                    )
            
            if before.voice.channel != after.voice.channel:
                if log_manager:
                    await log_manager.log_voice_action(
                        after.guild,
                        "déplacé",
                        after,
                        f"Déplacé de {before.voice.channel.name} vers {after.voice.channel.name}",
                        channel=after.voice.channel
                    )
        
        elif not before.voice and after.voice:
            if log_manager:
                await log_manager.log_voice_action(
                    after.guild,
                    "rejoint",
                    after,
                    f"A rejoint {after.voice.channel.name}",
                    channel=after.voice.channel
                )
        
        elif before.voice and not after.voice:
            if log_manager:
                await log_manager.log_voice_action(
                    before.guild,
                    "quitté",
                    before,
                    f"A quitté {before.voice.channel.name}",
                    channel=before.voice.channel
                )

@bot.event
async def on_voice_state_update(member, before, after):
    """Événement quand l'état vocal change"""
    if str(member.guild.id) == DISCORD_GUILD_ID:
        print(f"🎤 État vocal changé: {member.name}")
        
        if before and after:
            if before.self_stream != after.self_stream:
                action = "stop_stream" if before.self_stream else "stream"
                if log_manager:
                    await log_manager.log_voice_action(
                        member.guild,
                        action,
                        member,
                        f"Stream: {before.self_stream} → {after.self_stream}",
                        channel=after.channel
                    )

@bot.event
async def on_message_delete(message):
    """Événement quand un message est supprimé"""
    if message.guild and str(message.guild.id) == DISCORD_GUILD_ID and not message.author.bot:
        print(f"🗑️ Message supprimé: {message.author.name}")
        if log_manager:
            await log_manager.log_moderation_action(
                message.guild,
                "message_delete",
                message.guild.me,
                message.author,
                channel=message.channel,
                message_content=message.content,
                reason="Message supprimé"
            )

@bot.event
async def on_message_edit(before, after):
    """Événement quand un message est édité"""
    if before.guild and str(before.guild.id) == DISCORD_GUILD_ID and not before.author.bot and before.content != after.content:
        print(f"✏️ Message édité: {before.author.name}")
        if log_manager:
            await log_manager.log_moderation_action(
                before.guild,
                "message_edit",
                before.guild.me,
                before.author,
                channel=before.channel,
                old_content=before.content,
                new_content=after.content
            )

@bot.command(name='test_correction')
async def test_correction_command(ctx):
    """Teste la correction des événements"""
    embed = discord.Embed(
        title="🔧 Test de Correction",
        description="Test des événements corrigés",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    # Test d'envoi de logs
    if log_manager:
        try:
            await log_manager.log_voice_action(
                ctx.guild,
                "test_correction",
                ctx.author,
                "Test de correction",
                channel=ctx.channel
            )
            embed.add_field(name="✅ Log Vocal", value="Test réussi", inline=True)
        except Exception as e:
            embed.add_field(name="❌ Log Vocal", value=f"Erreur: {e}", inline=True)
        
        try:
            await log_manager.log_moderation_action(
                ctx.guild,
                "test_correction",
                ctx.author,
                ctx.author,
                reason="Test de correction"
            )
            embed.add_field(name="✅ Log Modération", value="Test réussi", inline=True)
        except Exception as e:
            embed.add_field(name="❌ Log Modération", value=f"Erreur: {e}", inline=True)
    else:
        embed.add_field(name="❌ Log Manager", value="Non initialisé", inline=True)
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN) 