"""
Système de Contrôle Seykooteam - Seykoofx
==========================================

Système permettant aux membres de l'équipe de prendre possession
du compte Seykooteam via un système de boutons avec authentification
"""

import discord
from discord.ext import commands
from datetime import datetime

# Configuration
SEYKOOTEAM_CHANNEL_ID = 1435643776419889183
SEYKOOTEAM_ACCOUNT_ID = 1435599551972249670
SEYKOOTEAM_LOG_CHANNEL_ID = 1435652718462242877  # Channel de logs
DEFAULT_ROLE_ID = 1400606089082437853  # Rôle par défaut à conserver
DEFAULT_ROLE_2_ID = 1005763703335034975  # Deuxième rôle par défaut à conserver

# Configuration des membres de l'équipe
# Format: {"nom": {"roles": [liste_des_ids], "password": "mot_de_passe", "label": "Label affiché (optionnel)"}}
TEAM_MEMBERS = {
    "josh": {
        "roles": [
            1288085709990658088,
            1005763703397941345,
            1335705793697288213,
            1400424737942933666,
            1113214565619085424,
            1081612566696046652,
            1422281872913731657,
            1400606089082437853,
            1081612511561908256
        ],
        "password": "josh2024",  # À changer selon vos besoins
        "label": "Josh"  # Label affiché sur le bouton (optionnel, utilise la clé si non défini)
    },
    "margaux8": {
        "roles": [
            1005763703397941345,
            1420379353610457098,
            1081612566696046652,
            1400606089082437853,
            1005763703335034975
        ],
        "password": "margaux2024",  # À changer selon vos besoins
        "label": "M𝔞𝔯𝔤𝔞𝔲𝔵 8"  # Label avec caractères spéciaux
    },
    # Les autres membres seront ajoutés plus tard
}

def is_seykooteam_account(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur est le compte Seykooteam"""
    return user.id == SEYKOOTEAM_ACCOUNT_ID

async def log_seykooteam_action(guild, action: str, member_name: str = None, details: str = None, **kwargs):
    """Log une action du compte Seykooteam"""
    log_channel = guild.get_channel(SEYKOOTEAM_LOG_CHANNEL_ID)
    if not log_channel:
        print(f"❌ Canal de logs Seykooteam introuvable (ID: {SEYKOOTEAM_LOG_CHANNEL_ID})")
        return
    
    # Couleurs selon l'action
    colors = {
        "connexion": 0x00ff00,      # Vert
        "déconnexion": 0xff0000,    # Rouge
        "message": 0x0099ff,         # Bleu
        "modification": 0xffff00,    # Jaune
    }
    
    embed = discord.Embed(
        title="🎮 Log Seykooteam",
        description=f"**Action:** {action}",
        color=colors.get(action.lower(), 0x0099ff),
        timestamp=datetime.now()
    )
    
    # Ajouter les informations selon l'action
    if member_name:
        embed.add_field(name="👤 Membre", value=member_name, inline=True)
    
    if details:
        embed.add_field(name="📋 Détails", value=details, inline=False)
    
    # Ajouter des champs supplémentaires
    if "channel" in kwargs:
        embed.add_field(name="📍 Channel", value=kwargs["channel"].mention, inline=True)
    
    if "roles" in kwargs:
        roles_list = ", ".join([role.mention for role in kwargs["roles"]]) if kwargs["roles"] else "Aucun"
        embed.add_field(name="📋 Rôles", value=roles_list if len(roles_list) < 1024 else f"{len(kwargs['roles'])} rôles", inline=False)
    
    if "nickname" in kwargs:
        embed.add_field(name="🏷️ Nom", value=kwargs["nickname"], inline=True)
    
    if "message_content" in kwargs:
        content = kwargs["message_content"][:1000] + "..." if len(kwargs["message_content"]) > 1000 else kwargs["message_content"]
        embed.add_field(name="💬 Message", value=content, inline=False)
    
    embed.set_footer(text="Seykooteam - Système de logs")
    
    try:
        await log_channel.send(embed=embed)
        print(f"✅ Log Seykooteam envoyé: {action}")
    except Exception as e:
        print(f"❌ Erreur envoi log Seykooteam: {e}")

class PasswordModal(discord.ui.Modal, title="Authentification"):
    """Modal pour saisir le mot de passe"""
    
    def __init__(self, member_name: str, member_config: dict):
        super().__init__()
        self.member_name = member_name
        self.member_config = member_config
        self.password_input = discord.ui.TextInput(
            label="Mot de passe",
            placeholder="Entrez votre mot de passe...",
            min_length=3,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.password_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Vérifie le mot de passe et applique les rôles"""
        # Vérifier que c'est bien le compte Seykooteam qui interagit
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Vérifier le mot de passe
        if self.password_input.value != self.member_config["password"]:
            await interaction.response.send_message(
                "❌ Mot de passe incorrect.",
                ephemeral=True
            )
            return
        
        # Récupérer le membre Seykooteam
        seykooteam_member = interaction.guild.get_member(SEYKOOTEAM_ACCOUNT_ID)
        if not seykooteam_member:
            await interaction.response.send_message(
                "❌ Compte Seykooteam introuvable sur le serveur.",
                ephemeral=True
            )
            return
        
        try:
            # Retirer tous les rôles sauf le rôle par défaut
            default_role = interaction.guild.get_role(DEFAULT_ROLE_ID)
            roles_to_keep = [default_role] if default_role else []
            
            # Récupérer les nouveaux rôles à ajouter
            new_roles = []
            for role_id in self.member_config["roles"]:
                role = interaction.guild.get_role(role_id)
                if role:
                    new_roles.append(role)
            
            # Appliquer les rôles
            await seykooteam_member.edit(roles=new_roles)
            
            # Renommer le compte avec le nom du membre
            new_nickname = f"seykooteam-{self.member_name}"
            try:
                await seykooteam_member.edit(nick=new_nickname)
            except Exception as e:
                print(f"⚠️ Erreur lors du renommage: {e}")
            
            # Logger l'action
            await log_seykooteam_action(
                interaction.guild,
                "connexion",
                member_name=self.member_name,
                details=f"Connexion réussie pour {self.member_name}",
                roles=new_roles,
                nickname=new_nickname
            )
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Connexion réussie",
                description=f"Le compte Seykooteam a été configuré pour **{self.member_name}**.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="👤 Membre",
                value=self.member_name,
                inline=True
            )
            embed.add_field(
                name="🔑 Authentification",
                value="✅ Validé",
                inline=True
            )
            embed.add_field(
                name="📋 Rôles appliqués",
                value=f"{len(new_roles)} rôles",
                inline=False
            )
            embed.set_footer(text="Seykooteam - Système de contrôle")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de l'application des rôles: {e}",
                ephemeral=True
            )


