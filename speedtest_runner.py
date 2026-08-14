#!/usr/bin/env python3
"""
Module d'exécution SpeedTest pour NetPing Monitor
Mesure le ping, débit descendant, débit montant, jitter et perte de paquets
"""

import subprocess
import json
import re
import time
import threading
import platform
from datetime import datetime
from typing import Dict, Optional, List
from speedtest_ip_detector import IPDetector


class SpeedTestRunner:
    """Exécuteur de tests de débit réseau"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.ip_detector = IPDetector()
        self.is_running = False
        self.last_result = None
        self.lock = threading.Lock()
        
        # Configuration des seuils
        self.thresholds = {
            'ping_warning': 100,      # ms
            'ping_critical': 200,     # ms
            'download_warning': 50,   # Mbps
            'download_critical': 10,  # Mbps
            'upload_warning': 20,     # Mbps
            'upload_critical': 5,     # Mbps
        }
    
    def run_speedtest(self, server_id: Optional[int] = None) -> Dict:
        """
        Exécute un test de débit complet
        
        Args:
            server_id: ID du serveur SpeedTest (optionnel)
            
        Returns:
            Dictionnaire avec les résultats du test
        """
        with self.lock:
            if self.is_running:
                return {
                    'success': False,
                    'error': 'Un test est déjà en cours',
                    'timestamp': datetime.now().isoformat()
                }
            
            self.is_running = True
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'success': False,
            'error': None,
            
            # Informations IP
            'public_ip': None,
            'isp': None,
            'city': None,
            'country': None,
            
            # Résultats SpeedTest
            'ping': None,
            'download': None,
            'upload': None,
            'jitter': None,
            'packet_loss': None,
            
            # Serveur
            'server_name': None,
            'server_id': None,
            'server_url': None,
            
            # Statut
            'status': 'unknown',
            'status_message': None
        }
        
        try:
            # 1. Détecter l'IP publique
            ip_info = self.ip_detector.detect()
            if ip_info['success']:
                result['public_ip'] = ip_info.get('ip')
                result['isp'] = ip_info.get('isp')
                result['city'] = ip_info.get('city')
                result['country'] = ip_info.get('country')
            
            # 2. Exécuter SpeedTest CLI
            speedtest_result = self._run_speedtest_cli(server_id)
            
            if speedtest_result['success']:
                result.update({
                    'success': True,
                    'ping': speedtest_result.get('ping'),
                    'download': speedtest_result.get('download'),
                    'upload': speedtest_result.get('upload'),
                    'jitter': speedtest_result.get('jitter'),
                    'packet_loss': speedtest_result.get('packet_loss'),
                    'server_name': speedtest_result.get('server_name'),
                    'server_id': speedtest_result.get('server_id'),
                    'server_url': speedtest_result.get('server_url'),
                })
                
                # Évaluer le statut
                result['status'], result['status_message'] = self._evaluate_status(result)
            else:
                result['error'] = speedtest_result.get('error', 'Échec du SpeedTest')
                
        except Exception as e:
            result['error'] = str(e)
            result['status'] = 'error'
        
        finally:
            with self.lock:
                self.is_running = False
                self.last_result = result
        
        return result
    
    def _run_speedtest_cli(self, server_id: Optional[int] = None) -> Dict:
        """
        Exécute la commande speedtest-cli
        
        Args:
            server_id: ID du serveur optionnel
            
        Returns:
            Résultats parsés
        """
        result = {
            'success': False,
            'error': None
        }
        
        try:
            # Construire la commande
            cmd = ['speedtest', '--format=json']
            
            if server_id:
                cmd.extend(['--server-id', str(server_id)])
            
            # Exécuter la commande
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes max
                encoding='utf-8',
                errors='ignore'
            )
            
            if process.returncode == 0:
                # Parser le JSON
                data = json.loads(process.stdout)
                
                result['success'] = True
                result['ping'] = data.get('ping', {}).get('latency', 0)
                result['jitter'] = data.get('ping', {}).get('jitter', 0)
                
                # Download
                download_data = data.get('download', {})
                result['download'] = download_data.get('bandwidth', 0) / 1_000_000  # bytes to Mbps
                
                # Upload
                upload_data = data.get('upload', {})
                result['upload'] = upload_data.get('bandwidth', 0) / 1_000_000  # bytes to Mbps
                
                # Packet loss (si disponible)
                result['packet_loss'] = data.get('packetLoss', 0)
                
                # Serveur
                server = data.get('server', {})
                result['server_name'] = server.get('name')
                result['server_id'] = server.get('id')
                result['server_url'] = server.get('url')
                
            else:
                # Erreur
                error_msg = process.stderr.strip() if process.stderr else process.stdout.strip()
                result['error'] = error_msg or 'Erreur inconnue SpeedTest'
                
        except FileNotFoundError:
            result['error'] = 'SpeedTest CLI non installé. Installez avec: pip install speedtest-cli'
        except subprocess.TimeoutExpired:
            result['error'] = 'Timeout: le test a pris trop de temps'
        except json.JSONDecodeError as e:
            result['error'] = f'Erreur de parsing JSON: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _evaluate_status(self, result: Dict) -> tuple:
        """
        Évalue le statut du test basé sur les seuils
        
        Args:
            result: Résultats du test
            
        Returns:
            Tuple (statut, message)
        """
        ping = result.get('ping', 0) or 0
        download = result.get('download', 0) or 0
        upload = result.get('upload', 0) or 0
        
        issues = []
        
        # Vérifier le ping
        if ping > self.thresholds['ping_critical']:
            issues.append('ping critique')
        elif ping > self.thresholds['ping_warning']:
            issues.append('ping élevé')
        
        # Vérifier le download
        if download < self.thresholds['download_critical']:
            issues.append('download très faible')
        elif download < self.thresholds['download_warning']:
            issues.append('download faible')
        
        # Vérifier l'upload
        if upload < self.thresholds['upload_critical']:
            issues.append('upload très faible')
        elif upload < self.thresholds['upload_warning']:
            issues.append('upload faible')
        
        if len(issues) >= 2:
            return 'critical', f"Problèmes critiques: {', '.join(issues)}"
        elif len(issues) == 1:
            return 'warning', f"Performance réduite: {issues[0]}"
        else:
            return 'good', 'Connexion stable'
    
    def run_ping_test(self, host: str = '8.8.8.8', count: int = 10) -> Dict:
        """
        Exécute un test de ping simple
        
        Args:
            host: Hôte à pinguer
            count: Nombre de pings
            
        Returns:
            Résultats du ping
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'host': host,
            'success': False,
            'avg_ping': None,
            'min_ping': None,
            'max_ping': None,
            'jitter': None,
            'packet_loss': 0,
            'error': None
        }
        
        try:
            if self.system == 'windows':
                cmd = ['ping', '-n', str(count), host]
            else:
                cmd = ['ping', '-c', str(count), host]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            if process.returncode == 0:
                output = process.stdout
                
                # Parser les résultats
                if self.system == 'windows':
                    # Format Windows
                    avg_match = re.search(r'Moyenne\s*=\s*(\d+)', output)
                    min_match = re.search(r'Minimum\s*=\s*(\d+)', output)
                    max_match = re.search(r'Maximum\s*=\s*(\d+)', output)
                    loss_match = re.search(r'perdus\s*=\s*(\d+)', output)
                else:
                    # Format Linux/Mac
                    avg_match = re.search(r'rtt min/avg/max/mdev\s*=\s*[\d.]+/([\d.]+)', output)
                    min_match = re.search(r'rtt min/avg/max/mdev\s*=\s*([\d.]+)', output)
                    max_match = re.search(r'rtt min/avg/max/mdev\s*=\s*[\d.]+/[\d.]+/([\d.]+)', output)
                    loss_match = re.search(r'(\d+)%\s*packet loss', output)
                
                result['success'] = True
                
                if avg_match:
                    result['avg_ping'] = float(avg_match.group(1))
                if min_match:
                    result['min_ping'] = float(min_match.group(1))
                if max_match:
                    result['max_ping'] = float(max_match.group(1))
                
                # Calculer le jitter approximatif (différence max-min / 2)
                if result['max_ping'] and result['min_ping']:
                    result['jitter'] = (result['max_ping'] - result['min_ping']) / 2
                
                # Packet loss
                if loss_match:
                    result['packet_loss'] = float(loss_match.group(1))
            else:
                result['error'] = 'Ping échoué'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def quick_test(self) -> Dict:
        """
        Test rapide (ping uniquement)
        
        Returns:
            Résultats du test rapide
        """
        return self.run_ping_test()
    
    def set_thresholds(self, ping_warning: int = None, ping_critical: int = None,
                       download_warning: int = None, download_critical: int = None,
                       upload_warning: int = None, upload_critical: int = None):
        """
        Configure les seuils d'alerte
        
        Args:
            ping_warning: Seuil d'avertissement ping (ms)
            ping_critical: Seuil critique ping (ms)
            download_warning: Seuil d'avertissement download (Mbps)
            download_critical: Seuil critique download (Mbps)
            upload_warning: Seuil d'avertissement upload (Mbps)
            upload_critical: Seuil critique upload (Mbps)
        """
        if ping_warning is not None:
            self.thresholds['ping_warning'] = ping_warning
        if ping_critical is not None:
            self.thresholds['ping_critical'] = ping_critical
        if download_warning is not None:
            self.thresholds['download_warning'] = download_warning
        if download_critical is not None:
            self.thresholds['download_critical'] = download_critical
        if upload_warning is not None:
            self.thresholds['upload_warning'] = upload_warning
        if upload_critical is not None:
            self.thresholds['upload_critical'] = upload_critical
    
    def get_status(self) -> Dict:
        """
        Retourne le statut actuel du runner
        
        Returns:
            Informations de statut
        """
        return {
            'is_running': self.is_running,
            'last_result': self.last_result,
            'thresholds': self.thresholds.copy()
        }


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE SPEEDTEST RUNNER")
    print("=" * 60)
    
    runner = SpeedTestRunner()
    
    print("\n1. Test rapide (ping)...")
    quick_result = runner.quick_test()
    if quick_result['success']:
        print(f"   ✅ Ping moyen: {quick_result['avg_ping']:.1f} ms")
        print(f"   Min: {quick_result['min_ping']:.1f} ms, Max: {quick_result['max_ping']:.1f} ms")
        print(f"   Jitter: {quick_result['jitter']:.1f} ms")
        print(f"   Perte de paquets: {quick_result['packet_loss']:.1f}%")
    else:
        print(f"   ❌ Erreur: {quick_result['error']}")
    
    print("\n2. Test SpeedTest complet (peut prendre 30-60 secondes)...")
    print("   Exécution en cours...")
    
    result = runner.run_speedtest()
    
    if result['success']:
        print(f"\n   ✅ SpeedTest réussi!")
        print(f"   IP Publique: {result['public_ip']}")
        print(f"   ISP: {result['isp']}")
        print(f"   Localisation: {result['city']}, {result['country']}")
        print(f"   Ping: {result['ping']:.1f} ms")
        print(f"   Download: {result['download']:.2f} Mbps")
        print(f"   Upload: {result['upload']:.2f} Mbps")
        print(f"   Jitter: {result['jitter']:.1f} ms")
        print(f"   Serveur: {result['server_name']}")
        print(f"   Statut: {result['status']} - {result['status_message']}")
    else:
        print(f"\n   ❌ Erreur: {result['error']}")
        print(f"   Note: Installez speedtest-cli avec: pip install speedtest-cli")
