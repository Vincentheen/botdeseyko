# Guide de Résolution des Problèmes de Logs - Seykoofx

## 🔍 Diagnostic des Problèmes

### Problème Identifié
Les logs vocaux (1400614430336614511) et de modération (1400614542538707097) ne fonctionnent pas.

### Causes Possibles

1. **Canaux introuvables** - Les canaux de logs n'existent pas ou ont été supprimés
2. **Permissions insuffisantes** - Le bot n'a pas les permissions nécessaires
3. **Intents manquants** - Les intents vocaux ne sont pas activés
4. **Événements non enregistrés** - Les événements Discord ne sont pas correctement configurés
5. **Erreurs dans le code** - Problèmes dans la logique des logs

## 🛠️ Solutions

### 1. Vérification des Canaux

Vérifiez que les canaux existent dans votre serveur Discord :

```bash
# IDs des canaux de logs
Voice Logs: 1400614430336614511
Modération Logs: 1400614542538707097
```

**Solution :**
- Allez dans votre serveur Discord
- Vérifiez que les canaux existent
- Si non, créez-les avec les bons IDs

### 2. Vérification des Permissions

Le bot doit avoir les permissions suivantes :

- **Voir les canaux** (`View Channel`)
- **Envoyer des messages** (`Send Messages`)
- **Utiliser les embeds** (`Embed Links`)
- **Attacher des fichiers** (`Attach Files`)
- **Lire l'historique** (`Read Message History`)

**Solution :**
1. Allez dans les paramètres du serveur
2. Rôles → Bot Seykoofx
3. Activez les permissions nécessaires

### 3. Activation des Intents

Les intents vocaux doivent être activés :

```python
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True  # IMPORTANT pour les logs vocaux
```

**Solution :**
- Vérifiez que `intents.voice_states = True` est présent dans `bot_unifie.py`

### 4. Configuration Discord Developer Portal

Dans le Discord Developer Portal :

1. Allez sur https://discord.com/developers/applications
2. Sélectionnez votre bot
3. Bot → Privileged Gateway Intents
4. Activez :
   - **Server Members Intent**
   - **Message Content Intent**
   - **Presence Intent** (optionnel)

## 🧪 Tests de Diagnostic

### Test 1 : Diagnostic Automatique

```bash
cd bot
python diagnostic_logs_probleme.py
```

### Test 2 : Test des Canaux

```bash
cd bot
python test_logs_final.py
```

### Test 3 : Test via Commande

Dans Discord, utilisez la commande :
```
!test_logs
```

### Test 4 : Test de Modération

Dans Discord, utilisez la commande :
```
!test_moderation
```

## 📋 Checklist de Vérification

- [ ] Les canaux de logs existent dans le serveur
- [ ] Le bot a les permissions nécessaires
- [ ] Les intents vocaux sont activés
- [ ] Le token Discord est correct
- [ ] Le bot est connecté au bon serveur
- [ ] Les événements sont correctement enregistrés

## 🔧 Corrections Apportées

### 1. Modification du système de logs (`logs.py`)

- ✅ Correction de la structure des événements
- ✅ Ajout de vérifications de sécurité
- ✅ Amélioration de la gestion des erreurs

### 2. Intégration dans le bot principal (`bot_unifie.py`)

- ✅ Ajout des intents vocaux
- ✅ Intégration des gestionnaires d'événements
- ✅ Ajout de la gestion d'erreurs

### 3. Scripts de diagnostic

- ✅ `diagnostic_logs_probleme.py` - Diagnostic complet
- ✅ `test_logs_final.py` - Test final
- ✅ `GUIDE_RESOLUTION_LOGS.md` - Guide de résolution

## 🚀 Démarrage

1. **Redémarrez le bot :**
```bash
cd bot
python bot_unifie.py
```

2. **Vérifiez les logs de démarrage :**
```
📊 Système de logs activé
✅ Canal Voice Logs trouvé
✅ Canal Modération Logs trouvé
```

3. **Testez les logs :**
```
!test_logs
!test_moderation
```

## 📞 Support

Si les problèmes persistent :

1. Vérifiez les logs d'erreur du bot
2. Utilisez les scripts de diagnostic
3. Vérifiez les permissions du bot
4. Testez avec les commandes de diagnostic

## 🔄 Mise à Jour

Les modifications apportées :

1. **logs.py** - Correction de la structure des événements
2. **bot_unifie.py** - Ajout des intents vocaux et gestionnaires
3. **Nouveaux scripts** - Diagnostic et tests

Tous les changements sont rétrocompatibles et n'affectent pas les autres fonctionnalités du bot. 