#!/usr/bin/env python3
"""
Module de détection IP publique pour NetPing Monitor
Récupère l'IP publique, l'ISP et la localisation
"""

import requests
from datetime import datetime
import threading
from typing import Optional, Dict


class IPDetector:
    """Détecteur d'IP publique avec informations de localisation"""
    
    # Services de détection IP (redondance pour fiabilité)
    IP_SERVICES = [
        {
            'url': 'https://ipapi.co/json/',
            'parser': lambda data: {
                'ip': data.get('ip'),
                'isp': data.get('org'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone'),
            }
        },
        {
            'url': 'http://ip-api.com/json/',
            'parser': lambda data: {
                'ip': data.get('query'),
                'isp': data.get('isp'),
                'city': data.get('city'),
                'region': data.get('regionName'),
                'country': data.get('country'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'timezone': data.get('timezone'),
            }
        },
        {
            'url': 'https://ipwhois.app/json/',
            'parser': lambda data: {
                'ip': data.get('ip'),
                'isp': data.get('isp'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'timezone': data.get('timezone'),
            }
        }
    ]
    
    def __init__(self, timeout: int = 10):
        """
        Initialise le détecteur IP
        
        Args:
            timeout: Délai d'attente maximum en secondes
        """
        self.timeout = timeout
        self.last_detection = None
        self.cache_duration = 300  # Cache de 5 minutes
        self.last_cache_time = 0
        self.lock = threading.Lock()
    
    def detect(self, use_cache: bool = True) -> Dict:
        """
        Détecte l'IP publique et les informations associées
        
        Args:
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Dictionnaire avec les informations IP
        """
        with self.lock:
            # Vérifier le cache
            if use_cache and self.last_detection:
                elapsed = datetime.now().timestamp() - self.last_cache_time
                if elapsed < self.cache_duration:
                    return self.last_detection
        
        result = {
            'ip': None,
            'isp': None,
            'city': None,
            'region': None,
            'country': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'detection_time': datetime.now().isoformat(),
            'success': False,
            'error': None
        }
        
        # Essayer chaque service jusqu'à succès
        for service in self.IP_SERVICES:
            try:
                response = requests.get(
                    service['url'], 
                    timeout=self.timeout,
                    headers={'User-Agent': 'NetPing-Monitor/1.0'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    parsed = service['parser'](data)
                    
                    # Mettre à jour le résultat
                    result.update(parsed)
                    result['success'] = True
                    result['error'] = None
                    
                    # Mettre en cache
                    with self.lock:
                        self.last_detection = result.copy()
                        self.last_cache_time = datetime.now().timestamp()
                    
                    return result
                    
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.RequestException as e:
                continue
            except Exception as e:
                result['error'] = str(e)
                continue
        
        # Tous les services ont échoué
        result['error'] = "Impossible de détecter l'IP publique - tous les services sont indisponibles"
        return result
    
    def get_ip_only(self) -> Optional[str]:
        """
        Récupère uniquement l'IP publique (rapide)
        
        Returns:
            Adresse IP ou None
        """
        try:
            # Services rapides pour IP uniquement
            fast_services = [
                'https://api.ipify.org?format=json',
                'https://api.ip.sb/ip',
                'https://ifconfig.me/ip'
            ]
            
            for service in fast_services:
                try:
                    response = requests.get(service, timeout=self.timeout)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if ip and len(ip.split('.')) == 4:
                            return ip
                except:
                    continue
                    
        except Exception:
            pass
        
        return None
    
    def has_ip_changed(self, previous_ip: str) -> bool:
        """
        Vérifie si l'IP a changé
        
        Args:
            previous_ip: IP précédente à comparer
            
        Returns:
            True si l'IP a changé
        """
        current = self.detect()
        if current['success']:
            return current['ip'] != previous_ip
        return False
    
    def get_location_string(self) -> str:
        """
        Retourne une chaîne formatée de la localisation
        
        Returns:
            Chaîne formatée (ex: "Paris, France - Orange")
        """
        info = self.detect()
        
        if not info['success']:
            return "Localisation inconnue"
        
        parts = []
        
        if info.get('city'):
            parts.append(info['city'])
        elif info.get('region'):
            parts.append(info['region'])
            
        if info.get('country'):
            parts.append(info['country'])
        
        location = ', '.join(parts) if parts else "Localisation inconnue"
        
        if info.get('isp'):
            location += f" - {info['isp']}"
        
        return location
    
    def clear_cache(self):
        """Efface le cache"""
        with self.lock:
            self.last_detection = None
            self.last_cache_time = 0


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE IP DETECTOR")
    print("=" * 60)
    
    detector = IPDetector()
    
    print("\nDétection de l'IP publique...")
    result = detector.detect()
    
    if result['success']:
        print(f"\n✅ Détection réussie!")
        print(f"   IP Publique: {result['ip']}")
        print(f"   ISP: {result['isp']}")
        print(f"   Ville: {result['city']}")
        print(f"   Région: {result['region']}")
        print(f"   Pays: {result['country']}")
        print(f"   Coordonnées: {result['latitude']}, {result['longitude']}")
        print(f"   Heure de détection: {result['detection_time']}")
    else:
        print(f"\n❌ Échec de la détection: {result['error']}")
    
    print("\nTest IP rapide...")
    ip = detector.get_ip_only()
    print(f"   IP: {ip}")
    
    print("\nLocalisation formatée:")
    print(f"   {detector.get_location_string()}")
