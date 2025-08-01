"""
Système de Planning - Seykoofx
==============================

Système de planning avec boutons pour créer, modifier et supprimer
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

# Configuration du canal de planning
PLANNING_CHANNEL_ID = 1400608607002820770

# Fichier pour stocker les données de planning
PLANNING_FILE = "planning_data.json"

# Rôles autorisés pour la gestion du planning
PLANNING_MANAGER_ROLES = [
    1335705793697288213,  # 『👤』Responsable Support
    1335706767908405432,  # 『👤』Relation Clients
    1335707516352331949,  # 『👤』Responsable Commercial
    1113214565619085424,  # 𝐀𝐝𝐦𝐢𝐧 technique
    1399517642884124702,  # 『👤』Moderateur technique
    1096054762862026833   # Directeur Général
]

def has_planning_permission(user: discord.Member) -> bool:
    """Vérifie si l'utilisateur a les permissions de gestion du planning"""
    user_roles = [role.id for role in user.roles]
    return any(role_id in user_roles for role_id in PLANNING_MANAGER_ROLES)

def load_planning_data():
    """Charge les données de planning"""
    if os.path.exists(PLANNING_FILE):
        try:
            with open(PLANNING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_planning_data(data):
    """Sauvegarde les données de planning"""
    try:
        with open(PLANNING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Erreur sauvegarde planning: {e}")

class PlanningView(discord.ui.View):
    """Vue avec les boutons pour le planning"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📅 Ajouter Date", style=discord.ButtonStyle.primary, custom_id="add_planning")
    async def add_planning(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_planning_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour gérer le planning.", ephemeral=True)
            return
        
        await show_add_planning_modal(interaction)
    
    @discord.ui.button(label="✏️ Modifier Date", style=discord.ButtonStyle.secondary, custom_id="edit_planning")
    async def edit_planning(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_planning_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour gérer le planning.", ephemeral=True)
            return
        
        await show_edit_planning_modal(interaction)
    
    @discord.ui.button(label="🗑️ Supprimer Date", style=discord.ButtonStyle.danger, custom_id="delete_planning")
    async def delete_planning(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_planning_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas les permissions pour gérer le planning.", ephemeral=True)
            return
        
        await show_delete_planning_modal(interaction)

class AddPlanningModal(discord.ui.Modal, title="Ajouter une date au planning"):
    """Modal pour ajouter une date au planning"""
    
    def __init__(self):
        super().__init__()
        self.title_input = discord.ui.TextInput(
            label="Titre du projet",
            placeholder="Ex: Trailer GTA VI",
            min_length=3,
            max_length=100,
            required=True
        )
        self.date_input = discord.ui.TextInput(
            label="Date (JJ/MM/AAAA)",
            placeholder="Ex: 15/12/2024",
            min_length=8,
            max_length=10,
            required=True
        )
        self.time_input = discord.ui.TextInput(
            label="Heure (HH:MM)",
            placeholder="Ex: 14:30",
            min_length=4,
            max_length=5,
            required=True
        )
        self.priority_input = discord.ui.TextInput(
            label="Priorité (1-5)",
            placeholder="Ex: 3",
            min_length=1,
            max_length=1,
            required=True
        )
        self.description_input = discord.ui.TextInput(
            label="Description",
            placeholder="Description du projet...",
            min_length=10,
            max_length=500,
            required=True,
            style=discord.TextStyle.paragraph
        )
        
        self.add_item(self.title_input)
        self.add_item(self.date_input)
        self.add_item(self.time_input)
        self.add_item(self.priority_input)
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Valider la date
            date_str = self.date_input.value
            time_str = self.time_input.value
            
            try:
                date_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            except:
                await interaction.response.send_message("❌ Format de date/heure invalide. Utilisez JJ/MM/AAAA HH:MM", ephemeral=True)
                return
            
            # Valider la priorité
            try:
                priority = int(self.priority_input.value)
                if priority < 1 or priority > 5:
                    raise ValueError()
            except:
                await interaction.response.send_message("❌ Priorité invalide. Utilisez un nombre entre 1 et 5.", ephemeral=True)
                return
            
            # Charger les données existantes
            planning_data = load_planning_data()
            
            # Créer l'entrée
            entry_id = f"planning_{len(planning_data) + 1}"
            entry = {
                "id": entry_id,
                "title": self.title_input.value,
                "date": date_obj.isoformat(),
                "priority": priority,
                "description": self.description_input.value,
                "created_by": interaction.user.id,
                "created_at": datetime.now().isoformat()
            }
            
            planning_data[entry_id] = entry
            save_planning_data(planning_data)
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Date Ajoutée",
                description=f"**{self.title_input.value}** a été ajouté au planning.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Date", value=date_obj.strftime("%d/%m/%Y %H:%M"), inline=True)
            embed.add_field(name="Priorité", value=f"{priority}/5", inline=True)
            embed.add_field(name="Description", value=self.description_input.value[:100] + "...", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Mettre à jour le planning
            await update_planning_display(interaction.guild)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de l'ajout : {e}", ephemeral=True)

class EditPlanningModal(discord.ui.Modal, title="Modifier une date du planning"):
    """Modal pour modifier une date du planning"""
    
    def __init__(self):
        super().__init__()
        self.entry_id_input = discord.ui.TextInput(
            label="ID de l'entrée",
            placeholder="Ex: planning_1",
            min_length=8,
            max_length=20,
            required=True
        )
        self.title_input = discord.ui.TextInput(
            label="Nouveau titre",
            placeholder="Ex: Trailer GTA VI",
            min_length=3,
            max_length=100,
            required=True
        )
        self.date_input = discord.ui.TextInput(
            label="Nouvelle date (JJ/MM/AAAA)",
            placeholder="Ex: 15/12/2024",
            min_length=8,
            max_length=10,
            required=True
        )
        self.time_input = discord.ui.TextInput(
            label="Nouvelle heure (HH:MM)",
            placeholder="Ex: 14:30",
            min_length=4,
            max_length=5,
            required=True
        )
        self.priority_input = discord.ui.TextInput(
            label="Nouvelle priorité (1-5)",
            placeholder="Ex: 3",
            min_length=1,
            max_length=1,
            required=True
        )
        
        self.add_item(self.entry_id_input)
        self.add_item(self.title_input)
        self.add_item(self.date_input)
        self.add_item(self.time_input)
        self.add_item(self.priority_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Charger les données
            planning_data = load_planning_data()
            entry_id = self.entry_id_input.value
            
            if entry_id not in planning_data:
                await interaction.response.send_message("❌ Entrée introuvable.", ephemeral=True)
                return
            
            # Valider la date
            date_str = self.date_input.value
            time_str = self.time_input.value
            
            try:
                date_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            except:
                await interaction.response.send_message("❌ Format de date/heure invalide.", ephemeral=True)
                return
            
            # Valider la priorité
            try:
                priority = int(self.priority_input.value)
                if priority < 1 or priority > 5:
                    raise ValueError()
            except:
                await interaction.response.send_message("❌ Priorité invalide.", ephemeral=True)
                return
            
            # Mettre à jour l'entrée
            planning_data[entry_id]["title"] = self.title_input.value
            planning_data[entry_id]["date"] = date_obj.isoformat()
            planning_data[entry_id]["priority"] = priority
            planning_data[entry_id]["updated_by"] = interaction.user.id
            planning_data[entry_id]["updated_at"] = datetime.now().isoformat()
            
            save_planning_data(planning_data)
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Date Modifiée",
                description=f"**{self.title_input.value}** a été modifié.",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            embed.add_field(name="Date", value=date_obj.strftime("%d/%m/%Y %H:%M"), inline=True)
            embed.add_field(name="Priorité", value=f"{priority}/5", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Mettre à jour le planning
            await update_planning_display(interaction.guild)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la modification : {e}", ephemeral=True)

class DeletePlanningModal(discord.ui.Modal, title="Supprimer une date du planning"):
    """Modal pour supprimer une date du planning"""
    
    def __init__(self):
        super().__init__()
        self.entry_id_input = discord.ui.TextInput(
            label="ID de l'entrée à supprimer",
            placeholder="Ex: planning_1",
            min_length=8,
            max_length=20,
            required=True
        )
        
        self.add_item(self.entry_id_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Charger les données
            planning_data = load_planning_data()
            entry_id = self.entry_id_input.value
            
            if entry_id not in planning_data:
                await interaction.response.send_message("❌ Entrée introuvable.", ephemeral=True)
                return
            
            # Récupérer les informations avant suppression
            entry = planning_data[entry_id]
            title = entry["title"]
            
            # Supprimer l'entrée
            del planning_data[entry_id]
            save_planning_data(planning_data)
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Date Supprimée",
                description=f"**{title}** a été supprimé du planning.",
                color=0xff0000,
                timestamp=datetime.now()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Mettre à jour le planning
            await update_planning_display(interaction.guild)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la suppression : {e}", ephemeral=True)

async def show_add_planning_modal(interaction: discord.Interaction):
    """Affiche le modal d'ajout de planning"""
    modal = AddPlanningModal()
    await interaction.response.send_modal(modal)

async def show_edit_planning_modal(interaction: discord.Interaction):
    """Affiche le modal de modification de planning"""
    modal = EditPlanningModal()
    await interaction.response.send_modal(modal)

async def show_delete_planning_modal(interaction: discord.Interaction):
    """Affiche le modal de suppression de planning"""
    modal = DeletePlanningModal()
    await interaction.response.send_modal(modal)

async def update_planning_display(guild):
    """Met à jour l'affichage du planning"""
    try:
        planning_channel = guild.get_channel(PLANNING_CHANNEL_ID)
        if not planning_channel:
            return
        
        # Charger les données
        planning_data = load_planning_data()
        
        if not planning_data:
            embed = discord.Embed(
                title="📅 Planning Seykoofx",
                description="Aucune date planifiée pour le moment.",
                color=0x0099ff,
                timestamp=datetime.now()
            )
        else:
            # Trier par date
            sorted_entries = sorted(planning_data.values(), key=lambda x: x["date"])
            
            embed = discord.Embed(
                title="📅 Planning Seykoofx",
                description="Dates planifiées :",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            for entry in sorted_entries:
                date_obj = datetime.fromisoformat(entry["date"])
                priority_emoji = "🔴" if entry["priority"] == 5 else "🟠" if entry["priority"] >= 3 else "🟡" if entry["priority"] >= 2 else "🟢"
                
                embed.add_field(
                    name=f"{priority_emoji} {entry['title']} (ID: {entry['id']})",
                    value=f"📅 {date_obj.strftime('%d/%m/%Y %H:%M')}\n📝 {entry['description'][:50]}...",
                    inline=False
                )
        
        # Créer la vue avec les boutons
        view = PlanningView()
        
        # Supprimer les anciens messages et envoyer le nouveau
        try:
            await planning_channel.purge()
        except:
            pass
        
        await planning_channel.send(embed=embed, view=view)
        
    except Exception as e:
        print(f"❌ Erreur mise à jour planning: {e}")

async def create_planning_panel(bot, guild):
    """Crée le panel de planning"""
    await update_planning_display(guild)

def setup_planning_system(bot):
    """Configure le système de planning"""
    print("✅ Système de planning configuré") 