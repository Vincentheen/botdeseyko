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
        "no_ticket_channel": "❌ Cette commande ne peut être utilisée que dans un canal de ticket.",
        "user_not_found": "❌ Utilisateur non trouvé. Veuillez mentionner un utilisateur valide ou fournir un ID valide.",
        "user_already_in_ticket": "❌ Cet utilisateur a déjà accès au ticket.",
        "user_added": "✅ {user} a été ajouté au ticket.",
        "add_user_no_permission": "❌ Vous n'avez pas la permission d'ajouter des utilisateurs à ce ticket.",
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
        "partenariat_desc": "Pour proposer un partenariat ou collaboration",
        "stage_desc": "Pour les demandes de stage",
        "info": "📋 Informations",
        "info_desc": "Un membre de l'équipe vous répondra dans les plus brefs délais.",
        "trailer_maker_view_only": "👁️ Vue Seule",
        "trailer_maker_view_only_desc": "Vous pouvez voir ce ticket mais pas le modifier."
    },
    "en": {
        "no_permission": "❌ You don't have permission to close this ticket.",
        "no_ticket_channel": "❌ This command can only be used in a ticket channel.",
        "user_not_found": "❌ User not found. Please mention a valid user or provide a valid ID.",
        "user_already_in_ticket": "❌ This user already has access to the ticket.",
        "user_added": "✅ {user} has been added to the ticket.",
        "add_user_no_permission": "❌ You don't have permission to add users to this ticket.",
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
        "partenariat_desc": "To propose a partnership or collaboration",
        "stage_desc": "For internship requests",
        "info": "📋 Information",
        "info_desc": "A team member will respond to you as soon as possible.",
        "trailer_maker_view_only": "👁️ View Only",
        "trailer_maker_view_only_desc": "You can view this ticket but cannot modify it."
    }
}

def get_language(user: discord.Member) -> str:
    """Détecte la langue de l'utilisateur de manière avancée"""
    
    # 1. Vérifier si l'utilisateur a un rôle "English" ou "Français"
    english_roles = ["English", "EN", "🇬🇧", "🇺🇸", "English Speaker"]
    french_roles = ["Français", "FR", "🇫🇷", "French Speaker"]
    
    user_role_names = [role.name for role in user.roles]
    
    for role_name in user_role_names:
        if any(english in role_name for english in english_roles):
            return "en"
        if any(french in role_name for french in french_roles):
            return "fr"
    
    # 2. Vérifier la localisation Discord (si disponible)
    if hasattr(user, 'locale') and user.locale:
        if user.locale.startswith('en'):
            return "en"
        elif user.locale.startswith('fr'):
            return "fr"
    
    # 3. Vérifier le nom d'utilisateur pour des indices
    username_lower = user.name.lower()
    if any(word in username_lower for word in ['english', 'en', 'uk', 'us', 'american', 'british']):
        return "en"
    elif any(word in username_lower for word in ['french', 'fr', 'français', 'francais']):
        return "fr"
    
    # 4. Par défaut, retourner français
    return "fr"

def get_message(key: str, lang: str = "fr", **kwargs) -> str:
    """Récupère un message dans la langue spécifiée"""
    message = MESSAGES[lang].get(key, key)
    return message.format(**kwargs) if kwargs else message

# Configuration des catégories de tickets
TICKET_CATEGORIES = {
    "commande": 1399437778189553744,
    "service_client": 1399438065591910516,
    "nous_rejoindre": 1399438265047715981,
    "voix_off": 1406036530471895060,  # Catégorie pour les tickets voix off
    "partenariat": 1421807618078539886,  # Catégorie pour les tickets partenariat
    "stage": 1440068368332755085  # Catégorie pour les tickets stage
}

# Configuration des canaux
TICKET_PANEL_CHANNEL_ID = 1399430693217505300  # Canal pour le panel de tickets (avec les boutons)
TICKET_LOG_CHANNEL_ID = 1400115679775948963    # Canal pour les logs de tickets

# Rôles autorisés pour la gestion des tickets
TICKET_MANAGER_ROLES = [
    1335705793697288213,  # 『👤』Responsable Support
    1335706767908405432,  # 『👤』Relation Clients
    1335707516352331949,  # 『👤』Responsable Commercial
    1113214565619085424,  # 𝐀𝐝𝐦𝐢𝐧 technique
    1399517642884124702,  # 『👤』Moderateur technique
    1096054762862026833,  # Directeur Général
    1400608804919316620,  # Assistant Director
    1420379353610457098,  # Rôle partenariat 1
    1335707332180447443   # Rôle partenariat 2
]

# Rôle des trailer makers (peut voir les tickets commande mais pas les modifier)
TRAILER_MAKER_ROLE_ID = 1400552543532355655

