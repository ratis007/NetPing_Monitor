# NetPing Monitor

Une application desktop de monitoring réseau écrite en Python avec Tkinter.

## 📋 Fonctionnalités

- ✅ Surveillance automatique du ping vers plusieurs sites/serveurs
- ✅ Ajout de cibles avec nom, adresse et intervalle de vérification
- ✅ Démarrage/arrêt de la surveillance
- ✅ Affichage du statut (Online/Offline)
- ✅ Temps de réponse en millisecondes
- ✅ Heure du dernier contrôle
- ✅ Détection de panne après 3 échecs consécutifs
- ✅ Alertes visuelles et sonores
- ✅ Historique des pannes dans un fichier local
- ✅ Interface simple et lisible

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- Windows (compatible également avec Linux/macOS)

### Installation des dépendances
```bash
# Tkinter est inclus avec Python sur Windows
# Pour vérifier l'installation:
python -m tkinter

# Si Tkinter n'est pas installé (Linux/macOS):
# sudo apt-get install python3-tk  # Debian/Ubuntu
# brew install python-tk           # macOS
```

### Téléchargement
```bash
git clone https://github.com/votre-username/netping-monitor.git
cd netping-monitor
```

## 🎮 Utilisation

### Lancement de l'application
```bash
python main.py
```

### Ajout d'une cible
1. Entrez le nom de la cible (ex: "Google DNS")
2. Entrez l'adresse IP ou domaine (ex: "8.8.8.8" ou "www.google.com")
3. Définissez l'intervalle de vérification (en secondes)
4. Cliquez sur "Ajouter"

### Démarrage de la surveillance
1. Ajoutez au moins une cible
2. Cliquez sur "▶ Démarrer la surveillance"

### Interface principale
- **Tableau des cibles**: Affiche toutes les cibles avec leur statut
- **Journal des événements**: Montre les logs en temps réel
- **Statistiques**: Affiche le nombre de cibles en ligne/hors ligne

## 🛠️ Structure du projet

```
netping-monitor/
├── main.py              # Interface principale Tkinter
├── network_monitor.py   # Module de ping réseau
├── target_manager.py    # Gestion des cibles
├── alert_system.py      # Système d'alertes
├── history_logger.py    # Journalisation des pannes
├── requirements.txt     # Dépendances
├── README.md           # Documentation
└── logs/               # Répertoire des logs (créé automatiquement)
```

## 🔧 Configuration

### Fichiers de configuration
- `targets.json`: Sauvegarde automatique des cibles
- `logs/outage_history.json`: Historique des pannes
- `logs/outage_history.csv`: Historique au format CSV

### Personnalisation
- **Intervalle de vérification**: 5 secondes minimum
- **Seuil d'alerte**: 3 échecs consécutifs
- **Durée d'alerte**: 30 secondes par défaut

## 📦 Génération d'exécutable (.exe)

Pour créer un fichier exécutable Windows:

```bash
# Installer PyInstaller
pip install pyinstaller

# Générer l'exécutable
pyinstaller --onefile --windowed --name="NetPingMonitor" main.py

# L'exécutable sera dans le dossier dist/
```

## 🐛 Dépannage

### Problèmes courants

1. **Tkinter non installé**
   ```bash
   # Windows: Réinstaller Python avec Tkinter coché
   # Linux: sudo apt-get install python3-tk
   # macOS: brew install python-tk
   ```

2. **Ping bloqué par le pare-feu**
   - Vérifiez les règles du pare-feu Windows
   - Autorisez Python à accéder au réseau

3. **Permissions insuffisantes**
   - Exécutez en tant qu'administrateur si nécessaire
   - Vérifiez les permissions d'écriture dans le répertoire

### Logs de débogage
Les logs sont sauvegardés dans le dossier `logs/`:
- `outage_history.json`: Historique structuré
- `outage_history.csv`: Historique format CSV

## 📊 Fonctionnalités avancées

### Export des données
- Export JSON/CSV de l'historique
- Rapports statistiques
- Graphiques de disponibilité (à venir)

### Alertes personnalisables
- Sons d'alerte modifiables
- Durée d'alerte configurable
- Limite d'alertes par heure

### Surveillance avancée
- Ping simultané multiple
- Tests de connexion réseau
- Informations réseau système

## 🤝 Contribution

Les contributions sont les bienvenues! Voici comment contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Icones par [Font Awesome](https://fontawesome.com/)
- Inspiration: Outils de monitoring réseau comme PingPlotter, PRTG
- Communauté Python et Tkinter

## 📞 Support

Pour le support ou les questions:
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Contacter le développeur

---

**NetPing Monitor** - Surveillance réseau simplifiée pour les techniciens