#!/usr/bin/env python3
"""
Module de planification des SpeedTests pour NetPing Monitor
Gère les horaires de test automatiques
"""

import json
import os
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List, Optional, Callable


class ScheduledTest:
    """Représente un test planifié"""
    
    def __init__(self, hour: int, minute: int, enabled: bool = True, daily: bool = True):
        self.hour = hour
        self.minute = minute
        self.enabled = enabled
        self.daily = daily
        self.last_run = None
        self.next_run = None
        self._calculate_next_run()
    
    def _calculate_next_run(self):
        """Calcule la prochaine exécution"""
        now = datetime.now()
        scheduled_time = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        
        # Si l'heure est déjà passée aujourd'hui, planifier pour demain
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        self.next_run = scheduled_time
    
    def mark_as_run(self):
        """Marque le test comme exécuté"""
        self.last_run = datetime.now()
        if self.daily:
            self._calculate_next_run()
    
    def is_due(self) -> bool:
        """Vérifie si le test est dû"""
        if not self.enabled:
            return False
        
        now = datetime.now()
        
        # Vérifier si c'est l'heure
        if self.next_run and now >= self.next_run:
            # Vérifier qu'on n'a pas déjà exécuté dans la dernière minute
            if self.last_run:
                time_since_last = (now - self.last_run).total_seconds()
                if time_since_last < 60:
                    return False
            return True
        
        return False
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'hour': self.hour,
            'minute': self.minute,
            'enabled': self.enabled,
            'daily': self.daily,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledTest':
        """Crée depuis un dictionnaire"""
        test = cls(
            hour=data['hour'],
            minute=data['minute'],
            enabled=data.get('enabled', True),
            daily=data.get('daily', True)
        )
        
        if data.get('last_run'):
            test.last_run = datetime.fromisoformat(data['last_run'])
        
        return test
    
    def get_time_string(self) -> str:
        """Retourne l'heure formatée"""
        return f"{self.hour:02d}:{self.minute:02d}"