class MemberButton(discord.ui.Button):
    """Bouton personnalisé pour un membre"""
    
    def __init__(self, member_name: str, member_config: dict, row: int):
        # Utiliser le label personnalisé si disponible, sinon utiliser le nom capitalisé
        label = member_config.get("label", member_name.capitalize())
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=f"seykooteam_{member_name}",
            row=row
        )
        self.member_name = member_name
        self.member_config = member_config
    
    async def callback(self, interaction: discord.Interaction):
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Afficher le modal de mot de passe
        modal = PasswordModal(self.member_name, self.member_config)
        await interaction.response.send_modal(modal)

class DisconnectButton(discord.ui.Button):
    """Bouton de déconnexion"""
    
    def __init__(self, row: int):
        super().__init__(
            label="🔴 Déconnecter",
            style=discord.ButtonStyle.danger,
            custom_id="seykooteam_disconnect",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Récupérer le membre Seykooteam
        seykooteam_member = interaction.guild.get_member(SEYKOOTEAM_ACCOUNT_ID)
        if not seykooteam_member:
            await interaction.response.send_message(
                "❌ Compte Seykooteam introuvable sur le serveur.",
                ephemeral=True
            )
            return
        
        try:
            # Récupérer les rôles par défaut
            default_role = interaction.guild.get_role(DEFAULT_ROLE_ID)
            default_role_2 = interaction.guild.get_role(DEFAULT_ROLE_2_ID)
            
            if not default_role:
                await interaction.response.send_message(
                    "❌ Rôle par défaut introuvable.",
                    ephemeral=True
                )
                return
            
            if not default_role_2:
                await interaction.response.send_message(
                    "❌ Deuxième rôle par défaut introuvable.",
                    ephemeral=True
                )
                return
            
            # Retirer tous les rôles sauf les rôles par défaut
            await seykooteam_member.edit(roles=[default_role, default_role_2])
            
            # Remettre le nom d'origine "Seykooteam"
            try:
                await seykooteam_member.edit(nick="Seykooteam")
            except Exception as e:
                print(f"⚠️ Erreur lors du renommage: {e}")
            
            # Logger l'action
            await log_seykooteam_action(
                interaction.guild,
                "déconnexion",
                details="Déconnexion du compte Seykooteam. Tous les rôles retirés sauf les rôles par défaut.",
                roles=[default_role, default_role_2],
                nickname="Seykooteam"
            )
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Déconnexion réussie",
                description="Le compte Seykooteam a été déconnecté. Tous les rôles ont été retirés sauf les rôles par défaut.",
                color=0xff0000,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📋 Statut",
                value="Déconnecté",
                inline=True
            )
            embed.set_footer(text="Seykooteam - Système de contrôle")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de la déconnexion: {e}",
                ephemeral=True
            )

