#!/usr/bin/env python3
"""
Manager principal du module SpeedTest pour NetPing Monitor
Orchestre tous les composants SpeedTest
"""

from speedtest_ip_detector import IPDetector
from speedtest_runner import SpeedTestRunner
from speedtest_scheduler import SpeedTestScheduler
from speedtest_storage import SpeedTestStorage
from speedtest_notifier import SpeedTestNotifier
from speedtest_excel_exporter import SpeedTestExcelExporter
from datetime import datetime
from typing import Dict, List, Optional, Callable
import threading
import os


class SpeedTestManager:
    """Manager principal du module SpeedTest"""
    
    def __init__(self, base_dir: str = "reports/speedtests"):
        """
        Initialise le manager SpeedTest
        
        Args:
            base_dir: Répertoire de base pour les rapports
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        # Initialisation des modules
        self.ip_detector = IPDetector()
        self.runner = SpeedTestRunner()
        self.storage = SpeedTestStorage(base_dir)
        self.scheduler = SpeedTestScheduler()
        self.notifier = SpeedTestNotifier()
        self.exporter = SpeedTestExcelExporter(base_dir)
        
        # État
        self.running = False
        self.on_test_complete: Optional[Callable] = None
        self.on_alert_sent: Optional[Callable] = None
        
        # Configurer le notifier
        self.notifier.on_alert_sent = self._on_alert_sent
        
        # Configurer le scheduler
        self.scheduler.on_test_due = self._on_scheduled_test
        
        # Configuration par défaut
        self._setup_default_schedule()
    
    def _setup_default_schedule(self):
        """Configure une planification par défaut"""
        # Horaires recommandés pour supervision réseau
        default_times = [
            (8, 50),   # Début journée
            (12, 0),   # Mi-journée
            (17, 25),  # Fin journée
            (22, 0),   # Soirée
        ]
        
        for hour, minute in default_times:
            self.scheduler.add_test(hour, minute, enabled=True, daily=True)
    
    def start(self):
        """Démarre le module SpeedTest"""
        if self.running:
            return
        
        self.running = True
        
        # Démarrer le planificateur
        self.scheduler.start()
        
        # Détecter IP initiale
        ip_info = self.ip_detector.detect()
        if ip_info['success']:
            self.notifier.previous_ip = ip_info.get('ip')
        
        print("Module SpeedTest démarré")
    
    def stop(self):
        """Arrête le module SpeedTest"""
        if not self.running:
            return
        
        self.running = False
        self.scheduler.stop()
        
        print("Module SpeedTest arrêté")
    
    def run_manual_test(self, server_id: Optional[int] = None) -> Dict:
        """
        Exécute un test manuel
        
        Args:
            server_id: ID du serveur SpeedTest (optionnel)
            
        Returns:
            Résultat du test
        """
        result = self.runner.run_speedtest(server_id)
        
        # Sauvegarder
        self.storage.save_result(result)
        
        # Notifier si nécessaire
        alerts = self.notifier.check_and_notify(result)
        
        # Appeler le callback
        if self.on_test_complete:
            self.on_test_complete(result, alerts)
        
        return result
    
    def run_quick_test(self) -> Dict:
        """
        Exécute un test rapide (ping uniquement)
        
        Returns:
            Résultat du test rapide
        """
        return self.runner.quick_test()
    
    def _on_scheduled_test(self, scheduled_test):
        """Appelé quand un test planifié est dû"""
        print(f"⏰ Test planifié exécuté: {scheduled_test.get_time_string()}")
        self.run_manual_test()
    
    def _on_alert_sent(self, alert_type: str, result: Dict):
        """Appelé quand une alerte est envoyée"""
        if self.on_alert_sent:
            self.on_alert_sent(alert_type, result)
    
    def get_current_status(self) -> Dict:
        """
        Retourne le statut actuel
        
        Returns:
            Dictionnaire de statut
        """
        latest = self.storage.get_latest_result()
        stats = self.storage.get_statistics(days=1)
        scheduler_status = self.scheduler.get_status()
        
        return {
            'running': self.running,
            'latest_result': latest,
            'daily_stats': stats,
            'scheduler': scheduler_status,
            'next_test': scheduler_status.get('next_test_time'),
            'time_until_next': scheduler_status.get('time_until_next'),
        }
    
    def get_daily_results(self) -> List[Dict]:
        """Récupère les résultats du jour"""
        return self.storage.get_results_for_today()
    
    def get_historical_results(self, days: int = 7) -> List[Dict]:
        """
        Récupère les résultats historiques
        
        Args:
            days: Nombre de jours
            
        Returns:
            Liste des résultats
        """
        return self.storage.get_results_for_last_n_days(days)
    
    def export_daily_report(self) -> Optional[str]:
        """
        Exporte un rapport journalier Excel
        
        Returns:
            Chemin du fichier créé
        """
        results = self.get_daily_results()
        
        if not results:
            return None
        
        date = datetime.now().strftime('%Y-%m-%d')
        return self.exporter.generate_daily_report(results, date)
    
    def export_custom_report(self, start_date: str, end_date: str, title: str = "Rapport SpeedTest") -> Optional[str]:
        """
        Exporte un rapport personnalisé
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            title: Titre du rapport
            
        Returns:
            Chemin du fichier créé
        """
        results = self.storage.get_results_by_date_range(start_date, end_date)
        
        if not results:
            return None
        
        return self.exporter.generate_custom_report(results, title, start_date, end_date)
    
    def configure_notifications(self, email_config: Dict = None, whatsapp_config: Dict = None):
        """
        Configure les notifications
        
        Args:
            email_config: Configuration email
            whatsapp_config: Configuration WhatsApp
        """
        if email_config:
            self.notifier.configure_email(**email_config)
        
        if whatsapp_config:
            self.notifier.configure_whatsapp(**whatsapp_config)
    
    def update_thresholds(self, **thresholds):
        """
        Met à jour les seuils d'alerte
        
        Args:
            **thresholds: Seuils à mettre à jour
        """
        self.notifier.update_thresholds(**thresholds)
        self.runner.set_thresholds(**thresholds)
    
    def get_schedule(self) -> List[Dict]:
        """Récupère la planification actuelle"""
        return [t.to_dict() for t in self.scheduler.get_all_tests()]
    
    def update_schedule(self, schedule_data: List[Dict]):
        """
        Met à jour la planification
        
        Args:
            schedule_data: Nouvelle planification
        """
        self.scheduler.clear_all()
        
        for test_data in schedule_data:
            self.scheduler.add_test(
                hour=test_data['hour'],
                minute=test_data['minute'],
                enabled=test_data.get('enabled', True),
                daily=test_data.get('daily', True)
            )
    
    def check_ip_change(self) -> bool:
        """Vérifie si l'IP a changé"""
        if not self.notifier.previous_ip:
            return False
        
        current_ip = self.ip_detector.get_ip_only()
        return current_ip and current_ip != self.notifier.previous_ip
    
    def generate_statistics(self, days: int = 30) -> Dict:
        """
        Génère des statistiques
        
        Args:
            days: Nombre de jours
            
        Returns:
            Statistiques
        """
        return self.storage.get_statistics(days)


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE SPEEDTEST MANAGER")
    print("=" * 60)
    
    manager = SpeedTestManager("test_reports/speedtests")
    
    print("\n1. Démarrage du module...")
    manager.start()
    
    print("\n2. Statut actuel:")
    status = manager.get_current_status()
    for key, value in status.items():
        if key != 'latest_result':
            print(f"   {key}: {value}")
    
    print("\n3. Planification actuelle:")
    schedule = manager.get_schedule()
    for test in schedule:
        print(f"   {test['hour']:02d}:{test['minute']:02d} - Activé: {test['enabled']}")
    
    print("\n4. Test manuel (peut prendre 30-60 secondes)...")
    print("   Exécution en cours...")
    
    result = manager.run_manual_test()
    
    if result.get('success'):
        print(f"   ✅ Test réussi!")
        print(f"   Ping: {result['ping']:.1f} ms")
        print(f"   Download: {result['download']:.2f} Mbps")
        print(f"   Upload: {result['upload']:.2f} Mbps")
    else:
        print(f"   ❌ Échec: {result.get('error')}")
    
    print("\n5. Résultats du jour:")
    results = manager.get_daily_results()
    print(f"   Tests effectués: {len(results)}")
    
    print("\n6. Export Excel...")
    report_path = manager.export_daily_report()
    if report_path:
        print(f"   ✅ Rapport créé: {report_path}")
    else:
        print("   ❌ Pas de données à exporter")
    
    print("\n7. Arrêt du module...")
    manager.stop()
    
    # Nettoyer
    import shutil
    if os.path.exists("test_reports"):
        shutil.rmtree("test_reports")
    
    print("\nTest terminé.")
