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

# Rôles autorisés pour la déconnexion forcée
FORCE_DISCONNECT_ROLES = [
    1400608804919316620,
    1113214565619085424,
    1096054762862026833
]

# Configuration Admin
ADMIN_ROLE_ID = 1288085709990658088  # Rôle à donner au compte Seykooteam pour l'admin
ADMIN_PASSWORD = "admin2024"  # Mot de passe admin (à changer)

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
        "password": "josh2025",
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
        "password": "margaux2025",
        "label": "M𝔞𝔯𝔤𝔞𝔲𝔵"  # Label avec caractères spéciaux
    },
    # Les autres membres seront ajoutés plus tard
}

def is_seykooteam_account(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur est le compte Seykooteam"""
    return user.id == SEYKOOTEAM_ACCOUNT_ID

def has_force_disconnect_permission(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur a la permission de déconnexion forcée"""
    user_roles = [role.id for role in user.roles]
    return any(role_id in user_roles for role_id in FORCE_DISCONNECT_ROLES)

def is_already_connected(guild, seykooteam_member: discord.Member) -> bool:
    """Vérifie si le compte Seykooteam est déjà connecté (nom différent de 'Seykooteam')"""
    if not seykooteam_member:
        return False
    current_nick = seykooteam_member.display_name or seykooteam_member.name
    return current_nick.lower() != "seykooteam"

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

async def connect_member(interaction: discord.Interaction, member_name: str, member_config: dict):
    """Connecte un membre au compte Seykooteam"""
    # Récupérer le membre Seykooteam
    seykooteam_member = interaction.guild.get_member(SEYKOOTEAM_ACCOUNT_ID)
    if not seykooteam_member:
        await interaction.response.send_message(
            "❌ Compte Seykooteam introuvable sur le serveur.",
            ephemeral=True
        )
        return
    
    # Vérifier si quelqu'un est déjà connecté
    if is_already_connected(interaction.guild, seykooteam_member):
        current_nick = seykooteam_member.display_name or seykooteam_member.name
        await interaction.response.send_message(
            f"❌ Le compte Seykooteam est déjà connecté sous le nom **{current_nick}**.\n"
            "Veuillez vous déconnecter avant de vous reconnecter.",
            ephemeral=True
        )
        return
    
    try:
        # Récupérer les nouveaux rôles à ajouter
        new_roles = []
        for role_id in member_config["roles"]:
            role = interaction.guild.get_role(role_id)
            if role:
                new_roles.append(role)
        
        # Appliquer les rôles
        await seykooteam_member.edit(roles=new_roles)
        
        # Renommer le compte avec le nom du membre
        new_nickname = f"seykooteam-{member_name}"
        try:
            await seykooteam_member.edit(nick=new_nickname)
        except Exception as e:
            print(f"⚠️ Erreur lors du renommage: {e}")
        
        # Logger l'action
        await log_seykooteam_action(
            interaction.guild,
            "connexion",
            member_name=member_name,
            details=f"Connexion réussie pour {member_name}",
            roles=new_roles,
            nickname=new_nickname
        )
        
        # Créer l'embed de confirmation
        embed = discord.Embed(
            title="✅ Connexion réussie",
            description=f"Le compte Seykooteam a été configuré pour **{member_name}**.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="👤 Membre",
            value=member_name,
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


class MemberPasswordModal(discord.ui.Modal, title="Authentification"):
    """Modal pour saisir le mot de passe d'un membre"""
    
    def __init__(self, member_name: str, member_config: dict):
        super().__init__()
        self.member_name = member_name
        self.member_config = member_config
        # Utiliser le label personnalisé si disponible
        label = member_config.get("label", member_name.capitalize())
        self.title = f"Authentification - {label}"
        
        self.password_input = discord.ui.TextInput(
            label="Mot de passe",
            placeholder=f"Entrez votre mot de passe...",
            min_length=3,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.password_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Vérifie le mot de passe et connecte le membre"""
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Vérifier le mot de passe
        correct_password = self.member_config.get("password", "")
        if self.password_input.value != correct_password:
            await interaction.response.send_message(
                "❌ Mot de passe incorrect.",
                ephemeral=True
            )
            return
        
        # Connecter le membre
        await connect_member(interaction, self.member_name, self.member_config)

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
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Afficher le modal de mot de passe
        modal = MemberPasswordModal(self.member_name, self.member_config)
        await interaction.response.send_modal(modal)

class AdminPasswordModal(discord.ui.Modal, title="Authentification Admin"):
    """Modal pour saisir le mot de passe admin"""
    
    def __init__(self):
        super().__init__()
        self.password_input = discord.ui.TextInput(
            label="Mot de passe admin",
            placeholder="Entrez le mot de passe admin...",
            min_length=3,
            max_length=50,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.password_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Vérifie le mot de passe et applique le rôle admin"""
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Vérifier le mot de passe
        if self.password_input.value != ADMIN_PASSWORD:
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
        
        # Vérifier si quelqu'un est déjà connecté (mais permettre au mode admin de forcer la connexion)
        if is_already_connected(interaction.guild, seykooteam_member):
            current_nick = seykooteam_member.display_name or seykooteam_member.name
            # Pour l'admin, on peut forcer la connexion même si quelqu'un est connecté
            # Mais on informe quand même l'utilisateur
            pass  # On continue quand même pour l'admin
        
        try:
            # Récupérer le rôle admin
            admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
            if not admin_role:
                await interaction.response.send_message(
                    "❌ Rôle admin introuvable.",
                    ephemeral=True
                )
                return
            
            # Récupérer les rôles par défaut
            default_role = interaction.guild.get_role(DEFAULT_ROLE_ID)
            default_role_2 = interaction.guild.get_role(DEFAULT_ROLE_2_ID)
            
            # Appliquer les rôles (rôles par défaut + rôle admin)
            roles_to_apply = [admin_role]
            if default_role:
                roles_to_apply.append(default_role)
            if default_role_2:
                roles_to_apply.append(default_role_2)
            
            await seykooteam_member.edit(roles=roles_to_apply)
            
            # Renommer le compte
            new_nickname = "seykooteam-admin"
            try:
                await seykooteam_member.edit(nick=new_nickname)
            except Exception as e:
                print(f"⚠️ Erreur lors du renommage: {e}")
            
            # Logger l'action
            await log_seykooteam_action(
                interaction.guild,
                "connexion",
                member_name="Admin",
                details="Connexion admin réussie",
                roles=roles_to_apply,
                nickname=new_nickname
            )
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Connexion Admin réussie",
                description=f"Le compte Seykooteam a été configuré en mode **Admin**.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📋 Rôle appliqué",
                value=admin_role.mention,
                inline=True
            )
            embed.set_footer(text="Seykooteam - Système de contrôle")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de l'application du rôle admin: {e}",
                ephemeral=True
            )

class AdminButton(discord.ui.Button):
    """Bouton Admin pour récupérer le bot"""
    
    def __init__(self, row: int):
        super().__init__(
            label="🔧 Admin",
            style=discord.ButtonStyle.secondary,
            custom_id="seykooteam_admin",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
        if not is_seykooteam_account(interaction.user):
            await interaction.response.send_message(
                "❌ Seul le compte Seykooteam peut utiliser ce système.",
                ephemeral=True
            )
            return
        
        # Afficher le modal de mot de passe
        modal = AdminPasswordModal()
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

class ForceDisconnectButton(discord.ui.Button):
    """Bouton de déconnexion forcée"""
    
    def __init__(self, row: int):
        super().__init__(
            label="🔴 DecoForce",
            style=discord.ButtonStyle.danger,
            custom_id="seykooteam_force_disconnect",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
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
            
            # Récupérer le nom actuel avant déconnexion (pour le log)
            old_nick = seykooteam_member.display_name or seykooteam_member.name
            
            # Retirer tous les rôles sauf les rôles par défaut
            await seykooteam_member.edit(roles=[default_role, default_role_2])
            
            # Remettre le nom d'origine "Seykooteam"
            try:
                await seykooteam_member.edit(nick="Seykooteam")
            except Exception as e:
                print(f"⚠️ Erreur lors du renommage: {e}")
            
            # Logger l'action avec mention de la déconnexion forcée
            await log_seykooteam_action(
                interaction.guild,
                "déconnexion",
                details=f"Déconnexion FORCÉE du compte Seykooteam. Ancien nom: {old_nick}",
                roles=[default_role, default_role_2],
                nickname="Seykooteam"
            )
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Déconnexion forcée réussie",
                description=f"Le compte Seykooteam a été déconnecté de force.\n"
                           f"Ancien nom: **{old_nick}**\n"
                           "Tous les rôles ont été retirés sauf les rôles par défaut.",
                color=0xff0000,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📋 Statut",
                value="Déconnecté (forcé)",
                inline=True
            )
            embed.set_footer(text="Seykooteam - Système de contrôle")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors de la déconnexion forcée: {e}",
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
        
        # Ajouter le bouton Admin sur une nouvelle rangée
        admin_row = row + 1 if row < 4 else 4
        admin_button = AdminButton(admin_row)
        self.add_item(admin_button)
        
        # Ajouter le bouton de déconnexion sur la dernière rangée
        disconnect_row = admin_row + 1 if admin_row < 4 else 4
        disconnect_button = DisconnectButton(disconnect_row)
        self.add_item(disconnect_button)
        
        # Ajouter le bouton de déconnexion forcée sur la même rangée
        force_disconnect_button = ForceDisconnectButton(disconnect_row)
        self.add_item(force_disconnect_button)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul le compte Seykooteam peut utiliser les boutons"""
        # Vérifier que seul le compte Seykooteam peut utiliser ce système
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
            value="1. Cliquez sur le bouton de votre nom\n2. Entrez votre mot de passe dans le modal qui apparaît\n3. Le compte Seykooteam recevra automatiquement vos rôles",
            inline=False
        )
        embed.add_field(
            name="🔧 Admin",
            value="Bouton pour récupérer le bot en mode admin. Nécessite le mot de passe admin.",
            inline=False
        )
        embed.add_field(
            name="🔴 Déconnexion",
            value="**Déconnecter** : Utilisez le bouton rouge pour retirer tous les rôles et revenir aux rôles par défaut.\n"
                  "**DecoForce** : Bouton de déconnexion forcée (en cas d'oubli de déconnexion).",
            inline=False
        )
        embed.add_field(
            name="🔒 Sécurité",
            value=f"**Important** : Seul le compte Seykooteam (<@{SEYKOOTEAM_ACCOUNT_ID}>) peut utiliser ce système. Chaque membre a son propre mot de passe.",
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

