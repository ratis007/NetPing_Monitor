#!/usr/bin/env python3
"""
NetPing Monitor - Application de surveillance réseau
Interface principale de l'application
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime
import json
import os
import sys

# Import des modules locaux
from network_monitor import NetworkMonitor
from target_manager import TargetManager
from alert_system import AlertSystem
from history_logger import HistoryLogger


class NetPingMonitor:
    """Classe principale de l'application NetPing Monitor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NetPing Monitor v1.0")
        self.root.geometry("1000x700")
        
        # Configuration de l'icône (si disponible)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Initialisation des composants
        self.monitor = NetworkMonitor()
        self.target_manager = TargetManager()
        self.alert_system = AlertSystem()
        self.history_logger = HistoryLogger()
        
        # Variables d'état
        self.monitoring_active = False
        self.monitoring_thread = None
        self.update_interval = 1000  # ms pour l'interface
        
        # Charger les cibles sauvegardées
        self.target_manager.load_targets()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer la mise à jour périodique
        self.update_display()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurer le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Titre
        title_label = ttk.Label(
            main_frame, 
            text="🔍 NetPing Monitor - Surveillance Réseau",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Section d'ajout de cible
        add_frame = ttk.LabelFrame(main_frame, text="Ajouter une cible", padding="10")
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        ttk.Label(add_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.name_entry = ttk.Entry(add_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(add_frame, text="Adresse:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.address_entry = ttk.Entry(add_frame, width=25)
        self.address_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(add_frame, text="Intervalle (s):").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.interval_entry = ttk.Entry(add_frame, width=10)
        self.interval_entry.insert(0, "30")
        self.interval_entry.grid(row=0, column=5, sticky=tk.W)
        
        add_button = ttk.Button(
            add_frame, 
            text="Ajouter", 
            command=self.add_target,
            width=15
        )
        add_button.grid(row=0, column=6, padx=(10, 0))
        
        # Boutons de contrôle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(
            control_frame,
            text="▶ Démarrer la surveillance",
            command=self.start_monitoring,
            width=20
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Arrêter la surveillance",
            command=self.stop_monitoring,
            width=20,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        clear_button = ttk.Button(
            control_frame,
            text="🗑 Effacer l'historique",
            command=self.clear_history,
            width=20
        )
        clear_button.grid(row=0, column=2)
        
        # Tableau des cibles
        table_frame = ttk.LabelFrame(main_frame, text="Cibles surveillées", padding="10")
        table_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Créer le Treeview
        columns = ("name", "address", "status", "response_time", "last_check", "failures")
        self.target_tree = ttk.Treeview(
            table_frame, 
            columns=columns,
            show="headings",
            height=15
        )
        
        # Définir les en-têtes
        headers = [
            ("Nom", 150),
            ("Adresse", 150),
            ("Statut", 100),
            ("Temps (ms)", 100),
            ("Dernier contrôle", 180),
            ("Échecs", 80)
        ]
        
        for i, (header, width) in enumerate(headers):
            self.target_tree.heading(columns[i], text=header)
            self.target_tree.column(columns[i], width=width)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=scrollbar.set)
        
        self.target_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Boutons pour les cibles
        target_buttons_frame = ttk.Frame(table_frame)
        target_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        remove_button = ttk.Button(
            target_buttons_frame,
            text="Supprimer la cible sélectionnée",
            command=self.remove_selected_target,
            width=25
        )
        remove_button.grid(row=0, column=0, padx=(0, 10))
        
        edit_button = ttk.Button(
            target_buttons_frame,
            text="Modifier l'intervalle",
            command=self.edit_interval,
            width=25
        )
        edit_button.grid(row=0, column=1)
        
        # Console de log
        log_frame = ttk.LabelFrame(main_frame, text="Journal des événements", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Statut en bas
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Prêt",
            font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.stats_label = ttk.Label(
            status_frame,
            text="Cibles: 0 | En ligne: 0 | Hors ligne: 0",
            font=("Arial", 10)
        )
        self.stats_label.grid(row=0, column=1, sticky=tk.E)
        
    def add_target(self):
        """Ajoute une nouvelle cible à surveiller"""
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        interval = self.interval_entry.get().strip()
        
        if not name or not address:
            messagebox.showwarning("Champs requis", "Veuillez remplir le nom et l'adresse")
            return
        
        try:
            interval = int(interval)
            if interval < 5:
                messagebox.showwarning("Intervalle trop court", "L'intervalle minimum est de 5 secondes")
                return
        except ValueError:
            messagebox.showwarning("Intervalle invalide", "L'intervalle doit être un nombre")
            return
        
        # Ajouter la cible
        target = {
            'name': name,
            'address': address,
            'interval': interval,
            'status': 'unknown',
            'response_time': 0,
            'last_check': '',
            'last_check_timestamp': 0,
            'failures': 0,
            'consecutive_failures': 0
        }
        
        self.target_manager.add_target(target)
        self.log_event(f"Cible ajoutée: {name} ({address})")
        
        # Effacer les champs
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        
        # Mettre à jour l'affichage
        self.update_target_display()
        
    def remove_selected_target(self):
        """Supprime la cible sélectionnée"""
        selection = self.target_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une cible")
            return
        
        item = self.target_tree.item(selection[0])
        target_name = item['values'][0]
        
        if messagebox.askyesno("Confirmation", f"Supprimer la cible '{target_name}' ?"):
            self.target_manager.remove_target(target_name)
            self.log_event(f"Cible supprimée: {target_name}")
            self.update_target_display()
    
    def edit_interval(self):
        """Modifie l'intervalle de la cible sélectionnée"""
        selection = self.target_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une cible")
            return
        
        item = self.target_tree.item(selection[0])
        target_name = item['values'][0]
        
        new_interval = simpledialog.askinteger(
            "Modifier l'intervalle",
            f"Nouvel intervalle pour {target_name} (secondes):",
            minvalue=5,
            initialvalue=30
        )
        
        if new_interval:
            self.target_manager.update_interval(target_name, new_interval)
            self.log_event(f"Intervalle modifié pour {target_name}: {new_interval}s")
            self.update_target_display()
    
    def start_monitoring(self):
        """Démarre la surveillance automatique"""
        if not self.target_manager.targets:
            messagebox.showwarning("Aucune cible", "Ajoutez d'abord des cibles à surveiller")
            return
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Démarrer le thread de surveillance
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.log_event("Surveillance démarrée")
        self.status_label.config(text="Surveillance active", foreground="green")
    
    def stop_monitoring(self):
        """Arrête la surveillance automatique"""
        self.monitoring_active = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)
        
        self.log_event("Surveillance arrêtée")
        self.status_label.config(text="Surveillance arrêtée", foreground="red")
    
    def monitoring_loop(self):
        """Boucle principale de surveillance"""
        while self.monitoring_active:
            targets = self.target_manager.targets.copy()
            
            for target_name, target in targets.items():
                if not self.monitoring_active:
                    break
                
                # Vérifier si c'est le moment de ping cette cible
                current_time = time.time()
                last_check = target.get('last_check_timestamp', 0)
                
                if current_time - last_check >= target['interval']:
                    # Effectuer le ping
                    result = self.monitor.ping_target(target['address'])
                    
                    # Mettre à jour la cible
                    if result['success']:
                        target['status'] = 'online'
                        target['response_time'] = result['response_time']
                        target['consecutive_failures'] = 0
                    else:
                        target['failures'] += 1
                        target['consecutive_failures'] += 1
                        
                        if target['consecutive_failures'] >= 3:
                            target['status'] = 'offline'
                            # Déclencher une alerte si c'est le 3ème échec consécutif
                            if target['consecutive_failures'] == 3:
                                self.trigger_alert(target)
                    
                    target['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    target['last_check_timestamp'] = current_time
                    
                    # Enregistrer dans l'historique si hors ligne
                    if target['status'] == 'offline':
                        self.history_logger.log_outage(target)
            
            # Pause avant la prochaine itération
            time.sleep(1)
    
    def trigger_alert(self, target):
        """Déclenche une alerte pour une cible hors ligne"""
        self.alert_system.trigger_alert(target)
        self.log_event(f"ALERTE: {target['name']} est hors ligne!")
        
        # Mettre à jour l'interface dans le thread principal
        self.root.after(0, lambda: self.flash_alert(target['name']))
    
    def flash_alert(self, target_name):
        """Fait clignoter l'interface pour alerter l'utilisateur"""
        # Cette méthode est appelée dans le thread principal
        messagebox.showwarning(
            "Alerte de panne",
            f"La cible '{target_name}' est hors ligne après 3 échecs consécutifs!"
        )
    
    def update_display(self):
        """Met à jour périodiquement l'affichage"""
        if self.monitoring_active:
            self.update_target_display()
        
        # Planifier la prochaine mise à jour
        self.root.after(self.update_interval, self.update_display)
    
    def update_target_display(self):
        """Met à jour l'affichage des cibles dans le tableau"""
        # Effacer l'ancien contenu
        for item in self.target_tree.get_children():
            self.target_tree.delete(item)
        
        # Ajouter les cibles actuelles
        online_count = 0
        offline_count = 0
        
        for target_name, target in self.target_manager.targets.items():
            status = target['status']
            status_display = "🟢 En ligne" if status == 'online' else "🔴 Hors ligne" if status == 'offline' else "⚪ Inconnu"
            
            response_time = f"{target['response_time']} ms" if target['response_time'] > 0 else "-"
            
            values = (
                target_name,
                target['address'],
                status_display,
                response_time,
                target.get('last_check', 'Jamais'),
                target.get('failures', 0)
            )
            
            self.target_tree.insert("", tk.END, values=values)
            
            # Compter les statuts
            if status == 'online':
                online_count += 1
            elif status == 'offline':
                offline_count += 1
        
        # Mettre à jour les statistiques
        total_count = len(self.target_manager.targets)
        self.stats_label.config(
            text=f"Cibles: {total_count} | En ligne: {online_count} | Hors ligne: {offline_count}"
        )
    
    def log_event(self, message):
        """Ajoute un message au journal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)  # Faire défiler vers le bas
        
        # Limiter la taille du journal
        if self.log_text.index('end-1c').split('.')[0] > '100':
            self.log_text.delete(1.0, 2.0)
    
    def clear_history(self):
        """Efface l'historique des pannes"""
        if messagebox.askyesno("Confirmation", "Effacer tout l'historique des pannes ?"):
            self.history_logger.clear_history()
            self.log_event("Historique des pannes effacé")
    
    def on_closing(self):
        """Gère la fermeture de l'application"""
        self.stop_monitoring()
        self.target_manager.save_targets()
        self.root.destroy()
    
    def run(self):
        """Exécute l'application"""
        # Configurer la fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Démarrer l'interface
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    app = NetPingMonitor()
    app.run()


if __name__ == "__main__":
    main()