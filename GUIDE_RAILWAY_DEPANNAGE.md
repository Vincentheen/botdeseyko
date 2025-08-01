# 🚀 GUIDE DE DÉPANNAGE RAILWAY - Seykoofx

## ❌ **Problèmes Courants et Solutions :**

### 🔧 **1. Configuration Railway**

#### **Variables d'Environnement Requises :**
```env
DISCORD_TOKEN=votre_token_bot_discord_ici
```

#### **Fichiers Requis :**
- ✅ `bot_simplifie.py` - Bot principal
- ✅ `requirements.txt` - Dépendances
- ✅ `Procfile` - Configuration Railway
- ✅ `runtime.txt` - Version Python

### 🚨 **2. Erreurs Courantes :**

#### **Erreur : "No buildpack specified"**
**Solution :**
- Vérifiez que le `Procfile` existe et contient : `worker: python bot_simplifie.py`

#### **Erreur : "Module not found"**
**Solution :**
- Vérifiez que `requirements.txt` contient :
```
discord.py==2.3.2
flask==2.3.3
python-dotenv==1.0.0
```

#### **Erreur : "Token not found"**
**Solution :**
- Ajoutez la variable d'environnement `DISCORD_TOKEN` dans Railway
- Vérifiez que le token est correct

#### **Erreur : "Import error"**
**Solution :**
- Vérifiez que tous les fichiers sont présents :
  - `tickets.py`
  - `reglement.py`
  - `verification.py`
  - `planning.py`
  - `logs.py`

### 🔍 **3. Vérification des Logs Railway :**

#### **Logs de Démarrage Normaux :**
```
🤖 Bot connecté: Seykoofx
📊 ID du bot: 1399410242617475132
------
✅ Tous les systèmes configurés
🚀 Création automatique des panels...
📡 Serveur trouvé: Seykoofx
🎫 Création du panel de tickets...
✅ Panel de tickets créé dans #tickets
📜 Création du panel de règlement...
✅ Panel de règlement créé dans #règlement
🔐 Création du panel de vérification...
✅ Panel de vérification créé dans #vérification
📅 Création du panel de planning...
✅ Panel de planning créé dans #planning
🎉 Création automatique de tous les panels terminée!
✅ Tous les systèmes sont maintenant opérationnels!
🚀 Bot simplifié Seykoofx démarré avec succès!
```

#### **Logs d'Erreur Courants :**
```
❌ Serveur Discord non trouvé
❌ Canal de tickets introuvable
❌ Erreur création panel tickets: [erreur]
```

### 🛠️ **4. Solutions par Étape :**

#### **Étape 1 : Vérifier la Configuration**
1. **Variables d'environnement** dans Railway
2. **Fichiers requis** dans le repository
3. **Procfile** avec `worker: python bot_simplifie.py`

#### **Étape 2 : Vérifier les Dépendances**
1. **requirements.txt** avec les bonnes versions
2. **runtime.txt** avec Python 3.11.7
3. **Tous les modules** présents

#### **Étape 3 : Vérifier les Permissions**
1. **Token Discord** valide
2. **Permissions du bot** dans Discord
3. **IDs des canaux** corrects

### 📋 **5. Checklist de Déploiement :**

- [ ] **Repository GitHub** connecté à Railway
- [ ] **Variables d'environnement** configurées
- [ ] **Tous les fichiers** présents
- [ ] **Procfile** correct
- [ ] **requirements.txt** complet
- [ ] **runtime.txt** spécifié
- [ ] **Token Discord** valide
- [ ] **Permissions bot** correctes
- [ ] **IDs des canaux** vérifiés

### 🎯 **6. Test de Fonctionnement :**

#### **Commandes de Test :**
```bash
!info - Informations du bot
!test_tickets - Test du système de tickets
!send_all - Recréer tous les panels
!force_send - Forcer l'envoi automatique
```

### 🚀 **7. Redéploiement :**

1. **Modifier un fichier** dans GitHub
2. **Railway redéploie** automatiquement
3. **Vérifier les logs** Railway
4. **Tester les commandes** dans Discord

### 📞 **8. Support :**

Si le problème persiste :
1. **Vérifiez les logs** Railway
2. **Testez localement** d'abord
3. **Vérifiez les permissions** Discord
4. **Contactez le support** si nécessaire

---

**💡 Le bot simplifié est optimisé pour Railway et devrait fonctionner parfaitement !** 