# Rôles autorisés pour les tickets stage (accès restreint)
STAGE_TICKET_ROLES = [
    1096054762862026833,  # Directeur Général
    1005763703397941345,  # Rôle stage 1
    1420379353610457098   # Rôle partenariat 1
]

def has_ticket_permission(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur a les permissions de gestion des tickets"""
    user_roles = [role.id for role in user.roles]
    return any(role_id in user_roles for role_id in TICKET_MANAGER_ROLES)

def is_trailer_maker(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur est un trailer maker"""
    return TRAILER_MAKER_ROLE_ID in [role.id for role in user.roles]

class LanguageSelectView(discord.ui.View):
    """Vue avec les boutons pour changer la langue du message de bienvenue"""
    
    def __init__(self, message_id: int, ticket_type: str):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.ticket_type = ticket_type
    
    @discord.ui.button(emoji="🇬🇧", style=discord.ButtonStyle.secondary, custom_id=f"lang_switch_en", row=0)
    async def set_english(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_language_change(interaction, "en")
    
    @discord.ui.button(emoji="🇪🇸", style=discord.ButtonStyle.secondary, custom_id=f"lang_switch_es", row=0)
    async def set_spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_language_change(interaction, "es")
    
    async def handle_language_change(self, interaction: discord.Interaction, new_lang: str):
        """Gère le changement de langue"""
        try:
            # Récupérer le message original depuis l'interaction (le message qui contient le bouton)
            message = interaction.message
            
            # Créer le nouvel embed avec la nouvelle langue selon le type de ticket
            if self.ticket_type == "commande":
                embed = create_commande_welcome_embed(new_lang)
            elif self.ticket_type == "stage":
                embed = create_stage_welcome_embed(new_lang)
            elif self.ticket_type == "partenariat":
                embed = create_partenariat_welcome_embed(new_lang)
            else:
                await interaction.response.send_message(
                    "❌ Type de ticket non supporté pour la traduction.",
                    ephemeral=True
                )
                return
            
            # Recréer la vue (pour maintenir les boutons)
            view = LanguageSelectView(message.id, self.ticket_type)
            
            # Mettre à jour le message
            await message.edit(embed=embed, view=view)
            
            # Confirmation éphémère
            lang_names = {"en": "English", "es": "Español", "fr": "Français"}
            await interaction.response.send_message(
                f"✅ Langue changée en {lang_names.get(new_lang, new_lang)}",
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "❌ Message introuvable. Le ticket a peut-être été supprimé.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur lors du changement de langue: {e}",
                ephemeral=True
            )

def create_commande_welcome_embed(language: str = "fr") -> discord.Embed:
    """
    Crée l'embed de bienvenue pour les tickets commande dans la langue spécifiée
    
    Args:
        language: La langue (fr, en, es)
    
    Returns:
        L'embed Discord
    """
    messages = {
        "fr": {
            "content": "**Bonjour, et merci d'avoir ouvert un ticket chez SeykooFX 🎬✨**\n\nPour commencer, merci de nous indiquer **le type de projet** que vous souhaitez (trailer, écran de chargement, FX, sound design, voix-off…) ainsi que **la durée** envisagée.",
            "cahier_des_charges_title": "📄 **Cahier des charges (recommandé)**",
            "cahier_des_charges_content": "Si vous avez déjà une idée précise, vous pouvez préparer un **cahier des charges** (Google Docs conseillé) contenant :\n\n• Les **scènes clés** ou éléments importants\n• Le **style visuel / sonore** souhaité\n• Vos **références ou inspirations**\n• L'**ambiance générale** recherchée\n• Une **éventuelle échéance**\n\nCela nous permettra de vous fournir un **devis clair et adapté**.",
            "infos_title": "🔗 **Informations utiles**",
            "infos_content": "💰 **Tarifs** : https://www.seykoofx.com/shop.htm\n🎨 **Dernières créations** : https://www.seykoofx.com/creation.html\n📞 **Prendre un premier rendez-vous vocal** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "Nous sommes impatients de découvrir votre projet et de vous accompagner dans sa réalisation 🚀",
            "signature": "**— SeykooFX | Relations Client**"
        },
        "en": {
            "content": "**Hello, and thank you for opening a ticket at SeykooFX 🎬✨**\n\nTo get started, please let us know **the type of project** you want (trailer, loading screen, FX, sound design, voice-over…) as well as **the desired duration**.",
            "cahier_des_charges_title": "📄 **Specifications (Recommended)**",
            "cahier_des_charges_content": "If you already have a clear idea, you can prepare **specifications** (Google Docs recommended) containing:\n\n• **Key scenes** or important elements\n• The desired **visual / sound style**\n• Your **references or inspirations**\n• The overall **atmosphere** you're looking for\n• A **possible deadline**\n\nThis will allow us to provide you with a **clear and tailored quote**.",
            "infos_title": "🔗 **Useful Information**",
            "infos_content": "💰 **Pricing** : https://www.seykoofx.com/shop.htm\n🎨 **Latest creations** : https://www.seykoofx.com/creation.html\n📞 **Schedule a first voice appointment** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "We look forward to discovering your project and supporting you in its realization 🚀",
            "signature": "**— SeykooFX | Customer Relations**"
        },
        "es": {
            "content": "**Hola, y gracias por abrir un ticket en SeykooFX 🎬✨**\n\nPara comenzar, por favor indícanos **el tipo de proyecto** que deseas (tráiler, pantalla de carga, FX, diseño de sonido, voz en off…) así como **la duración** prevista.",
            "cahier_des_charges_title": "📄 **Pliego de condiciones (Recomendado)**",
            "cahier_des_charges_content": "Si ya tienes una idea precisa, puedes preparar un **pliego de condiciones** (Google Docs recomendado) que contenga:\n\n• Las **escenas clave** o elementos importantes\n• El **estilo visual / sonoro** deseado\n• Tus **referencias o inspiraciones**\n• El **ambiente general** que buscas\n• Una **posible fecha límite**\n\nEsto nos permitirá ofrecerte un **presupuesto claro y adaptado**.",
            "infos_title": "🔗 **Información útil**",
            "infos_content": "💰 **Tarifas** : https://www.seykoofx.com/shop.htm\n🎨 **Últimas creaciones** : https://www.seykoofx.com/creation.html\n📞 **Solicitar una primera cita vocal** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "Esperamos descubrir tu proyecto y acompañarte en su realización 🚀",
            "signature": "**— SeykooFX | Relaciones Cliente**"
        }
    }
    
    msg = messages.get(language, messages["fr"])
    
    # Créer l'embed de bienvenue
    embed = discord.Embed(
        description=msg["content"],
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=msg["cahier_des_charges_title"],
        value=msg["cahier_des_charges_content"],
        inline=False
    )
    
    embed.add_field(
        name=msg["infos_title"],
        value=msg["infos_content"],
        inline=False
    )
    
    embed.add_field(
        name="\u200b",  # Ligne vide
        value=f"{msg['footer']}\n\n{msg['signature']}",
        inline=False
    )
    
    embed.set_footer(text="SeykooFX - Relations Client")
    
    return embed

def create_stage_welcome_embed(language: str = "fr") -> discord.Embed:
    """
    Crée l'embed de bienvenue pour les tickets stage dans la langue spécifiée
    
    Args:
        language: La langue (fr, en, es)
    
    Returns:
        L'embed Discord
    """
    messages = {
        "fr": {
            "content": "**Bonjour, et merci d'avoir ouvert un ticket dédié aux demandes de stage chez SeykooFX 🎓**\n\nAfin de mieux traiter votre candidature ou votre demande d'information, merci de nous préciser :",
            "infos_title": "📋 Informations à fournir",
            "infos_content": "• **Le type de stage recherché** (montage, FX, sound design, trailer, communication, etc.)\n• **La durée du stage** souhaitée\n• **Votre établissement scolaire**\n• **Vos compétences ou logiciels maîtrisés**\n• **Vos motivations** et ce que vous souhaitez apprendre",
            "documents_title": "📄 **Documents recommandés**",
            "documents_content": "Pour étudier votre profil efficacement, nous vous invitons à joindre :\n\n• Votre **CV**\n• Votre **portfolio**, showreel ou travaux personnels\n• Une **lettre de motivation** (ou quelques lignes expliquant votre démarche)",
            "footer": "Nous reviendrons vers vous après analyse de votre profil.\n\n**Merci pour votre intérêt et bonne chance dans votre candidature !** 🙌",
            "signature": "**— SeykooFX | Service Recrutement & Relations Stagiaires**"
        },
        "en": {
            "content": "**Hello, and thank you for opening an internship request ticket at SeykooFX 🎓**\n\nTo better process your application or information request, please let us know:",
            "infos_title": "📋 Information to Provide",
            "infos_content": "• **The type of internship** you are looking for (editing, FX, sound design, trailer, communication, etc.)\n• **The desired duration** of the internship\n• **Your educational institution**\n• **Your skills or software you master**\n• **Your motivations** and what you want to learn",
            "documents_title": "📄 **Recommended Documents**",
            "documents_content": "To effectively study your profile, we invite you to attach:\n\n• Your **CV**\n• Your **portfolio**, showreel or personal work\n• A **cover letter** (or a few lines explaining your approach)",
            "footer": "We will get back to you after analyzing your profile.\n\n**Thank you for your interest and good luck with your application!** 🙌",
            "signature": "**— SeykooFX | Recruitment & Intern Relations Service**"
        },
        "es": {
            "content": "**Hola, y gracias por abrir un ticket dedicado a solicitudes de prácticas en SeykooFX 🎓**\n\nPara procesar mejor tu candidatura o solicitud de información, por favor indícanos:",
            "infos_title": "📋 Información a Proporcionar",
            "infos_content": "• **El tipo de prácticas** que buscas (montaje, FX, diseño de sonido, tráiler, comunicación, etc.)\n• **La duración deseada** de las prácticas\n• **Tu institución educativa**\n• **Tus competencias o software que dominas**\n• **Tus motivaciones** y lo que deseas aprender",
            "documents_title": "📄 **Documentos Recomendados**",
            "documents_content": "Para estudiar tu perfil eficazmente, te invitamos a adjuntar:\n\n• Tu **CV**\n• Tu **portfolio**, showreel o trabajos personales\n• Una **carta de motivación** (o unas líneas explicando tu enfoque)",
            "footer": "Te contactaremos después de analizar tu perfil.\n\n**¡Gracias por tu interés y buena suerte con tu candidatura!** 🙌",
            "signature": "**— SeykooFX | Servicio de Reclutamiento y Relaciones con Practicantes**"
        }
    }
    
    msg = messages.get(language, messages["fr"])
    
    embed = discord.Embed(
        description=msg["content"],
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=msg["infos_title"],
        value=msg["infos_content"],
        inline=False
    )
    
    embed.add_field(
        name=msg["documents_title"],
        value=msg["documents_content"],
        inline=False
    )
    
    embed.add_field(
        name="\u200b",
        value=f"{msg['footer']}\n\n{msg['signature']}",
        inline=False
    )
    
    embed.set_footer(text="SeykooFX - Service Recrutement & Relations Stagiaires")
    
    return embed

async def send_stage_welcome_message(channel: discord.TextChannel, language: str = "fr"):
    """
    Envoie le message de bienvenue automatique pour les tickets de type "Stage"
    avec des boutons pour changer la langue
    
    Args:
        channel: Le canal du ticket
        language: La langue initiale (fr, en, es)
    """
    # Créer l'embed dans la langue initiale
    embed = create_stage_welcome_embed(language)
    
    try:
        message = await channel.send(embed=embed)
        
        # Créer la vue avec l'ID du message et le type de ticket
        view = LanguageSelectView(message.id, "stage")
        await message.edit(embed=embed, view=view)
        
        print(f"✅ Message de bienvenue stage envoyé dans {channel.name} (langue: {language})")
    except Exception as e:
        print(f"❌ Erreur envoi message bienvenue stage: {e}")

def create_partenariat_welcome_embed(language: str = "fr") -> discord.Embed:
    """
    Crée l'embed de bienvenue pour les tickets partenariat dans la langue spécifiée
    
    Args:
        language: La langue (fr, en, es)
    
    Returns:
        L'embed Discord
    """
    messages = {
        "fr": {
            "content": "**Bonjour, et merci d'avoir ouvert un ticket Partenariat chez SeykooFX 🤝**\n\nAfin d'étudier votre proposition de manière efficace, merci de nous préciser :",
            "infos_title": "📋 Informations à fournir",
            "infos_content": "• **Le type de partenariat souhaité** (collaboration, échange de services, partenariat commercial…)\n• **Votre structure / projet / entreprise**\n• **Ce que vous recherchez** dans la collaboration\n• **Ce que vous proposez en retour**\n• Tout lien utile : site, réseaux, portfolio, présentation, etc.",
            "charte_title": "📘 **Avant de continuer : merci de consulter notre Charte de Partenariat**",
            "charte_content": "Cela vous permettra de vérifier si votre demande correspond à nos critères ⬇️\n\n👉 https://discord.com/channels/1005763703335034970/1435267882572447765",
            "infos_utiles_title": "🔗 Informations utiles",
            "infos_utiles_content": "Pour découvrir notre univers et nos réalisations :\n\n🎨 **Nos créations** : https://www.seykoofx.com/creation.html\n\nPour planifier un échange vocal si nécessaire :\n\n📞 **Prendre rendez-vous** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "Nous analyserons votre proposition avec attention et reviendrons vers vous dans les plus brefs délais.\n\n**Merci pour votre intérêt envers SeykooFX !** ✨",
            "signature": "**— SeykooFX | Relations Partenaires**"
        },
        "en": {
            "content": "**Hello, and thank you for opening a Partnership ticket at SeykooFX 🤝**\n\nTo effectively study your proposal, please let us know:",
            "infos_title": "📋 Information to Provide",
            "infos_content": "• **The type of partnership** you want (collaboration, service exchange, commercial partnership…)\n• **Your structure / project / company**\n• **What you are looking for** in the collaboration\n• **What you offer in return**\n• Any useful links: website, social media, portfolio, presentation, etc.",
            "charte_title": "📘 **Before Continuing: Please Review Our Partnership Charter**",
            "charte_content": "This will allow you to verify if your request matches our criteria ⬇️\n\n👉 https://discord.com/channels/1005763703335034970/1435267882572447765",
            "infos_utiles_title": "🔗 Useful Information",
            "infos_utiles_content": "To discover our universe and our creations:\n\n🎨 **Our creations** : https://www.seykoofx.com/creation.html\n\nTo schedule a voice exchange if necessary:\n\n📞 **Schedule an appointment** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "We will analyze your proposal carefully and get back to you as soon as possible.\n\n**Thank you for your interest in SeykooFX!** ✨",
            "signature": "**— SeykooFX | Partner Relations**"
        },
        "es": {
            "content": "**Hola, y gracias por abrir un ticket de Asociación en SeykooFX 🤝**\n\nPara estudiar tu propuesta de manera eficaz, por favor indícanos:",
            "infos_title": "📋 Información a Proporcionar",
            "infos_content": "• **El tipo de asociación** que deseas (colaboración, intercambio de servicios, asociación comercial…)\n• **Tu estructura / proyecto / empresa**\n• **Lo que buscas** en la colaboración\n• **Lo que ofreces a cambio**\n• Cualquier enlace útil: sitio web, redes sociales, portfolio, presentación, etc.",
            "charte_title": "📘 **Antes de Continuar: Por Favor Consulta Nuestra Carta de Asociación**",
            "charte_content": "Esto te permitirá verificar si tu solicitud coincide con nuestros criterios ⬇️\n\n👉 https://discord.com/channels/1005763703335034970/1435267882572447765",
            "infos_utiles_title": "🔗 Información Útil",
            "infos_utiles_content": "Para descubrir nuestro universo y nuestras creaciones:\n\n🎨 **Nuestras creaciones** : https://www.seykoofx.com/creation.html\n\nPara planificar un intercambio vocal si es necesario:\n\n📞 **Solicitar una cita** : https://www.seykoofx.com/planning-realtime.html",
            "footer": "Analizaremos tu propuesta con atención y te contactaremos lo antes posible.\n\n**¡Gracias por tu interés en SeykooFX!** ✨",
            "signature": "**— SeykooFX | Relaciones con Socios**"
        }
    }
    
    msg = messages.get(language, messages["fr"])
    
    embed = discord.Embed(
        description=msg["content"],
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name=msg["infos_title"],
        value=msg["infos_content"],
        inline=False
    )
    
    embed.add_field(
        name=msg["charte_title"],
        value=msg["charte_content"],
        inline=False
    )
    
    embed.add_field(
        name=msg["infos_utiles_title"],
        value=msg["infos_utiles_content"],
        inline=False
    )
    
    embed.add_field(
        name="\u200b",
        value=f"{msg['footer']}\n\n{msg['signature']}",
        inline=False
    )
    
    embed.set_footer(text="SeykooFX - Relations Partenaires")
    
    return embed

async def send_partenariat_welcome_message(channel: discord.TextChannel, language: str = "fr"):
    """
    Envoie le message de bienvenue automatique pour les tickets de type "Partenariat"
    avec des boutons pour changer la langue
    
    Args:
        channel: Le canal du ticket
        language: La langue initiale (fr, en, es)
    """
    # Créer l'embed dans la langue initiale
    embed = create_partenariat_welcome_embed(language)
    
    try:
        message = await channel.send(embed=embed)
        
        # Créer la vue avec l'ID du message et le type de ticket
        view = LanguageSelectView(message.id, "partenariat")
        await message.edit(embed=embed, view=view)
        
        print(f"✅ Message de bienvenue partenariat envoyé dans {channel.name} (langue: {language})")
    except Exception as e:
        print(f"❌ Erreur envoi message bienvenue partenariat: {e}")

async def send_commande_welcome_message(channel: discord.TextChannel, language: str = "fr"):
    """
    Envoie le message de bienvenue automatique pour les tickets de type "Commande"
    avec des boutons pour changer la langue
    
    Args:
        channel: Le canal du ticket
        language: La langue initiale (fr, en, es)
    """
    # Créer l'embed dans la langue initiale
    embed = create_commande_welcome_embed(language)
    
    # Créer la vue avec les boutons de langue
    # On va créer la vue après avoir envoyé le message pour avoir l'ID
    try:
        message = await channel.send(embed=embed)
        
        # Créer la vue avec l'ID du message et le type de ticket
        view = LanguageSelectView(message.id, "commande")
        await message.edit(embed=embed, view=view)
        
        print(f"✅ Message de bienvenue envoyé dans {channel.name} (langue: {language})")
    except Exception as e:
        print(f"❌ Erreur envoi message bienvenue: {e}")

def can_manage_ticket(user: discord.Member, ticket_channel) -> bool:
    """Vérifie si l'utilisateur peut gérer un ticket spécifique"""
    # Vérifier si c'est un ticket stage (permissions spéciales)
    if ticket_channel.category and ticket_channel.category.id == TICKET_CATEGORIES.get("stage"):
        user_roles = [role.id for role in user.roles]
        return any(role_id in user_roles for role_id in STAGE_TICKET_ROLES)
    
    # Seuls les managers ont accès pour les autres tickets
    if has_ticket_permission(user):
        return True
    
    # Les trailer makers ne peuvent pas gérer les tickets (même s'ils peuvent les voir)
    if is_trailer_maker(user):
        return False
    
    # Tous les autres utilisateurs (y compris le créateur) n'ont pas accès
    return False

class TicketSelect(discord.ui.Select):
    """Menu déroulant pour sélectionner le type de ticket"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="🛒 Commande",
                description="Devis & commandes • Tarifs & services • Questions commerciales",
                value="commande",
                emoji="🛒"
            ),
            discord.SelectOption(
                label="🎧 Service Client",
                description="Support technique • Questions générales • Aide & dépannage",
                value="service_client",
                emoji="🎧"
            ),
            discord.SelectOption(
                label="👥 Nous Rejoindre",
                description="Recrutement • Candidatures • Partenariats",
                value="nous_rejoindre",
                emoji="👥"
            ),
            discord.SelectOption(
                label="🎙️ Voix Off",
                description="Voix off pro • Doublage • Narration",
                value="voix_off",
                emoji="🎙️"
            ),
            discord.SelectOption(
                label="🤝 Partenariat",
                description="Propositions de collaboration • Partenariats commerciaux • Échanges de services",
                value="partenariat",
                emoji="🤝"
            ),
            discord.SelectOption(
                label="🎓 Stage",
                description="Demandes de stage • Candidatures stage • Informations stage",
                value="stage",
                emoji="🎓"
            )
        ]
        
        super().__init__(
            placeholder="Sélectionnez une catégorie pour créer un ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_menu"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Appelé quand une option est sélectionnée"""
        ticket_type = self.values[0]
        await create_ticket(interaction, ticket_type)

class TicketView(discord.ui.View):
    """Vue avec un menu déroulant pour créer des tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
        # Ajouter le menu déroulant
        self.add_item(TicketSelect())

class TicketControlView(discord.ui.View):
    """Vue pour contrôler les tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_language(interaction.user)
        
        if not can_manage_ticket(interaction.user, interaction.channel):
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
        
        # Permissions spéciales pour les tickets stage (seulement les rôles autorisés)
        if ticket_type == "stage":
            for role_id in STAGE_TICKET_ROLES:
                role = interaction.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True,
                        manage_channels=True,
                        attach_files=True,
                        embed_links=True,
                        add_reactions=True,
                        use_external_emojis=True,
                        mention_everyone=True
                    )
        else:
            # Ajouter les permissions pour les rôles de gestion (pour les autres types de tickets)
            for role_id in TICKET_MANAGER_ROLES:
                role = interaction.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True,
                        manage_channels=True,
                        attach_files=True,
                        embed_links=True,
                        add_reactions=True,
                        use_external_emojis=True,
                        mention_everyone=True
                    )
        
        # Permissions spéciales pour les trailer makers dans les tickets commande
        if ticket_type == "commande":
            trailer_maker_role = interaction.guild.get_role(TRAILER_MAKER_ROLE_ID)
            if trailer_maker_role:
                # Les trailer makers peuvent voir mais pas modifier les tickets commande
                overwrites[trailer_maker_role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=False,
                    add_reactions=False,
                    attach_files=False,
                    embed_links=False,
                    use_external_emojis=False,
                    use_external_stickers=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    send_messages_in_threads=False,
                    manage_messages=False,
                    manage_threads=False
                )
        
        ticket_channel = await interaction.guild.create_text_channel(
            f"ticket-{interaction.user.name.lower()}",
            category=category,
            overwrites=overwrites
        )
        
        # Créer l'embed de bienvenue avec le nouveau format
        ticket_type_emoji = {
            "commande": "🛒",
            "service_client": "🎧", 
            "nous_rejoindre": "👥",
            "voix_off": "🎙️",
            "partenariat": "🤝",
            "stage": "🎓"
        }
        
        ticket_type_name = {
            "commande": "Commande",
            "service_client": "Service Client",
            "nous_rejoindre": "Nous Rejoindre",
            "voix_off": "Voix Off",
            "partenariat": "Partenariat",
            "stage": "Stage"
        }
        
        embed = discord.Embed(
            title=f"🎫 Ticket {ticket_type_emoji.get(ticket_type, '📋')} {ticket_type_name.get(ticket_type, ticket_type.replace('_', ' ').title())}",
            description=f"Bienvenue {interaction.user.mention} ! Votre ticket a été créé avec succès.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📋 Instructions",
            value="Décrivez votre demande en détail. Un membre de l'équipe vous répondra dès que possible.",
            inline=False
        )
        embed.add_field(
            name="🔧 Contrôles",
            value="Utilisez les boutons ci-dessous pour gérer votre ticket.",
            inline=False
        )
        embed.set_footer(text="Seykoofx - Support Pro")
        
        # Créer la vue de contrôle
        control_view = TicketControlView()
        
        await ticket_channel.send(embed=embed, view=control_view)
        
        # Envoyer le message automatique selon le type de ticket
        # Toujours en français par défaut (les boutons de traduction permettent de changer)
        if ticket_type == "commande":
            await send_commande_welcome_message(ticket_channel, "fr")
        elif ticket_type == "stage":
            await send_stage_welcome_message(ticket_channel, "fr")
        elif ticket_type == "partenariat":
            await send_partenariat_welcome_message(ticket_channel, "fr")
        
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
        # Récupérer le canal pour le panel de tickets
        ticket_channel = guild.get_channel(TICKET_PANEL_CHANNEL_ID)
        if not ticket_channel:
            print("❌ Canal du panel de tickets introuvable")
            return
        
        # Supprimer les anciens messages
        try:
            await ticket_channel.purge()
        except:
            pass
        
        # Créer l'embed du panel (version française par défaut)
        embed = discord.Embed(
            title="✨ Centre d'Assistance Seykoofx",
            description="Sélectionnez une catégorie pour créer un ticket :\n\n",
            color=0x2b2d31,
            timestamp=datetime.now()
        )
        
        # Services principaux
        embed.add_field(
            name="🛒 Commande",
            value="• Devis & commandes\n• Tarifs & services\n• Questions commerciales\n\u200b",
            inline=False
        )
        embed.add_field(
            name="🎧 Service Client",
            value="• Support technique\n• Questions générales\n• Aide & dépannage\n\u200b",
            inline=False
        )
        embed.add_field(
            name="👥 Nous Rejoindre",
            value="• Recrutement\n• Candidatures\n• Partenariats\n\u200b",
            inline=False
        )
        embed.add_field(
            name="🎙️ Voix Off",
            value="• Voix off pro\n• Doublage\n• Narration\n\u200b",
            inline=False
        )
        embed.add_field(
            name="🤝 Partenariat",
            value="• Propositions de collaboration\n• Partenariats commerciaux\n• Échanges de services\n\u200b",
            inline=False
        )
        embed.add_field(
            name="🎓 Stage",
            value="• Demandes de stage\n• Candidatures stage\n• Informations stage",
            inline=False
        )
        
        embed.set_footer(text="Seykoofx • Excellence & Innovation", icon_url="https://cdn.discordapp.com/emojis/1001399870095155240.webp")
        
        # Créer la vue avec les boutons
        view = TicketView()
        
        await ticket_channel.send(embed=embed, view=view)
        print(f"✅ Panel de tickets envoyé dans #{ticket_channel.name}")
        
    except Exception as e:
        print(f"❌ Erreur création panel tickets: {e}")

