#!/usr/bin/env python3
"""
Module de stockage des résultats SpeedTest pour NetPing Monitor
Gère la sauvegarde et la consultation des résultats
"""

import json
import os
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional
import csv


class SpeedTestStorage:
    """Gestionnaire de stockage des résultats SpeedTest"""
    
    def __init__(self, base_dir: str = "reports/speedtests"):
        """
        Initialise le stockage
        
        Args:
            base_dir: Répertoire de base pour les rapports
        """
        self.base_dir = base_dir
        self.results_file = os.path.join(base_dir, "speedtest_results.json")
        self.lock = threading.Lock()
        
        # Créer le répertoire si nécessaire
        os.makedirs(base_dir, exist_ok=True)
        
        # Charger les résultats existants
        self.results: List[Dict] = self._load_results()
    
    def _load_results(self) -> List[Dict]:
        """Charge les résultats depuis le fichier"""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des résultats: {e}")
        
        return []
    
    def _save_results(self):
        """Sauvegarde les résultats"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def save_result(self, result: Dict) -> bool:
        """
        Sauvegarde un résultat de test
        
        Args:
            result: Résultat du test
            
        Returns:
            True si sauvegardé
        """
        with self.lock:
            # Ajouter un ID unique
            result['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Ajouter à la liste
            self.results.append(result)
            
            # Trier par date
            self.results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limiter la taille (garder 1000 derniers)
            if len(self.results) > 1000:
                self.results = self.results[:1000]
            
            # Sauvegarder
            return self._save_results()
    
    def get_all_results(self, limit: int = 100) -> List[Dict]:
        """
        Récupère tous les résultats
        
        Args:
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des résultats
        """
        return self.results[:limit]
    
    def get_results_by_date(self, date: str) -> List[Dict]:
        """
        Récupère les résultats pour une date donnée
        
        Args:
            date: Date au format YYYY-MM-DD
            
        Returns:
            Liste des résultats
        """
        return [r for r in self.results if r.get('date') == date]
    
    def get_results_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Récupère les résultats dans une plage de dates
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            
        Returns:
            Liste des résultats
        """
        return [
            r for r in self.results
            if start_date <= r.get('date', '') <= end_date
        ]
    
    def get_results_for_today(self) -> List[Dict]:
        """Récupère les résultats du jour"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_results_by_date(today)
    
    def get_results_for_yesterday(self) -> List[Dict]:
        """Récupère les résultats d'hier"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        return self.get_results_by_date(yesterday)
    
    def get_results_for_last_n_days(self, n: int = 7) -> List[Dict]:
        """
        Récupère les résultats des N derniers jours
        
        Args:
            n: Nombre de jours
            
        Returns:
            Liste des résultats
        """
        start_date = (datetime.now() - timedelta(days=n)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_results_by_date_range(start_date, today)
    
    def get_latest_result(self) -> Optional[Dict]:
        """Récupère le dernier résultat"""
        return self.results[0] if self.results else None
    
    def get_statistics(self, days: int = 7) -> Dict:
        """
        Calcule les statistiques sur les résultats
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dictionnaire des statistiques
        """
        results = self.get_results_for_last_n_days(days)
        
        if not results:
            return {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'avg_ping': None,
                'avg_download': None,
                'avg_upload': None,
                'best_download': None,
                'worst_download': None,
                'best_download_time': None,
                'worst_download_time': None,
            }
        
        # Filtrer les tests réussis
        successful = [r for r in results if r.get('success')]
        
        # Pings
        pings = [r['ping'] for r in successful if r.get('ping') is not None]
        downloads = [r['download'] for r in successful if r.get('download') is not None]
        uploads = [r['upload'] for r in successful if r.get('upload') is not None]
        
        stats = {
            'total_tests': len(results),
            'successful_tests': len(successful),
            'failed_tests': len(results) - len(successful),
            'success_rate': round(len(successful) / len(results) * 100, 1) if results else 0,
        }
        
        # Statistiques ping
        if pings:
            stats['avg_ping'] = round(sum(pings) / len(pings), 1)
            stats['min_ping'] = round(min(pings), 1)
            stats['max_ping'] = round(max(pings), 1)
        else:
            stats['avg_ping'] = None
        
        # Statistiques download
        if downloads:
            stats['avg_download'] = round(sum(downloads) / len(downloads), 2)
            stats['best_download'] = round(max(downloads), 2)
            stats['worst_download'] = round(min(downloads), 2)
            
            # Trouver les heures des meilleurs/pire tests
            for r in successful:
                if r.get('download') == max(downloads):
                    stats['best_download_time'] = r.get('time')
                if r.get('download') == min(downloads):
                    stats['worst_download_time'] = r.get('time')
        else:
            stats['avg_download'] = None
        
        # Statistiques upload
        if uploads:
            stats['avg_upload'] = round(sum(uploads) / len(uploads), 2)
            stats['best_upload'] = round(max(uploads), 2)
            stats['worst_upload'] = round(min(uploads), 2)
        else:
            stats['avg_upload'] = None
        
        # IPs uniques
        unique_ips = set(r.get('public_ip') for r in successful if r.get('public_ip'))
        stats['unique_ips'] = len(unique_ips)
        stats['ip_changes'] = len(unique_ips) - 1 if len(unique_ips) > 0 else 0
        
        return stats
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """
        Génère un résumé journalier
        
        Args:
            date: Date (par défaut aujourd'hui)
            
        Returns:
            Résumé de la journée
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        results = self.get_results_by_date(date)
        
        if not results:
            return {
                'date': date,
                'total_tests': 0,
                'message': 'Aucun test effectué ce jour'
            }
        
        successful = [r for r in results if r.get('success')]
        
        summary = {
            'date': date,
            'total_tests': len(results),
            'successful_tests': len(successful),
            'failed_tests': len(results) - len(successful),
        }
        
        if successful:
            pings = [r['ping'] for r in successful if r.get('ping') is not None]
            downloads = [r['download'] for r in successful if r.get('download') is not None]
            uploads = [r['upload'] for r in successful if r.get('upload') is not None]
            
            if pings:
                summary['avg_ping'] = round(sum(pings) / len(pings), 1)
            if downloads:
                summary['avg_download'] = round(sum(downloads) / len(downloads), 2)
                summary['max_download'] = round(max(downloads), 2)
                summary['min_download'] = round(min(downloads), 2)
            if uploads:
                summary['avg_upload'] = round(sum(uploads) / len(uploads), 2)
            
            # Premier et dernier test
            summary['first_test_time'] = successful[-1].get('time')
            summary['last_test_time'] = successful[0].get('time')
            
            # IP publique
            summary['public_ips'] = list(set(r.get('public_ip') for r in successful if r.get('public_ip')))
            summary['isp'] = successful[0].get('isp')
        
        return summary
    
    def export_to_csv(self, filename: str = None, date: str = None) -> str:
        """
        Exporte les résultats en CSV
        
        Args:
            filename: Nom du fichier (optionnel)
            date: Date spécifique (optionnel)
            
        Returns:
            Chemin du fichier créé
        """
        if date:
            results = self.get_results_by_date(date)
        else:
            results = self.results
        
        if not results:
            return None
        
        if filename is None:
            if date:
                filename = f"speedtest_{date}.csv"
            else:
                filename = f"speedtest_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.base_dir, filename)
        
        # Champs à exporter
        fields = [
            'date', 'time', 'public_ip', 'isp', 'city', 'country',
            'ping', 'download', 'upload', 'jitter', 'packet_loss',
            'server_name', 'status', 'success'
        ]
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(results)
            
            return filepath
        except Exception as e:
            print(f"Erreur lors de l'export CSV: {e}")
            return None
    
    def delete_old_results(self, days: int = 90):
        """
        Supprime les anciens résultats
        
        Args:
            days: Nombre de jours à conserver
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.lock:
            self.results = [r for r in self.results if r.get('date', '') >= cutoff_date]
            self._save_results()
    
    def clear_all(self):
        """Efface tous les résultats"""
        with self.lock:
            self.results.clear()
            self._save_results()
    
    def get_result_count(self) -> int:
        """Retourne le nombre de résultats"""
        return len(self.results)
    
    def search_results(self, query: str) -> List[Dict]:
        """
        Recherche dans les résultats
        
        Args:
            query: Terme de recherche
            
        Returns:
            Résultats correspondants
        """
        query = query.lower()
        
        return [
            r for r in self.results
            if query in str(r.get('public_ip', '')).lower()
            or query in str(r.get('isp', '')).lower()
            or query in str(r.get('server_name', '')).lower()
            or query in str(r.get('status', '')).lower()
        ]


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE STORAGE")
    print("=" * 60)
    
    storage = SpeedTestStorage("test_reports/speedtests")
    
    # Créer des résultats de test
    print("\n1. Création de résultats de test...")
    
    test_results = [
        {
            'timestamp': '2026-06-22T08:50:00',
            'date': '2026-06-22',
            'time': '08:50:00',
            'success': True,
            'public_ip': '41.243.13.114',
            'isp': 'Orange',
            'city': 'Paris',
            'country': 'France',
            'ping': 25.5,
            'download': 150.2,
            'upload': 45.8,
            'jitter': 3.2,
            'packet_loss': 0.0,
            'server_name': 'Paris Server',
            'status': 'good'
        },
        {
            'timestamp': '2026-06-22T12:00:00',
            'date': '2026-06-22',
            'time': '12:00:00',
            'success': True,
            'public_ip': '41.243.13.114',
            'isp': 'Orange',
            'city': 'Paris',
            'country': 'France',
            'ping': 35.2,
            'download': 95.5,
            'upload': 42.1,
            'jitter': 5.1,
            'packet_loss': 0.0,
            'server_name': 'Paris Server',
            'status': 'warning'
        },
        {
            'timestamp': '2026-06-22T17:25:00',
            'date': '2026-06-22',
            'time': '17:25:00',
            'success': True,
            'public_ip': '41.243.13.114',
            'isp': 'Orange',
            'city': 'Paris',
            'country': 'France',
            'ping': 28.3,
            'download': 120.8,
            'upload': 44.5,
            'jitter': 2.8,
            'packet_loss': 0.0,
            'server_name': 'Paris Server',
            'status': 'good'
        }
    ]
    
    for result in test_results:
        storage.save_result(result)
        print(f"   ✅ Sauvegardé: {result['time']}")
    
    # Récupérer les résultats du jour
    print("\n2. Résultats du jour:")
    today_results = storage.get_results_for_today()
    for r in today_results:
        print(f"   {r['time']} - Ping: {r['ping']}ms, DL: {r['download']}Mbps, UP: {r['upload']}Mbps")
    
    # Statistiques
    print("\n3. Statistiques:")
    stats = storage.get_statistics(days=7)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Résumé journalier
    print("\n4. Résumé journalier:")
    summary = storage.get_daily_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Export CSV
    print("\n5. Export CSV:")
    csv_file = storage.export_to_csv()
    if csv_file:
        print(f"   ✅ Fichier créé: {csv_file}")
    
    # Nettoyer
    import shutil
    if os.path.exists("test_reports"):
        shutil.rmtree("test_reports")
    
    print("\nTest terminé.")