class SpeedTestScheduler:
    """Gestionnaire de planification des SpeedTests"""
    
    def __init__(self, config_file: str = "speedtest_schedule.json"):
        self.config_file = config_file
        self.scheduled_tests: List[ScheduledTest] = []
        self.lock = threading.Lock()
        self.running = False
        self.scheduler_thread = None
        self.on_test_due: Optional[Callable] = None
        self.check_interval = 30  # Vérifier toutes les 30 secondes
        
        # Charger la configuration
        self.load_schedule()
    
    def add_test(self, hour: int, minute: int, enabled: bool = True, daily: bool = True) -> ScheduledTest:
        """
        Ajoute un test planifié
        
        Args:
            hour: Heure (0-23)
            minute: Minute (0-59)
            enabled: Activé ou non
            daily: Répété chaque jour
            
        Returns:
            Le test créé
        """
        with self.lock:
            # Vérifier si ce test existe déjà
            for test in self.scheduled_tests:
                if test.hour == hour and test.minute == minute:
                    # Mettre à jour
                    test.enabled = enabled
                    test.daily = daily
                    self.save_schedule()
                    return test
            
            # Créer un nouveau test
            new_test = ScheduledTest(hour, minute, enabled, daily)
            self.scheduled_tests.append(new_test)
            self.save_schedule()
            
            return new_test
    
    def remove_test(self, hour: int, minute: int) -> bool:
        """
        Supprime un test planifié
        
        Args:
            hour: Heure
            minute: Minute
            
        Returns:
            True si supprimé
        """
        with self.lock:
            for i, test in enumerate(self.scheduled_tests):
                if test.hour == hour and test.minute == minute:
                    del self.scheduled_tests[i]
                    self.save_schedule()
                    return True
            return False
    
    def update_test(self, old_hour: int, old_minute: int, 
                    new_hour: int, new_minute: int, 
                    enabled: bool = None, daily: bool = None) -> bool:
        """
        Modifie un test planifié
        
        Args:
            old_hour: Ancienne heure
            old_minute: Ancienne minute
            new_hour: Nouvelle heure
            new_minute: Nouvelle minute
            enabled: Nouvel état (optionnel)
            daily: Nouveau mode quotidien (optionnel)
            
        Returns:
            True si modifié
        """
        with self.lock:
            for test in self.scheduled_tests:
                if test.hour == old_hour and test.minute == old_minute:
                    test.hour = new_hour
                    test.minute = new_minute
                    if enabled is not None:
                        test.enabled = enabled
                    if daily is not None:
                        test.daily = daily
                    test._calculate_next_run()
                    self.save_schedule()
                    return True
            return False
    
    def toggle_test(self, hour: int, minute: int) -> bool:
        """
        Active/désactive un test
        
        Args:
            hour: Heure
            minute: Minute
            
        Returns:
            Nouvel état
        """
        with self.lock:
            for test in self.scheduled_tests:
                if test.hour == hour and test.minute == minute:
                    test.enabled = not test.enabled
                    self.save_schedule()
                    return test.enabled
        return False
    
    def get_all_tests(self) -> List[ScheduledTest]:
        """Retourne tous les tests planifiés"""
        return self.scheduled_tests.copy()
    
    def get_enabled_tests(self) -> List[ScheduledTest]:
        """Retourne les tests activés"""
        return [t for t in self.scheduled_tests if t.enabled]
    
    def get_next_test(self) -> Optional[ScheduledTest]:
        """Retourne le prochain test à exécuter"""
        enabled = self.get_enabled_tests()
        if not enabled:
            return None
        
        return min(enabled, key=lambda t: t.next_run)
    
    def get_time_until_next(self) -> Optional[timedelta]:
        """Retourne le temps jusqu'au prochain test"""
        next_test = self.get_next_test()
        if next_test and next_test.next_run:
            return next_test.next_run - datetime.now()
        return None
    
    def save_schedule(self):
        """Sauvegarde la planification"""
        try:
            data = {
                'tests': [t.to_dict() for t in self.scheduled_tests],
                'last_saved': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_schedule(self):
        """Charge la planification"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.scheduled_tests = [
                    ScheduledTest.from_dict(t) for t in data.get('tests', [])
                ]
                
                print(f"Chargé {len(self.scheduled_tests)} tests planifiés")
                return True
            return False
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def clear_all(self):
        """Efface toutes les planifications"""
        with self.lock:
            self.scheduled_tests.clear()
            self.save_schedule()
    
    def start(self, on_test_due: Callable = None):
        """
        Démarre le planificateur
        
        Args:
            on_test_due: Callback appelé quand un test est dû
        """
        if self.running:
            return
        
        self.on_test_due = on_test_due
        self.running = True
        
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        print("Planificateur SpeedTest démarré")
    
    def stop(self):
        """Arrête le planificateur"""
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        print("Planificateur SpeedTest arrêté")
    
    def _scheduler_loop(self):
        """Boucle principale du planificateur"""
        while self.running:
            try:
                now = datetime.now()
                
                with self.lock:
                    for test in self.scheduled_tests:
                        if test.is_due():
                            # Marquer comme exécuté
                            test.mark_as_run()
                            
                            # Appeler le callback
                            if self.on_test_due:
                                try:
                                    self.on_test_due(test)
                                except Exception as e:
                                    print(f"Erreur dans le callback: {e}")
                
                # Attendre avant la prochaine vérification
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Erreur dans la boucle du planificateur: {e}")
                time.sleep(10)
    
    def get_status(self) -> Dict:
        """Retourne le statut du planificateur"""
        next_test = self.get_next_test()
        time_until = self.get_time_until_next()
        
        return {
            'running': self.running,
            'total_tests': len(self.scheduled_tests),
            'enabled_tests': len(self.get_enabled_tests()),
            'next_test_time': next_test.get_time_string() if next_test else None,
            'next_test_datetime': next_test.next_run.isoformat() if next_test else None,
            'time_until_next': str(time_until).split('.')[0] if time_until else None,
        }
    
    def add_default_schedule(self):
        """Ajoute une planification par défaut"""
        default_times = [
            (8, 50),   # 08h50
            (12, 0),   # 12h00
            (17, 25),  # 17h25
            (22, 0),   # 22h00
        ]
        
        for hour, minute in default_times:
            self.add_test(hour, minute, enabled=True, daily=True)


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE SCHEDULER")
    print("=" * 60)
    
    scheduler = SpeedTestScheduler("test_schedule.json")
    
    # Ajouter des tests
    print("\n1. Ajout de tests planifiés...")
    scheduler.add_test(8, 50, enabled=True)
    scheduler.add_test(12, 0, enabled=True)
    scheduler.add_test(17, 25, enabled=True)
    scheduler.add_test(22, 0, enabled=False)  # Désactivé
    
    # Afficher les tests
    print("\n2. Tests planifiés:")
    for test in scheduler.get_all_tests():
        status = "✅" if test.enabled else "❌"
        print(f"   {status} {test.get_time_string()} - Quotidien: {test.daily}")
        print(f"      Prochaine exécution: {test.next_run}")
    
    # Statut
    print("\n3. Statut:")
    status = scheduler.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test du callback
    def test_callback(test):
        print(f"\n   ⏰ TEST DÛ! Heure: {test.get_time_string()}")
    
    print("\n4. Démarrage du planificateur (5 secondes)...")
    scheduler.start(on_test_due=test_callback)
    time.sleep(5)
    scheduler.stop()
    
    # Nettoyer
    if os.path.exists("test_schedule.json"):
        os.remove("test_schedule.json")
    
    print("\nTest terminé.")
