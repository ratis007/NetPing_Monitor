# Guide d'installation et d'utilisation - NetPing Monitor

## 📋 Résumé du projet

NetPing Monitor est une application desktop de monitoring réseau écrite en Python avec Tkinter. Elle permet de surveiller automatiquement le ping de plusieurs sites, serveurs ou adresses IP, et d'alerter l'utilisateur lorsqu'une cible devient inaccessible.

## 🎯 Fonctionnalités implémentées

### ✅ **Fonctionnalités principales**
1. **Ajout de cibles** avec nom, adresse IP/domaine et intervalle de vérification
2. **Surveillance automatique** avec ping à intervalle régulier
3. **Affichage du statut** en temps réel (Online/Offline)
4. **Temps de réponse** en millisecondes
5. **Heure du dernier contrôle**
6. **Détection de panne** après 3 échecs consécutifs
7. **Alertes visuelles et sonores** lors des pannes
8. **Historique des pannes** dans des fichiers locaux (JSON/CSV)
9. **Interface simple** avec tableau de bord lisible

### ✅ **Modules développés**
- `main.py` : Interface graphique principale (Tkinter)
- `network_monitor.py` : Module de ping réseau (compatible Windows)
- `target_manager.py` : Gestion et persistance des cibles
- `alert_system.py` : Système d'alertes visuelles et sonores
- `history_logger.py` : Journalisation des pannes
- `requirements.txt` : Dépendances du projet
- `README.md` : Documentation complète

### ✅ **Scripts utilitaires**
- `start.bat` : Script de démarrage pour Windows
- `build_exe.bat` : Script de construction d'exécutable .exe
- `test_app.py` : Script de test des modules
- `quick_test.py` : Test rapide de l'interface
- `demo_targets.json` : Exemple de cibles préconfigurées

## 🚀 **Installation rapide**

### Option 1 : Utilisation directe (recommandée)
```bash
# 1. Téléchargez tous les fichiers dans un dossier
# 2. Double-cliquez sur start.bat
# OU
# 3. Exécutez dans un terminal:
python main.py
```

### Option 2 : Installation manuelle
```bash
# 1. Vérifiez que Python 3.7+ est installé
python --version

# 2. Vérifiez Tkinter
python -m tkinter

# 3. Lancez l'application
python main.py
```

## 🛠️ **Génération d'exécutable (.exe)**

Pour créer un fichier exécutable Windows autonome:

```bash
# Méthode 1 : Utilisez le script fourni
build_exe.bat

# Méthode 2 : Manuellement
pip install pyinstaller
pyinstaller --onefile --windowed --name="NetPingMonitor" main.py
```

L'exécutable sera généré dans le dossier `dist/NetPingMonitor.exe`

## 📊 **Utilisation de l'application**

### 1. **Ajouter une cible**
   - Nom: "Google DNS"
   - Adresse: "8.8.8.8"
   - Intervalle: 30 (secondes)
   - Cliquez sur "Ajouter"

### 2. **Démarrer la surveillance**
   - Cliquez sur "▶ Démarrer la surveillance"
   - L'application ping automatiquement les cibles

### 3. **Surveiller les statuts**
   - 🟢 En ligne : Ping réussi
   - 🔴 Hors ligne : 3 échecs consécutifs
   - Temps de réponse affiché en ms

### 4. **Recevoir des alertes**
   - Alerte visuelle : Fenêtre pop-up
   - Alerte sonore : Bips (Windows seulement)
   - Journal : Fichier logs/outage_history.json

## 🔧 **Structure des fichiers**

```
NetPing Monitor/
├── main.py              # Application principale
├── network_monitor.py   # Ping réseau (Windows/Linux/macOS)
├── target_manager.py    # Gestion des cibles (JSON)
├── alert_system.py      # Alertes visuelles/sonores
├── history_logger.py    # Historique des pannes
├── requirements.txt     # Dépendances (Tkinter)
├── README.md           # Documentation complète
├── start.bat           # Script de démarrage Windows
├── build_exe.bat       # Script de construction .exe
├── test_app.py         # Tests des modules
├── quick_test.py       # Test rapide
├── demo_targets.json   # Cibles d'exemple
└── logs/              # Historique (créé automatiquement)
    ├── outage_history.json
    └── outage_history.csv
```

## ⚙️ **Configuration**

### Fichiers de configuration générés automatiquement:
- `targets.json` : Sauvegarde des cibles
- `logs/outage_history.json` : Historique JSON
- `logs/outage_history.csv` : Historique CSV

### Paramètres modifiables:
- **Intervalle minimum** : 5 secondes (dans `target_manager.py`)
- **Seuil d'alerte** : 3 échecs consécutifs (dans `main.py`)
- **Durée d'alerte** : 30 secondes (dans `alert_system.py`)

## 🐛 **Dépannage**

### Problème : "Tkinter non trouvé"
```bash
# Windows : Réinstallez Python en cochant "tcl/tk"
# Linux   : sudo apt-get install python3-tk
# macOS   : brew install python-tk
```

### Problème : "Ping échoue"
- Vérifiez votre connexion Internet
- Vérifiez les règles du pare-feu Windows
- Essayez avec une adresse IP simple (8.8.8.8)

### Problème : "Permissions refusées"
- Exécutez en tant qu'administrateur
- Vérifiez les permissions d'écriture dans le dossier

## 📈 **Fonctionnalités avancées**

### Export des données
```python
# L'historique est automatiquement exporté en:
# - JSON: logs/outage_history.json
# - CSV: logs/outage_history.csv
```

### Surveillance multiple
- Jusqu'à 100 cibles simultanément
- Intervalles personnalisables par cible
- Ping simultané optimisé

### Statistiques
- Disponibilité par cible
- Temps de réponse moyen
- Nombre total de pannes
- Cibles les plus problématiques

## 🔄 **Mises à jour futures possibles**

1. **Graphiques** : Visualisation des temps de réponse
2. **Notifications** : Alertes par email/notifications système
3. **Rapports** : Génération automatique de rapports PDF
4. **Monitoring avancé** : Ports TCP, services HTTP
5. **Interface web** : Dashboard accessible via navigateur

## 📞 **Support**

### Pour obtenir de l'aide:
1. Consultez le fichier `README.md`
2. Exécutez les tests: `python test_app.py`
3. Vérifiez les logs dans le dossier `logs/`

### En cas de problème:
1. Vérifiez que tous les fichiers sont présents
2. Exécutez `python quick_test.py` pour tester Tkinter
3. Consultez les messages d'erreur dans la console

## ✅ **Vérification finale**

Pour vérifier que tout fonctionne:

```bash
# Test 1: Vérifier les modules
python test_app.py

# Test 2: Vérifier l'interface
python quick_test.py

# Test 3: Lancer l'application
python main.py
```

## 🎉 **Félicitations !**

Vous avez maintenant une application complète de monitoring réseau:

- ✅ Simple à utiliser (interface graphique)
- ✅ Léger (seulement Tkinter comme dépendance)
- ✅ Portable (fichier .exe possible)
- ✅ Persistant (sauvegarde automatique)
- ✅ Alerte en temps réel
- ✅ Historique complet

**L'application est prête à être utilisée par des techniciens réseau pour surveiller leur infrastructure!**

---

*NetPing Monitor - Développé avec Python et Tkinter*
*Compatibilité: Windows (Linux/macOS avec adaptations mineures)*