async def update_existing_commande_tickets(guild):
    """Met à jour les permissions des tickets commande existants pour les trailer makers"""
    try:
        commande_category_id = TICKET_CATEGORIES.get("commande")
        if not commande_category_id:
            print("❌ Catégorie commande introuvable")
            return
        
        category = guild.get_channel(commande_category_id)
        if not category:
            print("❌ Catégorie commande introuvable")
            return
        
        trailer_maker_role = guild.get_role(TRAILER_MAKER_ROLE_ID)
        if not trailer_maker_role:
            print("❌ Rôle trailer maker introuvable")
            return
        
        updated_count = 0
        for channel in category.channels:
            if channel.name.startswith("ticket-"):
                # Vérifier si les permissions des trailer makers sont déjà configurées
                current_overwrites = channel.overwrites_for(trailer_maker_role)
                if not current_overwrites.read_messages:
                    # Ajouter les permissions de lecture seule pour les trailer makers
                    await channel.set_permissions(trailer_maker_role, 
                        read_messages=True,
                        send_messages=False,
                        add_reactions=False,
                        attach_files=False,
                        embed_links=False,
                        use_external_emojis=False,
                        use_external_stickers=False,
                        create_public_threads=False,
                        create_private_threads=False,
                        send_messages_in_threads=False,
                        manage_messages=False,
                        manage_threads=False
                    )
                    updated_count += 1
                    print(f"✅ Permissions mises à jour pour {channel.name}")
        
        if updated_count > 0:
            print(f"✅ {updated_count} tickets commande mis à jour pour les trailer makers")
        else:
            print("ℹ️ Aucun ticket commande nécessitait de mise à jour")
            
    except Exception as e:
        print(f"❌ Erreur mise à jour tickets existants: {e}")

