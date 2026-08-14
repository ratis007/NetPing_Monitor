#!/usr/bin/env python3
"""
Test d'intégration du module SpeedTest
Vérifie que tous les composants fonctionnent correctement
"""

import sys
import os

print("=" * 60)
print("TEST D'INTÉGRATION DU MODULE SPEEDTEST")
print("=" * 60)

# Vérifier les dépendances
print("\n1. Vérification des dépendances...")

dependencies = [
    ('customtkinter', 'customtkinter'),
    ('speedtest-cli', 'speedtest'),
    ('requests', 'requests'),
    ('openpyxl', 'openpyxl'),
    ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib.pyplot'),
    ('numpy', 'numpy'),
    ('python-dateutil', 'dateutil'),
    ('pytz', 'pytz'),
]

missing = []
for pip_name, import_name in dependencies:
    try:
        if '.' in import_name:
            module = __import__(import_name.split('.')[0])
        else:
            __import__(import_name)
        print(f"   ✅ {pip_name}")
    except ImportError:
        missing.append(pip_name)
        print(f"   ❌ {pip_name}")

if missing:
    print(f"\n   DÉPENDANCES MANQUANTES: {', '.join(missing)}")
    print("   Installez-les avec: pip install " + " ".join(missing))
else:
    print("\n   ✅ Toutes les dépendances sont installées")

# Vérifier les modules
print("\n2. Vérification des modules NetPing Monitor...")

modules = [
    'speedtest_ip_detector',
    'speedtest_runner',
    'speedtest_scheduler',
    'speedtest_storage',
    'speedtest_notifier',
    'speedtest_excel_exporter',
    'speedtest_manager',
    'ui_speedtest',
]

for module in modules:
    try:
        __import__(module)
        print(f"   ✅ {module}.py")
    except ImportError as e:
        print(f"   ❌ {module}.py - {e}")

# Tester l'interface
print("\n3. Test de l'interface...")
try:
    import customtkinter as ctk
    print("   ✅ CustomTkinter fonctionne")
    print(f"   Version: {ctk.__version__}")
except Exception as e:
    print(f"   ❌ CustomTkinter erreur: {e}")

# Tester SpeedTest simple
print("\n4. Test SpeedTest (version courte)...")
try:
    from speedtest_ip_detector import IPDetector
    ip_detector = IPDetector()
    ip_info = ip_detector.detect()
    if ip_info.get('success'):
        print(f"   ✅ IP détectée: {ip_info.get('ip')}")
        print(f"   ISP: {ip_info.get('isp', 'N/A')}")
        print(f"   Localisation: {ip_info.get('city', 'N/A')}, {ip_info.get('country', 'N/A')}")
    else:
        print(f"   ⚠️  IP non détectée: {ip_info.get('error')}")
except Exception as e:
    print(f"   ❌ Détection IP erreur: {e}")

# Tester le stockage
print("\n5. Test du système de stockage...")
try:
    from speedtest_storage import SpeedTestStorage
    storage = SpeedTestStorage("test_data")
    
    # Test données
    test_result = {
        'date': '2026-06-22',
        'time': '12:00:00',
        'success': True,
        'public_ip': '41.243.13.114',
        'isp': 'Orange',
        'ping': 25.5,
        'download': 120.7,
        'upload': 45.3,
        'jitter': 2.1,
        'status': 'good',
        'status_message': 'Connexion excellente'
    }
    
    storage.save_result(test_result)
    latest = storage.get_latest_result()
    
    if latest:
        print(f"   ✅ Stockage fonctionnel")
        print(f"   Données sauvegardées: Ping {latest.get('ping', 'N/A')}ms")
    else:
        print(f"   ❌ Aucune donnée sauvegardée")
    
    # Nettoyer
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
        
except Exception as e:
    print(f"   ❌ Stockage erreur: {e}")

# Interface utilisateur
print("\n6. Test de l'interface utilisateur...")
try:
    print("   Pour tester l'interface complète, exécutez:")
    print("   python ui_speedtest.py")
    print("   ou")
    print("   python main_with_speedtest.py")
except Exception as e:
    print(f"   ⚠️  Interface erreur: {e}")

# Instructions d'utilisation
print("\n" + "=" * 60)
print("INSTRUCTIONS D'UTILISATION")
print("=" * 60)
print("\n1. Interface Simple SpeedTest:")
print("   python ui_speedtest.py")
print("\n2. Version Complète NetPing Monitor:")
print("   python main_with_speedtest.py")
print("\n3. Installer les dépendances manquantes:")
print("   pip install -r requirements.txt")
print("\n4. Options de lancement:")
print("   - start_speedtest.bat (Windows)")
print("   - python start_speedtest.bat")
print("\n5. Documentation:")
print("   - Lisez README_SPEEDTEST.md pour les détails")
print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)