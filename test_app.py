#!/usr/bin/env python3
"""
Script de test pour NetPing Monitor
Teste les différents modules de l'application
"""

import os
import sys
import time
from datetime import datetime

def test_imports():
    """Teste l'importation des modules"""
    print("Test des importations...")
    
    modules = [
        'tkinter',
        'threading',
        'json',
        'subprocess',
        'platform',
        'winsound'
    ]
    
    for module in modules:
        try:
            if module == 'tkinter':
                import tkinter
                print(f"  ✅ {module}: OK")
            elif module == 'winsound':
                import winsound
                print(f"  ✅ {module}: OK (Windows seulement)")
            else:
                __import__(module)
                print(f"  ✅ {module}: OK")
        except ImportError as e:
            if module == 'winsound' and sys.platform != 'win32':
                print(f"  ⚠ {module}: Non disponible (pas Windows)")
            else:
                print(f"  ❌ {module}: Échec - {e}")
    
    print()

def test_local_modules():
    """Teste les modules locaux"""
    print("Test des modules locaux...")
    
    local_modules = [
        'network_monitor',
        'target_manager', 
        'alert_system',
        'history_logger'
    ]
    
    for module in local_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}.py: OK")
        except ImportError as e:
            print(f"  ❌ {module}.py: Échec - {e}")
    
    print()

def test_network_monitor():
    """Teste le module de surveillance réseau"""
    print("Test du module NetworkMonitor...")
    
    try:
        from network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        
        # Test de validation d'adresse
        test_addresses = [
            ('8.8.8.8', True),
            ('www.google.com', True),
            ('', False),
            ('invalid', False),
            ('192.168.1.1', True)
        ]
        
        for address, expected in test_addresses:
            result = monitor.validate_address(address)
            status = "✅" if result == expected else "❌"
            print(f"  {status} Validation '{address}': {result} (attendu: {expected})")
        
        # Test de ping rapide (seulement si réseau disponible)
        print("\n  Test de ping (peut prendre quelques secondes)...")
        test_ping = monitor.ping_target('8.8.8.8', timeout=3)
        
        if test_ping['success']:
            print(f"  ✅ Ping réussi: {test_ping['response_time']}ms")
        else:
            print(f"  ⚠ Ping échoué: {test_ping['error']}")
            print(f"    (Cela peut être normal si hors ligne ou pare-feu actif)")
        
        # Informations réseau
        network_info = monitor.get_network_info()
        print(f"  ℹ Hostname: {network_info['hostname']}")
        print(f"  ℹ IP locale: {network_info['local_ip']}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()

def test_target_manager():
    """Teste le gestionnaire de cibles"""
    print("Test du module TargetManager...")
    
    try:
        from target_manager import TargetManager
        
        # Utiliser un fichier de test
        test_file = "test_targets_temp.json"
        manager = TargetManager(test_file)
        
        # Ajouter des cibles de test
        test_targets = [
            {'name': 'Test 1', 'address': '192.168.1.1', 'interval': 30},
            {'name': 'Test 2', 'address': '192.168.1.2', 'interval': 45}
        ]
        
        for target in test_targets:
            try:
                manager.add_target(target)
                print(f"  ✅ Ajout: {target['name']}")
            except ValueError as e:
                print(f"  ❌ Erreur d'ajout: {e}")
        
        # Vérifier le nombre de cibles
        target_count = len(manager.targets)
        print(f"  ℹ Cibles totales: {target_count}")
        
        # Statistiques
        stats = manager.get_statistics()
        print(f"  ℹ Statistiques générées: {len(stats)} items")
        
        # Nettoyer
        manager.clear_all_targets()
        if os.path.exists(test_file):
            os.remove(test_file)
        print(f"  ✅ Nettoyage terminé")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()

def test_alert_system():
    """Teste le système d'alertes"""
    print("Test du module AlertSystem...")
    
    try:
        from alert_system import AlertSystem
        
        alert = AlertSystem()
        
        # Test configuration
        print(f"  ℹ Alertes sonores: {'Activées' if alert.config['sound_enabled'] else 'Désactivées'}")
        print(f"  ℹ Alertes visuelles: {'Activées' if alert.config['visual_enabled'] else 'Désactivées'}")
        
        # Test d'alerte (simulée)
        test_target = {'name': 'Serveur Test', 'address': '192.168.1.100'}
        print(f"  ⚠ Déclenchement d'alerte de test...")
        
        # Désactiver le son pour le test
        original_sound = alert.config['sound_enabled']
        alert.config['sound_enabled'] = False
        
        alert.trigger_alert(test_target)
        
        # Vérifier l'alerte
        active_alerts = alert.get_active_alerts()
        print(f"  ℹ Alertes actives: {len(active_alerts)}")
        
        # Nettoyer
        alert.clear_all_alerts()
        alert.config['sound_enabled'] = original_sound
        print(f"  ✅ Alertes nettoyées")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()

def test_history_logger():
    """Teste le journal d'historique"""
    print("Test du module HistoryLogger...")
    
    try:
        from history_logger import HistoryLogger
        
        # Utiliser un répertoire de test
        test_dir = "test_logs_temp"
        logger = HistoryLogger(test_dir)
        
        # Enregistrer une panne de test
        test_target = {
            'name': 'Serveur Test',
            'address': '192.168.1.100',
            'response_time': 25,
            'failures': 3,
            'consecutive_failures': 3
        }
        
        logger.log_outage(test_target)
        print(f"  ✅ Panne enregistrée")
        
        # Vérifier l'historique
        history = logger.get_outage_history()
        print(f"  ℹ Entrées historiques: {len(history)}")
        
        # Statistiques
        stats = logger.get_outage_statistics(days=1)
        print(f"  ℹ Statistiques générées")
        
        # Nettoyer
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print(f"  ✅ Nettoyage terminé")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("TEST NETPING MONITOR")
    print("=" * 60)
    print()
    
    # Vérifier Python
    print(f"Python: {sys.version}")
    print(f"Plateforme: {sys.platform}")
    print(f"Répertoire: {os.getcwd()}")
    print()
    
    # Exécuter les tests
    tests = [
        test_imports,
        test_local_modules,
        test_network_monitor,
        test_target_manager,
        test_alert_system,
        test_history_logger
    ]
    
    for test_func in tests:
        test_func()
        time.sleep(0.5)  # Pause pour lisibilité
    
    # Résumé
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print()
    print("L'application NetPing Monitor devrait être fonctionnelle.")
    print()
    print("Prochaines étapes:")
    print("1. Lancez l'application: python main.py")
    print("2. Ou utilisez le script: start.bat")
    print("3. Ajoutez des cibles à surveiller")
    print("4. Démarrez la surveillance")
    print()
    print("Pour générer un exécutable .exe:")
    print("pip install pyinstaller")
    print("pyinstaller --onefile --windowed main.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\nErreur inattendue: {e}")
    
    input("\nAppuyez sur Entrée pour quitter...")