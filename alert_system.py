#!/usr/bin/env python3
"""
Système d'alertes pour NetPing Monitor
Gère les alertes visuelles et sonores
"""

import tkinter as tk
from tkinter import messagebox
import winsound  # Pour Windows
import platform
import threading
import time
from datetime import datetime


class AlertSystem:
    """Système de gestion des alertes"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.active_alerts = {}  # Format: {target_name: alert_data}
        self.alert_lock = threading.Lock()
        
        # Configuration des alertes
        self.config = {
            'sound_enabled': True,
            'visual_enabled': True,
            'alert_duration': 30,  # secondes
            'max_alerts_per_hour': 10,
            'alert_history': []
        }
        
    def trigger_alert(self, target_data):
        """
        Déclenche une alerte pour une cible hors ligne
        
        Args:
            target_data: Données de la cible
        """
        target_name = target_data.get('name', 'Inconnu')
        target_address = target_data.get('address', 'N/A')
        
        with self.alert_lock:
            # Vérifier si une alerte est déjà active pour cette cible
            if target_name in self.active_alerts:
                return
            
            # Créer les données d'alerte
            alert_data = {
                'target_name': target_name,
                'target_address': target_address,
                'trigger_time': datetime.now(),
                'status': 'active',
                'acknowledged': False,
                'alert_count': 1
            }
            
            self.active_alerts[target_name] = alert_data
            
            # Ajouter à l'historique
            self.config['alert_history'].append({
                **alert_data,
                'trigger_time': alert_data['trigger_time'].isoformat()
            })
            
            # Limiter la taille de l'historique
            if len(self.config['alert_history']) > 100:
                self.config['alert_history'] = self.config['alert_history'][-100:]
        
        # Déclencher les alertes
        if self.config['visual_enabled']:
            self._trigger_visual_alert(alert_data)
        
        if self.config['sound_enabled']:
            self._trigger_sound_alert()
        
        # Démarrer le timer d'expiration
        expiration_thread = threading.Thread(
            target=self._alert_expiration_timer,
            args=(target_name,),
            daemon=True
        )
        expiration_thread.start()
    
    def _trigger_visual_alert(self, alert_data):
        """
        Déclenche une alerte visuelle
        
        Args:
            alert_data: Données de l'alerte
        """
        # Cette fonction est conçue pour être appelée depuis le thread principal
        # Dans l'implémentation réelle, elle devrait utiliser tkinter.after()
        
        message = (
            f"ALERTE: {alert_data['target_name']} est hors ligne!\n\n"
            f"Adresse: {alert_data['target_address']}\n"
            f"Heure: {alert_data['trigger_time'].strftime('%H:%M:%S')}\n\n"
            f"La cible est hors ligne après 3 échecs consécutifs de ping."
        )
        
        # Note: L'affichage réel de la boîte de dialogue sera fait dans le thread principal
        print(f"[ALERTE VISUELLE] {message}")
    
    def _trigger_sound_alert(self):
        """
        Déclenche une alerte sonore
        """
        try:
            if self.system == "windows":
                # Sons Windows
                sounds = [
                    winsound.SND_ALIAS,  # Son système par défaut
                    'SystemExclamation',  # Son d'exclamation
                    'SystemHand',         # Son d'erreur critique
                    'SystemQuestion'      # Son de question
                ]
                
                for sound in sounds:
                    try:
                        winsound.PlaySound(sound, winsound.SND_ALIAS)
                        time.sleep(0.5)
                    except:
                        pass
                
                # Son personnalisé (bips)
                for _ in range(3):
                    winsound.Beep(1000, 200)  # Fréquence 1000Hz, durée 200ms
                    time.sleep(0.1)
            
            else:
                # Pour Linux/macOS, on pourrait utiliser des commandes système
                print("[ALERTE SONORE] Bip bip bip!")
                
        except Exception as e:
            print(f"Erreur lors de l'alerte sonore: {e}")
    
    def _alert_expiration_timer(self, target_name, duration=None):
        """
        Timer d'expiration d'alerte
        
        Args:
            target_name: Nom de la cible
            duration: Durée en secondes (optionnel)
        """
        if duration is None:
            duration = self.config['alert_duration']
        
        time.sleep(duration)
        
        with self.alert_lock:
            if target_name in self.active_alerts:
                alert_data = self.active_alerts[target_name]
                if not alert_data.get('acknowledged', False):
                    # Marquer comme expiré
                    alert_data['status'] = 'expired'
                    alert_data['expire_time'] = datetime.now()
                    print(f"Alerte expirée pour {target_name}")
    
    def acknowledge_alert(self, target_name):
        """
        Marque une alerte comme acquittée
        
        Args:
            target_name: Nom de la cible
        
        Returns:
            bool: Succès de l'acquittement
        """
        with self.alert_lock:
            if target_name in self.active_alerts:
                self.active_alerts[target_name]['acknowledged'] = True
                self.active_alerts[target_name]['status'] = 'acknowledged'
                self.active_alerts[target_name]['acknowledge_time'] = datetime.now()
                return True
        return False
    
    def clear_alert(self, target_name):
        """
        Supprime une alerte
        
        Args:
            target_name: Nom de la cible
        
        Returns:
            bool: Succès de la suppression
        """
        with self.alert_lock:
            if target_name in self.active_alerts:
                del self.active_alerts[target_name]
                return True
        return False
    
    def clear_all_alerts(self):
        """Efface toutes les alertes"""
        with self.alert_lock:
            self.active_alerts.clear()
        return True
    
    def get_active_alerts(self):
        """
        Récupère les alertes actives
        
        Returns:
            list: Liste des alertes actives
        """
        with self.alert_lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit=50):
        """
        Récupère l'historique des alertes
        
        Args:
            limit: Nombre maximum d'entrées à retourner
        
        Returns:
            list: Historique des alertes
        """
        return self.config['alert_history'][-limit:]
    
    def get_alert_statistics(self):
        """
        Récupère des statistiques sur les alertes
        
        Returns:
            dict: Statistiques des alertes
        """
        active_count = len(self.active_alerts)
        total_history = len(self.config['alert_history'])
        
        # Compter par statut
        acknowledged_count = sum(1 for alert in self.active_alerts.values() 
                               if alert.get('acknowledged', False))
        
        # Alertes des dernières 24h
        day_ago = datetime.now().timestamp() - 24 * 3600
        recent_alerts = [
            alert for alert in self.config['alert_history']
            if datetime.fromisoformat(alert['trigger_time']).timestamp() > day_ago
        ]
        
        return {
            'active_alerts': active_count,
            'acknowledged_alerts': acknowledged_count,
            'total_alerts_history': total_history,
            'recent_alerts_24h': len(recent_alerts),
            'sound_enabled': self.config['sound_enabled'],
            'visual_enabled': self.config['visual_enabled']
        }
    
    def update_config(self, config_updates):
        """
        Met à jour la configuration des alertes
        
        Args:
            config_updates: Dictionnaire des mises à jour
        
        Returns:
            bool: Succès de la mise à jour
        """
        for key, value in config_updates.items():
            if key in self.config:
                self.config[key] = value
        
        return True
    
    def save_config(self, filename="alert_config.json"):
        """
        Sauvegarde la configuration des alertes
        
        Args:
            filename: Nom du fichier de configuration
        
        Returns:
            bool: Succès de la sauvegarde
        """
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_config(self, filename="alert_config.json"):
        """
        Charge la configuration des alertes
        
        Args:
            filename: Nom du fichier de configuration
        
        Returns:
            bool: Succès du chargement
        """
        try:
            import json
            import os
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Fusionner avec la configuration actuelle
                for key, value in loaded_config.items():
                    if key in self.config:
                        self.config[key] = value
                
                return True
            return False
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def test_alert(self):
        """
        Teste le système d'alertes avec une cible fictive
        """
        print("Test du système d'alertes...")
        
        test_target = {
            'name': 'Serveur Test',
            'address': '192.168.1.100',
            'status': 'offline'
        }
        
        # Déclencher une alerte de test
        self.trigger_alert(test_target)
        
        print("Alerte déclenchée!")
        print(f"Alertes actives: {len(self.get_active_alerts())}")
        
        # Afficher les statistiques
        stats = self.get_alert_statistics()
        print("\nStatistiques des alertes:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Nettoyer
        time.sleep(2)
        self.clear_all_alerts()
        print("\nAlertes nettoyées.")


# Fonction utilitaire pour tester le module
if __name__ == "__main__":
    alert_system = AlertSystem()
    alert_system.test_alert()