class SeykooteamView(discord.ui.View):
    """Vue avec les boutons pour contrôler le compte Seykooteam"""
    
    def __init__(self):
        super().__init__(timeout=None)
        
        # Ajouter les boutons pour chaque membre
        row = 0
        for i, (member_name, member_config) in enumerate(TEAM_MEMBERS.items()):
            if i > 0 and i % 3 == 0:  # 3 boutons par rangée
                row += 1
            button = MemberButton(member_name, member_config, row)
            self.add_item(button)
        
        # Ajouter le bouton de déconnexion sur la dernière rangée
        disconnect_row = row + 1 if row < 4 else 4
        disconnect_button = DisconnectButton(disconnect_row)
        self.add_item(disconnect_button)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul le compte Seykooteam peut interagir"""
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return False
        return True

def create_seykooteam_view() -> SeykooteamView:
    """Crée la vue avec tous les boutons configurés"""
    return SeykooteamView()

async def create_seykooteam_panel(bot, guild):
    """Crée le panel de contrôle Seykooteam"""
    try:
        # Récupérer le canal
        channel = guild.get_channel(SEYKOOTEAM_CHANNEL_ID)
        if not channel:
            print("❌ Canal Seykooteam introuvable")
            return
        
        # Supprimer les anciens messages
        try:
            await channel.purge()
        except:
            pass
        
        # Créer l'embed du panel
        embed = discord.Embed(
            title="🎮 Système de Contrôle Seykooteam",
            description="Sélectionnez un membre de l'équipe pour prendre possession du compte Seykooteam.",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📋 Instructions",
            value="1. Cliquez sur le bouton du membre que vous souhaitez représenter\n2. Entrez le mot de passe correspondant\n3. Le compte Seykooteam recevra automatiquement les rôles appropriés",
            inline=False
        )
        embed.add_field(
            name="🔴 Déconnexion",
            value="Utilisez le bouton rouge pour retirer tous les rôles et revenir aux rôles par défaut (sans mot de passe).",
            inline=False
        )
        embed.add_field(
            name="🔒 Sécurité",
            value=f"Seul le compte Seykooteam (<@{SEYKOOTEAM_ACCOUNT_ID}>) peut utiliser ce système.",
            inline=False
        )
        embed.set_footer(text="Seykooteam - Système de contrôle d'équipe")
        
        # Créer la vue avec les boutons
        view = create_seykooteam_view()
        
        await channel.send(embed=embed, view=view)
        print(f"✅ Panel Seykooteam envoyé dans #{channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel Seykooteam: {e}")

async def log_seykooteam_message(message):
    """Log un message envoyé par le compte Seykooteam"""
    if message.author.id == SEYKOOTEAM_ACCOUNT_ID:
        # Logger tous les messages du compte Seykooteam
        if message.content or message.attachments:
            content = message.content if message.content else "[Fichier joint]"
            if message.attachments:
                attachments = ", ".join([att.filename for att in message.attachments])
                content = f"{content}\n📎 Fichiers: {attachments}" if content else f"📎 Fichiers: {attachments}"
            
            await log_seykooteam_action(
                message.guild,
                "message",
                details=f"Message envoyé par le compte Seykooteam",
                channel=message.channel,
                message_content=content,
                nickname=message.author.display_name
            )

def setup_seykooteam_system(bot):
    """Configure le système Seykooteam"""
    print("✅ Système Seykooteam configuré")

