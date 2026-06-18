#!/usr/bin/env python3
"""
Module de surveillance réseau pour NetPing Monitor
Gère les pings vers les cibles réseau
"""

import subprocess
import platform
import re
import time
from datetime import datetime
import socket


class NetworkMonitor:
    """Classe de surveillance réseau"""
    
    def __init__(self):
        self.system = platform.system().lower()
        
    def ping_target(self, address, timeout=5):
        """
        Ping une adresse et retourne le résultat
        
        Args:
            address: Adresse IP ou domaine
            timeout: Délai d'attente en secondes
        
        Returns:
            dict: Résultat du ping avec succès, temps de réponse, etc.
        """
        try:
            # Valider l'adresse
            if not address:
                return {
                    'success': False,
                    'response_time': 0,
                    'error': 'Adresse vide'
                }
            
            # Préparer la commande ping selon le système
            if self.system == "windows":
                command = ['ping', '-n', '1', '-w', str(timeout * 1000), address]
            else:  # Linux, macOS
                command = ['ping', '-c', '1', '-W', str(timeout), address]
            
            # Exécuter la commande ping
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Analyser la sortie
            if result.returncode == 0:
                # Extraire le temps de réponse
                response_time = self._extract_response_time(result.stdout)
                
                return {
                    'success': True,
                    'response_time': response_time,
                    'output': result.stdout,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response_time': 0,
                    'output': result.stdout + result.stderr,
                    'error': 'Échec du ping'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'response_time': 0,
                'output': '',
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': 0,
                'output': '',
                'error': f'Erreur: {str(e)}'
            }
    
    def _extract_response_time(self, ping_output):
        """
        Extrait le temps de réponse de la sortie ping
        
        Args:
            ping_output: Sortie texte de la commande ping
        
        Returns:
            float: Temps de réponse en millisecondes
        """
        try:
            if self.system == "windows":
                # Format Windows: Temps=10ms
                pattern = r'Temps[=:]\s*(\d+)ms'
            else:
                # Format Linux/macOS: time=10.5 ms
                pattern = r'time[=:]\s*([\d.]+)\s*ms'
            
            match = re.search(pattern, ping_output, re.IGNORECASE)
            if match:
                return float(match.group(1))
            
            # Essayer un autre pattern
            pattern2 = r'(\d+(?:\.\d+)?)\s*ms'
            match = re.search(pattern2, ping_output)
            if match:
                return float(match.group(1))
            
            return 0
            
        except (ValueError, TypeError):
            return 0
    
    def validate_address(self, address):
        """
        Valide une adresse IP ou un domaine
        
        Args:
            address: Adresse à valider
        
        Returns:
            bool: True si l'adresse semble valide
        """
        if not address or not isinstance(address, str):
            return False
        
        # Supprimer les espaces
        address = address.strip()
        
        # Vérifier si c'est une IP
        try:
            socket.inet_aton(address)
            return True
        except socket.error:
            pass
        
        # Vérifier si c'est un domaine valide (simplifié)
        # Un domaine doit avoir au moins un point et des caractères valides
        if '.' in address and len(address) > 3:
            # Vérifier les caractères valides
            valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
            if all(c in valid_chars for c in address):
                return True
        
        return False
    
    def test_connection(self):
        """
        Teste la connexion réseau en pingant un serveur connu
        
        Returns:
            dict: Résultat du test
        """
        test_servers = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "www.google.com"
        ]
        
        results = []
        for server in test_servers:
            result = self.ping_target(server, timeout=3)
            results.append({
                'server': server,
                'success': result['success'],
                'response_time': result['response_time']
            })
        
        # Déterminer si au moins un serveur répond
        successful = any(r['success'] for r in results)
        
        return {
            'overall_success': successful,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def bulk_ping(self, addresses, timeout=5):
        """
        Ping plusieurs adresses simultanément (séquentiellement)
        
        Args:
            addresses: Liste d'adresses à ping
            timeout: Timeout pour chaque ping
        
        Returns:
            dict: Résultats pour chaque adresse
        """
        results = {}
        
        for address in addresses:
            result = self.ping_target(address, timeout)
            results[address] = result
        
        return results
    
    def get_network_info(self):
        """
        Récupère des informations sur le réseau local
        
        Returns:
            dict: Informations réseau
        """
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'system': self.system,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {
                'hostname': 'Inconnu',
                'local_ip': 'Inconnu',
                'system': self.system,
                'timestamp': datetime.now().isoformat()
            }


# Fonction utilitaire pour tester le module
if __name__ == "__main__":
    monitor = NetworkMonitor()
    
    print("Test du module NetworkMonitor")
    print("=" * 40)
    
    # Tester la connexion
    print("\nTest de connexion réseau:")
    test_result = monitor.test_connection()
    print(f"Connexion globale: {'OK' if test_result['overall_success'] else 'ÉCHEC'}")
    
    for result in test_result['results']:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['server']}: {result['response_time']}ms")
    
    # Tester une adresse spécifique
    print("\nTest d'une adresse spécifique:")
    address = "8.8.8.8"
    ping_result = monitor.ping_target(address)
    
    print(f"Ping vers {address}:")
    print(f"  Succès: {ping_result['success']}")
    print(f"  Temps de réponse: {ping_result['response_time']}ms")
    
    if ping_result['error']:
        print(f"  Erreur: {ping_result['error']}")
    
    # Informations réseau
    print("\nInformations réseau:")
    network_info = monitor.get_network_info()
    for key, value in network_info.items():
        if key != 'timestamp':
            print(f"  {key}: {value}")