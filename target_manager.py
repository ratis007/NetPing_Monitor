#!/usr/bin/env python3
"""
Gestionnaire de cibles pour NetPing Monitor
Gère l'ajout, la suppression et la persistance des cibles
"""

import json
import os
from datetime import datetime
import threading


class TargetManager:
    """Gère les cibles à surveiller"""
    
    def __init__(self, config_file="targets.json"):
        self.config_file = config_file
        self.targets = {}  # Format: {name: target_data}
        self.lock = threading.Lock()
        
    def add_target(self, target_data):
        """
        Ajoute une nouvelle cible
        
        Args:
            target_data: Dictionnaire contenant les données de la cible
        """
        name = target_data.get('name')
        if not name:
            raise ValueError("Le nom de la cible est requis")
        
        with self.lock:
            # Initialiser les données par défaut
            default_target = {
                'address': '',
                'interval': 30,  # secondes
                'status': 'unknown',
                'response_time': 0,
                'last_check': '',
                'last_check_timestamp': 0,
                'failures': 0,
                'consecutive_failures': 0,
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            
            # Fusionner avec les données fournies
            target = {**default_target, **target_data}
            
            # Validation
            if not target['address']:
                raise ValueError("L'adresse de la cible est requise")
            
            if target['interval'] < 5:
                raise ValueError("L'intervalle minimum est de 5 secondes")
            
            # Ajouter à la collection
            self.targets[name] = target
            
            # Sauvegarder
            self.save_targets()
            
        return True
    
    def remove_target(self, target_name):
        """
        Supprime une cible
        
        Args:
            target_name: Nom de la cible à supprimer
        """
        with self.lock:
            if target_name in self.targets:
                del self.targets[target_name]
                self.save_targets()
                return True
            return False
    
    def update_target(self, target_name, updates):
        """
        Met à jour une cible existante
        
        Args:
            target_name: Nom de la cible
            updates: Dictionnaire des mises à jour
        """
        with self.lock:
            if target_name not in self.targets:
                return False
            
            target = self.targets[target_name]
            
            # Mettre à jour les champs
            for key, value in updates.items():
                if key in target and key not in ['created_at']:
                    target[key] = value
            
            target['last_modified'] = datetime.now().isoformat()
            self.save_targets()
            
        return True
    
    def update_interval(self, target_name, new_interval):
        """
        Met à jour l'intervalle de vérification d'une cible
        
        Args:
            target_name: Nom de la cible
            new_interval: Nouvel intervalle en secondes
        """
        if new_interval < 5:
            raise ValueError("L'intervalle minimum est de 5 secondes")
        
        return self.update_target(target_name, {'interval': new_interval})
    
    def update_status(self, target_name, status, response_time=0):
        """
        Met à jour le statut d'une cible après un ping
        
        Args:
            target_name: Nom de la cible
            status: Nouveau statut ('online', 'offline', 'unknown')
            response_time: Temps de réponse en ms
        """
        updates = {
            'status': status,
            'response_time': response_time,
            'last_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_check_timestamp': datetime.now().timestamp()
        }
        
        if status == 'online':
            updates['consecutive_failures'] = 0
        elif status == 'offline':
            updates['failures'] = self.targets.get(target_name, {}).get('failures', 0) + 1
            updates['consecutive_failures'] = self.targets.get(target_name, {}).get('consecutive_failures', 0) + 1
        
        return self.update_target(target_name, updates)
    
    def get_target(self, target_name):
        """
        Récupère une cible par son nom
        
        Args:
            target_name: Nom de la cible
        
        Returns:
            dict: Données de la cible ou None
        """
        return self.targets.get(target_name)
    
    def get_all_targets(self):
        """
        Récupère toutes les cibles
        
        Returns:
            list: Liste de toutes les cibles
        """
        return list(self.targets.values())
    
    def get_targets_by_status(self, status):
        """
        Récupère les cibles par statut
        
        Args:
            status: Statut à filtrer ('online', 'offline', 'unknown')
        
        Returns:
            list: Cibles avec le statut spécifié
        """
        return [
            target for target in self.targets.values()
            if target.get('status') == status
        ]
    
    def get_statistics(self):
        """
        Récupère des statistiques sur les cibles
        
        Returns:
            dict: Statistiques
        """
        total = len(self.targets)
        online = len(self.get_targets_by_status('online'))
        offline = len(self.get_targets_by_status('offline'))
        unknown = len(self.get_targets_by_status('unknown'))
        
        # Temps de réponse moyen
        response_times = [
            t['response_time'] for t in self.targets.values()
            if t.get('response_time', 0) > 0
        ]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        # Total des échecs
        total_failures = sum(t.get('failures', 0) for t in self.targets.values())
        
        return {
            'total_targets': total,
            'online': online,
            'offline': offline,
            'unknown': unknown,
            'avg_response_time': round(avg_response, 2),
            'total_failures': total_failures,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_targets(self):
        """Sauvegarde les cibles dans un fichier JSON"""
        try:
            with self.lock:
                data = {
                    'targets': self.targets,
                    'last_saved': datetime.now().isoformat(),
                    'version': '1.0'
                }
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_targets(self):
        """Charge les cibles depuis le fichier JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                with self.lock:
                    self.targets = data.get('targets', {})
                
                print(f"Chargé {len(self.targets)} cibles depuis {self.config_file}")
                return True
            else:
                print(f"Fichier {self.config_file} non trouvé, création d'une nouvelle configuration")
                self.targets = {}
                return True
                
        except json.JSONDecodeError:
            print(f"Fichier {self.config_file} corrompu, création d'une nouvelle configuration")
            self.targets = {}
            return False
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            self.targets = {}
            return False
    
    def export_targets(self, filename):
        """
        Exporte les cibles vers un fichier
        
        Args:
            filename: Nom du fichier d'export
        
        Returns:
            bool: Succès de l'export
        """
        try:
            data = {
                'targets': self.targets,
                'export_date': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return False
    
    def import_targets(self, filename):
        """
        Importe des cibles depuis un fichier
        
        Args:
            filename: Nom du fichier à importer
        
        Returns:
            bool: Succès de l'import
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_targets = data.get('targets', {})
            
            with self.lock:
                # Fusionner avec les cibles existantes
                for name, target in imported_targets.items():
                    if name not in self.targets:
                        self.targets[name] = target
            
            self.save_targets()
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            return False
    
    def clear_all_targets(self):
        """Efface toutes les cibles"""
        with self.lock:
            self.targets.clear()
            self.save_targets()
        
        return True


# Fonction utilitaire pour tester le module
if __name__ == "__main__":
    manager = TargetManager("test_targets.json")
    
    print("Test du module TargetManager")
    print("=" * 40)
    
    # Ajouter quelques cibles de test
    test_targets = [
        {
            'name': 'Google DNS',
            'address': '8.8.8.8',
            'interval': 30
        },
        {
            'name': 'Cloudflare DNS',
            'address': '1.1.1.1',
            'interval': 45
        },
        {
            'name': 'Serveur Local',
            'address': '192.168.1.1',
            'interval': 60
        }
    ]
    
    for target in test_targets:
        try:
            manager.add_target(target)
            print(f"✅ Ajouté: {target['name']}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")
    
    # Afficher les statistiques
    print("\nStatistiques:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")
    
    # Afficher toutes les cibles
    print("\nCibles actuelles:")
    for name, target in manager.targets.items():
        print(f"  {name}: {target['address']} (intervalle: {target['interval']}s)")
    
    # Nettoyer
    manager.clear_all_targets()
    if os.path.exists("test_targets.json"):
        os.remove("test_targets.json")