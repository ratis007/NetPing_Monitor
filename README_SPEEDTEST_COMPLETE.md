# Module SpeedTest pour NetPing Monitor

## Table des matières
1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Utilisation](#utilisation)
6. [Configuration](#configuration)
7. [Dépannage](#dépannage)
8. [API](#api)
9. [Développement](#développement)

## Présentation

Le module SpeedTest est une extension complète pour NetPing Monitor qui permet de surveiller la qualité de votre connexion Internet. Il intègre des tests de débit, des alertes automatisées, des rapports Excel avec graphiques, et une interface utilisateur moderne.

## Fonctionnalités

### ✅ Tests Réseau
- **Test complet** : Ping, download, upload et jitter
- **Test rapide** : Ping uniquement
- **Détection automatique** des serveurs SpeedTest
- **Évaluation du statut** selon les seuils configurés
- **Cache des résultats** pour éviter les appels inutiles

### 📅 Planification Automatique
- **Tests planifiés** aux heures définies
- **Activation/désactivation** individuelle
- **Mode quotidien/hebdomadaire**
- **Exécution en arrière-plan**
- **Notifications des tests manqués**

### 📊 Stockage & Analyse
- **Base de données JSON** structurée
- **Statistiques journalières/mensuelles**
- **Export CSV** pour analyse externe
- **Filtres par date/heure**
- **Détection des tendances**

### 📈 Rapports & Graphiques
- **Rapports Excel journaliers**
- **Graphiques d'évolution** (ping, débit)
- **Résumés statistiques**
- **Export automatique**
- **Format professionnel**

### 🔔 Notifications
- **Email** avec templates HTML
- **WhatsApp** via API
- **Alertes configurables** :
  - Test échoué
  - Ping critique (> seuil)
  - Download faible (< seuil)
  - Upload faible (< seuil)
  - Changement d'IP
  - Test manqué
- **Rate limiting** pour éviter le spam

### 🎨 Interface Utilisateur
- **Tableau de bord moderne** (CustomTkinter)
- **Cartes statistiques** en temps réel
- **Historique des tests**
- **Configuration graphique** :
  - Planification
  - Notifications
  - Seuils d'alerte
- **Mode sombre** professionnel

## Architecture

```
📁 NetPing Monitor/
├── 📄 speedtest_ip_detector.py    # Détection IP publique
├── 📄 speedtest_runner.py         # Exécution des tests
├── 📄 speedtest_scheduler.py      # Planification
├── 📄 speedtest_storage.py        # Stockage des résultats
├── 📄 speedtest_notifier.py       # Notifications
├── 📄 speedtest_excel_exporter.py # Rapports Excel
├── 📄 speedtest_manager.py        # Orchestration
├── 📄 ui_speedtest.py             # Interface utilisateur
├── 📄 main_with_speedtest.py      # Application complète
├── 📄 requirements.txt            # Dépendances
├── 📄 start_speedtest.bat         # Script de lancement
└── 📄 test_speedtest_integration.py # Tests
```

### Flot de données
1. **Détection IP** → 2. **Test SpeedTest** → 3. **Évaluation statut**
4. **Stockage** → 5. **Notifications** → 6. **Interface utilisateur**
7. **Rapports périodiques**

## Installation

### Prérequis
- Python 3.8 ou supérieur
- Tkinter (inclus avec Python standard sous Windows)
- Connexion Internet

### Installation des dépendances
```bash
# Installer toutes les dépendances
pip install -r requirements.txt

# Ou installer uniquement l'essentiel
pip install customtkinter speedtest-cli requests
```

### Vérification de l'installation
```bash
# Exécuter le script de test
python test_speedtest_integration.py

# Tester l'interface
python ui_speedtest.py
```

## Utilisation

### Lancement rapide
```bash
# Interface SpeedTest uniquement
python ui_speedtest.py

# Application complète NetPing Monitor
python main_with_speedtest.py

# Script batch (Windows)
start_speedtest.bat
```

### Interface Utilisateur

#### 📊 Tableau de bord principal
- **Cartes statistiques** : IP, Ping, Download, Upload
- **Test manuel** : Bouton "⚡ Test Manuel"
- **Test rapide** : Bouton "⚡ Test Rapide"
- **Historique** : Tests du jour
- **Statistiques** : Résumés journaliers

#### ⚙️ Configuration
- **Planification** : Tests automatisés
- **Notifications** : Email et WhatsApp
- **Seuils** : Alertes personnalisées
- **Historique** : Consultation détaillée

#### 📈 Rapports
- **Export Excel** : Rapports journaliers/mensuels
- **Graphiques** : Évolution des performances
- **Statistiques** : Analyse détaillée

## Configuration

### Fichiers de configuration

#### `notification_config.json`
```json
{
  "email_enabled": true,
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587,
  "email_username": "votre.email@gmail.com",
  "email_password": "votre-mot-de-passe",
  "email_recipients": ["destinataire@example.com"],
  "whatsapp_enabled": false,
  "ping_threshold_critical": 200,
  "ping_threshold_warning": 100,
  "download_threshold_critical": 10,
  "download_threshold_warning": 50,
  "upload_threshold_critical": 5,
  "upload_threshold_warning": 20
}
```

#### `speedtest_schedule.json`
```json
[
  {
    "hour": 8,
    "minute": 0,
    "enabled": true,
    "daily": true
  },
  {
    "hour": 12,
    "minute": 0,
    "enabled": true,
    "daily": true
  }
]
```

### Configuration Email
1. Activer les notifications email
2. Configurer les paramètres SMTP
3. Ajouter les destinataires
4. Tester la configuration

### Configuration WhatsApp
1. Activer les notifications WhatsApp
2. Configurer l'URL de l'API
3. Configurer la clé API
4. Ajouter les numéros de téléphone

## Dépannage

### Problèmes courants

#### ❌ "Module non trouvé"
```bash
# Vérifier que Python peut trouver les modules
python -c "import sys; print(sys.path)"
```

#### ❌ "Erreur d'import"
```bash
# Tester l'importation
python -c "from speedtest_ip_detector import IPDetector; print('OK')"
```

#### ❌ "Erreur de dépendance"
```bash
# Vérifier les dépendances
pip list | grep -E "customtkinter|speedtest|requests"
```

#### ❌ "Interface ne s'affiche pas"
```bash
# Tester Tkinter
python -c "import tkinter; tkinter._test()"
```

#### ❌ "Test SpeedTest échoué"
1. Vérifier la connexion Internet
2. Tester manuellement : `speedtest-cli`
3. Vérifier le pare-feu

### Logs de débogage
```python
# Activer les logs détaillés
import speedtest
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API

### SpeedTestManager
```python
from speedtest_manager import SpeedTestManager

# Initialisation
manager = SpeedTestManager("reports/speedtests")

# Démarrer/arrêter
manager.start()
manager.stop()

# Exécuter un test
result = manager.run_manual_test()

# Récupérer des données
status = manager.get_current_status()
results = manager.get_daily_results()
stats = manager.generate_statistics(days=30)

# Export
report_path = manager.export_daily_report()
```

### Interface programmatique
```python
# Tests individuels
from speedtest_runner import SpeedTestRunner
runner = SpeedTestRunner()
result = runner.run_speedtest()

# Détection IP
from speedtest_ip_detector import IPDetector
detector = IPDetector()
ip_info = detector.detect()

# Stockage
from speedtest_storage import SpeedTestStorage
storage = SpeedTestStorage("data")
storage.save_result(result)

# Notifications
from speedtest_notifier import SpeedTestNotifier
notifier = SpeedTestNotifier()
alerts = notifier.check_and_notify(result)
```

## Développement

### Structure du code
```
📁 speedtest_ip_detector.py
├── class IPDetector
│   ├── detect() - Détection IP complète
│   ├── get_ip_only() - IP uniquement
│   └── cache - Système de cache

📁 speedtest_runner.py
├── class SpeedTestRunner
│   ├── run_speedtest() - Test complet
│   ├── quick_test() - Test rapide
│   ├── set_thresholds() - Configurer les seuils
│   └── evaluate_status() - Évaluer le résultat

📁 speedtest_scheduler.py
├── class ScheduledTest
├── class SpeedTestScheduler
│   ├── add_test() - Ajouter un test
│   ├── start()/stop() - Contrôle
│   └── on_test_due - Callback

📁 speedtest_storage.py
├── class SpeedTestStorage
│   ├── save_result() - Sauvegarde
│   ├── get_results_*() - Récupération
│   └── get_statistics() - Statistiques

📁 speedtest_notifier.py
├── class NotificationConfig
├── class EmailNotifier
├── class WhatsAppNotifier
└── class SpeedTestNotifier
```

### Ajouter de nouvelles fonctionnalités

#### 1. Nouveau type d'alerte
```python
# Ajouter dans SpeedTestNotifier.check_and_notify()
if nouvelle_condition:
    alerts.append('nouveau_type')
    self._send_alerts(result, 'nouveau_type')
```

#### 2. Nouvelle source de détection IP
```python
# Ajouter dans IPDetector._get_ip_from_service()
services = {
    'nouveau_service': 'https://api.nouveau-service.com/ip',
}
```

#### 3. Nouveau format d'export
```python
# Créer SpeedTestCSVExporter.py
class SpeedTestCSVExporter:
    def generate_report(self, results):
        # Implémenter l'export CSV
```

### Tests
```bash
# Tests unitaires
python -m pytest test_speedtest_*.py

# Tests d'intégration
python test_speedtest_integration.py

# Tests d'interface
python ui_speedtest.py
```

### Bonnes pratiques
- Suivre les conventions PEP 8
- Documenter toutes les fonctions
- Gérer les erreurs correctement
- Utiliser des types hints
- Écrire des tests unitaires

## Licence et crédits

### Licence
Projet open-source sous licence MIT

### Crédits
- **NetPing Monitor** : Supervision réseau
- **speedtest-cli** : Tests de débit
- **CustomTkinter** : Interface moderne
- **openpyxl/pandas** : Rapports Excel
- **matplotlib** : Graphiques

### Contribuer
1. Fork le projet
2. Créer une branche
3. Faire les modifications
4. Tester les changements
5. Soumettre une pull request

### Support
- Documentation : README.md
- Issues : GitHub issues
- Contact : via le dépôt principal

---

## Résumé des commandes utiles

```bash
# Installation
pip install -r requirements.txt

# Tests
python test_speedtest_integration.py
python ui_speedtest.py
python main_with_speedtest.py

# Lancement
start_speedtest.bat

# Dépendances
pip list | findstr "customtkinter speedtest"

# Diagnostic
python -c "import tkinter; tkinter._test()"
python -c "import speedtest; print('OK')"
```

**Version du module** : 1.0.0  
**Date** : Juin 2026  
**Auteur** : Équipe NetPing Monitor  
**Statut** : Production