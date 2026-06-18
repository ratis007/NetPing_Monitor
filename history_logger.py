#!/usr/bin/env python3
"""
Journalisation de l'historique pour NetPing Monitor
Enregistre les pannes et les événements
"""

import json
import os
from datetime import datetime, timedelta
import csv
import threading


class HistoryLogger:
    """Gestionnaire de journalisation de l'historique"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.history_file = os.path.join(log_dir, "outage_history.json")
        self.csv_file = os.path.join(log_dir, "outage_history.csv")
        self.lock = threading.Lock()
        
        # Créer le répertoire de logs s'il n'existe pas
        os.makedirs(log_dir, exist_ok=True)
        
        # Charger l'historique existant
        self.outage_history = self._load_history()
        
    def _load_history(self):
        """
        Charge l'historique depuis le fichier
        
        Returns:
            list: Historique des pannes
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # S'assurer que c'est une liste
                if isinstance(history, list):
                    return history
                else:
                    return []
            else:
                return []
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Erreur lors du chargement de l'historique: {e}")
            return []
    
    def _save_history(self):
        """Sauvegarde l'historique dans le fichier"""
        try:
            with self.lock:
                # Trier par date (plus récent en premier)
                sorted_history = sorted(
                    self.outage_history,
                    key=lambda x: x.get('start_time', ''),
                    reverse=True
                )
                
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(sorted_history, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def log_outage(self, target_data, end_time=None):
        """
        Enregistre une panne dans l'historique
        
        Args:
            target_data: Données de la cible
            end_time: Heure de fin (optionnel, None pour panne en cours)
        
        Returns:
            bool: Succès de l'enregistrement
        """
        try:
            outage_record = {
                'target_name': target_data.get('name', 'Inconnu'),
                'target_address': target_data.get('address', 'N/A'),
                'start_time': datetime.now().isoformat(),
                'end_time': end_time.isoformat() if end_time else None,
                'status': 'ongoing' if end_time is None else 'resolved',
                'response_time_before': target_data.get('response_time', 0),
                'failures_count': target_data.get('failures', 0),
                'consecutive_failures': target_data.get('consecutive_failures', 0)
            }
            
            with self.lock:
                self.outage_history.append(outage_record)
                
                # Limiter la taille de l'historique
                if len(self.outage_history) > 1000:
                    self.outage_history = self.outage_history[-1000:]
            
            # Sauvegarder
            self._save_history()
            
            # Mettre à jour le CSV
            self._update_csv(outage_record)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la panne: {e}")
            return False
    
    def log_recovery(self, target_name, recovery_time=None):
        """
        Marque une panne comme résolue
        
        Args:
            target_name: Nom de la cible
            recovery_time: Heure de récupération (optionnel)
        
        Returns:
            bool: Succès de la mise à jour
        """
        if recovery_time is None:
            recovery_time = datetime.now()
        
        try:
            with self.lock:
                # Trouver la dernière panne non résolue pour cette cible
                for record in reversed(self.outage_history):
                    if (record['target_name'] == target_name and 
                        record['status'] == 'ongoing'):
                        record['end_time'] = recovery_time.isoformat()
                        record['status'] = 'resolved'
                        
                        # Calculer la durée
                        start_time = datetime.fromisoformat(record['start_time'])
                        duration = (recovery_time - start_time).total_seconds()
                        record['duration_seconds'] = duration
                        
                        self._save_history()
                        self._update_csv_record(record)
                        return True
            
            return False
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la récupération: {e}")
            return False
    
    def _update_csv(self, outage_record):
        """
        Met à jour le fichier CSV avec un nouvel enregistrement
        
        Args:
            outage_record: Enregistrement de panne
        """
        try:
            file_exists = os.path.exists(self.csv_file)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Écrire l'en-tête si le fichier n'existe pas
                if not file_exists:
                    headers = [
                        'target_name', 'target_address', 'start_time', 'end_time',
                        'status', 'response_time_before', 'failures_count',
                        'consecutive_failures', 'duration_seconds'
                    ]
                    writer.writerow(headers)
                
                # Calculer la durée si disponible
                duration = None
                if outage_record.get('end_time'):
                    start = datetime.fromisoformat(outage_record['start_time'])
                    end = datetime.fromisoformat(outage_record['end_time'])
                    duration = (end - start).total_seconds()
                
                # Écrire la ligne
                row = [
                    outage_record['target_name'],
                    outage_record['target_address'],
                    outage_record['start_time'],
                    outage_record.get('end_time', ''),
                    outage_record['status'],
                    outage_record.get('response_time_before', 0),
                    outage_record.get('failures_count', 0),
                    outage_record.get('consecutive_failures', 0),
                    duration if duration is not None else ''
                ]
                writer.writerow(row)
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour du CSV: {e}")
    
    def _update_csv_record(self, outage_record):
        """
        Met à jour un enregistrement existant dans le CSV
        (implémentation simplifiée - dans une vraie application,
        on devrait réécrire tout le fichier ou utiliser une base de données)
        """
        # Pour simplifier, on ajoute simplement une nouvelle ligne
        # Une implémentation complète nécessiterait de réécrire le fichier
        self._update_csv(outage_record)
    
    def get_outage_history(self, target_name=None, days=None, limit=100):
        """
        Récupère l'historique des pannes avec filtres optionnels
        
        Args:
            target_name: Filtrer par nom de cible (optionnel)
            days: Nombre de jours à considérer (optionnel)
            limit: Nombre maximum d'entrées à retourner
        
        Returns:
            list: Historique filtré des pannes
        """
        with self.lock:
            history = self.outage_history.copy()
        
        # Filtrer par nom de cible
        if target_name:
            history = [record for record in history 
                      if record['target_name'] == target_name]
        
        # Filtrer par date
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()
            
            filtered_history = []
            for record in history:
                start_time = record.get('start_time', '')
                if start_time > cutoff_iso:
                    filtered_history.append(record)
            
            history = filtered_history
        
        # Limiter le nombre de résultats
        return history[:limit]
    
    def get_outage_statistics(self, days=30):
        """
        Récupère des statistiques sur les pannes
        
        Args:
            days: Nombre de jours à considérer
        
        Returns:
            dict: Statistiques des pannes
        """
        recent_outages = self.get_outage_history(days=days)
        
        total_outages = len(recent_outages)
        ongoing_outages = sum(1 for o in recent_outages if o['status'] == 'ongoing')
        resolved_outages = sum(1 for o in recent_outages if o['status'] == 'resolved')
        
        # Calculer la durée moyenne des pannes résolues
        resolved_records = [o for o in recent_outages if o['status'] == 'resolved']
        durations = []
        
        for record in resolved_records:
            if record.get('end_time'):
                try:
                    start = datetime.fromisoformat(record['start_time'])
                    end = datetime.fromisoformat(record['end_time'])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
                except:
                    pass
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Cibles les plus problématiques
        target_counts = {}
        for record in recent_outages:
            target = record['target_name']
            target_counts[target] = target_counts.get(target, 0) + 1
        
        problematic_targets = sorted(
            target_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_outages_last_days': total_outages,
            'ongoing_outages': ongoing_outages,
            'resolved_outages': resolved_outages,
            'average_duration_seconds': round(avg_duration, 2),
            'most_problematic_targets': problematic_targets,
            'analysis_period_days': days,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_history(self, confirm=True):
        """
        Efface tout l'historique
        
        Args:
            confirm: Demander confirmation (dans l'interface utilisateur)
        
        Returns:
            bool: Succès de l'effacement
        """
        try:
            with self.lock:
                self.outage_history.clear()
                self._save_history()
                
                # Réinitialiser le CSV
                if os.path.exists(self.csv_file):
                    os.remove(self.csv_file)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'effacement de l'historique: {e}")
            return False
    
    def export_history(self, filename, format='json'):
        """
        Exporte l'historique vers un fichier
        
        Args:
            filename: Nom du fichier d'export
            format: Format d'export ('json' ou 'csv')
        
        Returns:
            bool: Succès de l'export
        """
        try:
            if format.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.outage_history, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'csv':
                # Copier le fichier CSV existant
                if os.path.exists(self.csv_file):
                    import shutil
                    shutil.copy2(self.csv_file, filename)
                else:
                    # Créer un nouveau fichier CSV
                    self._update_csv({})  # Crée juste l'en-tête
                    if os.path.exists(self.csv_file):
                        import shutil
                        shutil.copy2(self.csv_file, filename)
            
            else:
                print(f"Format non supporté: {format}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return False
    
    def get_daily_summary(self, date=None):
        """
        Récupère un résumé quotidien des pannes
        
        Args:
            date: Date spécifique (optionnel, aujourd'hui par défaut)
        
        Returns:
            dict: Résumé quotidien
        """
        if date is None:
            date = datetime.now().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        start_iso = start_of_day.isoformat()
        end_iso = end_of_day.isoformat()
        
        daily_outages = []
        with self.lock:
            for record in self.outage_history:
                record_time = record.get('start_time', '')
                if start_iso <= record_time <= end_iso:
                    daily_outages.append(record)
        
        total_outages = len(daily_outages)
        total_duration = 0
        
        for record in daily_outages:
            if record.get('end_time'):
                try:
                    start = datetime.fromisoformat(record['start_time'])
                    end = datetime.fromisoformat(record['end_time'])
                    duration = (end - start).total_seconds()
                    total_duration += duration
                except:
                    pass
        
        return {
            'date': date.isoformat(),
            'total_outages': total_outages,
            'total_duration_seconds': total_duration,
            'outages_by_target': len(set(r['target_name'] for r in daily_outages)),
            'outage_records': daily_outages
        }


# Fonction utilitaire pour tester le module
if __name__ == "__main__":
    logger = HistoryLogger("test_logs")
    
    print("Test du module HistoryLogger")
    print("=" * 40)
    
    # Enregistrer quelques pannes de test
    test_targets = [
        {
            'name': 'Serveur Web',
            'address': '192.168.1.10',
            'response_time': 15,
            'failures': 3,
            'consecutive_failures': 3
        },
        {
            'name': 'Base de données',
            'address': '192.168.1.20',
            'response_time': 8,
            'failures': 5,
            'consecutive_failures': 5
        }
    ]
    
    for target in test_targets:
        logger.log_outage(target)
        print(f"✅ Panne enregistrée pour {target['name']}")
    
    # Marquer une panne comme résolue
    logger.log_recovery('Serveur Web')
    print("✅ Récupération enregistrée pour Serveur Web")
    
    # Afficher l'historique
    print("\nHistorique des pannes:")
    history = logger.get_outage_history()
    for record in history:
        print(f"  {record['target_name']}: {record['status']} à {record['start_time']}")
    
    # Afficher les statistiques
    print("\nStatistiques des pannes:")
    stats = logger.get_outage_statistics(days=7)
    for key, value in stats.items():
        if key != 'most_problematic_targets':
            print(f"  {key}: {value}")
    
    print("\nCibles les plus problématiques:")
    for target, count in stats.get('most_problematic_targets', []):
        print(f"  {target}: {count} pannes")
    
    # Nettoyer
    import shutil
    if os.path.exists("test_logs"):
        shutil.rmtree("test_logs")