class TicketCommands(commands.Cog):
    """Commandes pour gérer les tickets"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="adduser")
    async def add_user(self, ctx, user: discord.Member):
        """Ajoute un utilisateur au ticket actuel"""
        lang = get_language(ctx.author)
        
        # Vérifier si c'est un canal de ticket
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send(get_message("no_ticket_channel", lang))
            return
        
        # Vérifier les permissions
        if not can_manage_ticket(ctx.author, ctx.channel):
            await ctx.send(get_message("add_user_no_permission", lang))
            return
        
        # Vérifier si l'utilisateur a déjà accès
        if ctx.channel.permissions_for(user).read_messages:
            await ctx.send(get_message("user_already_in_ticket", lang))
            return
        
        # Ajouter l'utilisateur
        try:
            await ctx.channel.set_permissions(user,
                read_messages=True,
                send_messages=True
            )
            await ctx.send(get_message("user_added", lang, user=user.mention))
            
            # Log l'action
            try:
                from logs import log_ticket_action
                await log_ticket_action(
                    ctx.guild,
                    "ajout_utilisateur",
                    ctx.author,
                    f"ticket-{ctx.channel.id}",
                    channel=ctx.channel,
                    target_user=user
                )
            except Exception as e:
                print(f"❌ Erreur log ticket: {e}")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

    @commands.command(name="close")
    async def close_ticket(self, ctx):
        """Ferme le ticket actuel"""
        lang = get_language(ctx.author)
        
        # Vérifier si c'est un canal de ticket
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send(get_message("no_ticket_channel", lang))
            return
        
        # Vérifier les permissions
        if not can_manage_ticket(ctx.author, ctx.channel):
            await ctx.send(get_message("no_permission", lang))
            return
        
        await ctx.send(get_message("closing_ticket", lang))
        
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
        
        await ctx.channel.send(embed=embed)
        
        # Log la fermeture
        try:
            from logs import log_ticket_action
            await log_ticket_action(
                ctx.guild,
                "fermé",
                ctx.author,
                f"ticket-{ctx.channel.id}",
                channel=ctx.channel
            )
        except Exception as e:
            print(f"❌ Erreur log ticket: {e}")
        
        # Attendre 10 secondes puis supprimer le canal
        await asyncio.sleep(10)
        try:
            await ctx.channel.delete()
        except Exception as e:
            print(f"❌ Erreur suppression canal: {e}")
    
    @commands.command(name="ticketcount")
    @commands.has_permissions(manage_channels=True)
    async def ticket_count(self, ctx):
        """Compte le nombre de tickets ouverts dans chaque catégorie"""
        lang = get_language(ctx.author)
        
        # Noms des catégories pour l'affichage
        category_names = {
            "commande": "🛒 Commande",
            "service_client": "🎧 Service Client",
            "nous_rejoindre": "👥 Nous Rejoindre",
            "voix_off": "🎙️ Voix Off",
            "partenariat": "🤝 Partenariat",
            "stage": "🎓 Stage"
        }
        
        # Créer l'embed de statistiques
        embed = discord.Embed(
            title="📊 Statistiques des Tickets",
            description="Nombre de tickets ouverts par catégorie",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        total_tickets = 0
        
        # Compter les tickets pour chaque catégorie
        for ticket_type, category_id in TICKET_CATEGORIES.items():
            category = ctx.guild.get_channel(category_id)
            if category:
                # Compter les canaux qui commencent par "ticket-"
                ticket_count = sum(1 for channel in category.channels if channel.name.startswith("ticket-"))
                total_tickets += ticket_count
                
                category_name = category_names.get(ticket_type, ticket_type.replace("_", " ").title())
                embed.add_field(
                    name=category_name,
                    value=f"**{ticket_count}** ticket(s) ouvert(s)",
                    inline=True
                )
            else:
                category_name = category_names.get(ticket_type, ticket_type.replace("_", " ").title())
                embed.add_field(
                    name=category_name,
                    value="❌ Catégorie introuvable",
                    inline=True
                )
        
        # Ajouter le total
        embed.add_field(
            name="\u200b",
            value=f"**📈 Total : {total_tickets} ticket(s) ouvert(s)**",
            inline=False
        )
        
        embed.set_footer(text="SeykooFX - Statistiques des Tickets")
        
        await ctx.send(embed=embed)

def setup_ticket_system(bot):
    """Configure le système de tickets"""
    # Ajouter les vues persistantes
    bot.add_view(TicketView())
    bot.add_view(TicketControlView())
    # Ajouter la vue pour les boutons de langue (les custom_id sont fixes donc elle fonctionne après redémarrage)
    # Note: On crée une vue temporaire juste pour enregistrer les custom_id
    temp_view = LanguageSelectView(0, "commande")  # ID temporaire, ne sera pas utilisé
    bot.add_view(temp_view)
    # Ajouter les commandes
    try:
        bot.add_cog(TicketCommands(bot))
        print("✅ Système de tickets configuré")
        print("   - Commandes chargées: !adduser, !close, !ticketcount")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du cog TicketCommands: {e}") 
