#!/usr/bin/env python3
"""
Interface principale NetPing Monitor avec CustomTkinter
Tableau de bord moderne de supervision réseau
"""

import customtkinter as ctk
from datetime import datetime
import threading
import time

from config import theme_manager
from ui_components import StatCard, TargetTable, AlertHistory, Header, ModernButton, StatusBadge
from network_monitor import NetworkMonitor
from target_manager import TargetManager
from alert_system import AlertSystem
from history_logger import HistoryLogger


class NetPingMonitorApp(ctk.CTk):
    """Application principale NetPing Monitor avec interface moderne"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration du thème sombre
        theme_manager.set_dark_mode()
        
        # Configuration de la fenêtre
        self.title("NetPing Monitor")
        self.geometry("1200x800")
        self.configure(fg_color="#1e1e1e")
        
        # Initialisation des composants
        self.monitor = NetworkMonitor()
        self.target_manager = TargetManager()
        self.alert_system = AlertSystem()
        self.history_logger = HistoryLogger()
        
        # Variables d'état
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_count = 0
        
        # Charger les cibles sauvegardées
        self.target_manager.load_targets()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer la mise à jour périodique
        self.update_display()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        self.header = Header(self)
        self.header.grid(row=0, column=0, sticky="ew")
        
        # === CONTENU PRINCIPAL ===
        self.main_content = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)
        
        # === CARTES STATISTIQUES ===
        self.stats_frame = ctk.CTkFrame(self.main_content, fg_color="#1e1e1e")
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Créer les cartes
        self.card_total = StatCard(
            self.stats_frame, 
            title="Total Cibles", 
            value=0, 
            icon="📊", 
            color="#4a90d9"
        )
        self.card_total.grid(row=0, column=0, padx=(0, 15))
        
        self.card_online = StatCard(
            self.stats_frame, 
            title="En Ligne", 
            value=0, 
            icon="🟢", 
            color="#28a745"
        )
        self.card_online.grid(row=0, column=1, padx=15)
        
        self.card_offline = StatCard(
            self.stats_frame, 
            title="Hors Ligne", 
            value=0, 
            icon="🔴", 
            color="#dc3545"
        )
        self.card_offline.grid(row=0, column=2, padx=15)
        
        self.card_alerts = StatCard(
            self.stats_frame, 
            title="Alertes", 
            value=0, 
            icon="⚠️", 
            color="#ffc107"
        )
        self.card_alerts.grid(row=0, column=3, padx=(15, 0))
        
        # === BOUTONS DE CONTRÔLE ===
        self.control_frame = ctk.CTkFrame(self.main_content, fg_color="#2d2d2d", corner_radius=12)
        self.control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Bouton Ajouter
        self.btn_add = ModernButton(
            self.control_frame, 
            text="Ajouter une cible", 
            icon="➕",
            command=self.show_add_target_dialog
        )
        self.btn_add.grid(row=0, column=0, padx=15, pady=15)
        
        # Bouton Démarrer
        self.btn_start = ModernButton(
            self.control_frame, 
            text="Démarrer la surveillance", 
            icon="▶",
            command=self.start_monitoring,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.btn_start.grid(row=0, column=1, padx=15, pady=15)
        
        # Bouton Arrêter
        self.btn_stop = ModernButton(
            self.control_frame, 
            text="Arrêter la surveillance", 
            icon="⏹",
            command=self.stop_monitoring,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.btn_stop.grid(row=0, column=2, padx=15, pady=15)
        self.btn_stop.configure(state="disabled")
        
        # === TABLEAU ET HISTORIQUE ===
        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="#1e1e1e")
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Tableau des cibles
        self.target_table = TargetTable(
            self.content_frame, 
            targets=self.target_manager.targets,
            on_delete=self.delete_target
        )
        self.target_table.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Historique des alertes
        self.alert_history = AlertHistory(self.content_frame)
        self.alert_history.grid(row=0, column=1, sticky="nsew")
        
        # === BARRE DE STATUT ===
        self.status_bar = ctk.CTkFrame(self, fg_color="#2d2d2d", height=30)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text="Prêt", 
            font=("Segoe UI", 10),
            text_color="#b0b0b0"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=5, sticky="w")
        
        self.time_label = ctk.CTkLabel(
            self.status_bar, 
            text="", 
            font=("Segoe UI", 10),
            text_color="#b0b0b0"
        )
        self.time_label.grid(row=0, column=1, padx=15, pady=5, sticky="e")
    
    def show_add_target_dialog(self):
        """Affiche une boîte de dialogue pour ajouter une cible"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter une cible")
        dialog.geometry("400x250")
        dialog.configure(fg_color="#2d2d2d")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Titre
        title = ctk.CTkLabel(
            dialog, 
            text="Nouvelle Cible", 
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Nom
        label_name = ctk.CTkLabel(dialog, text="Nom:", font=("Segoe UI", 11))
        label_name.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        entry_name = ctk.CTkEntry(dialog, width=200, height=35, corner_radius=8)
        entry_name.grid(row=1, column=1, padx=20, pady=10)
        
        # Adresse
        label_address = ctk.CTkLabel(dialog, text="Adresse:", font=("Segoe UI", 11))
        label_address.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        entry_address = ctk.CTkEntry(dialog, width=200, height=35, corner_radius=8)
        entry_address.grid(row=2, column=1, padx=20, pady=10)
        
        # Intervalle
        label_interval = ctk.CTkLabel(dialog, text="Intervalle (s):", font=("Segoe UI", 11))
        label_interval.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        entry_interval = ctk.CTkEntry(dialog, width=200, height=35, corner_radius=8)
        entry_interval.insert(0, "30")
        entry_interval.grid(row=3, column=1, padx=20, pady=10)
        
        # Boutons
        def add_target():
            name = entry_name.get().strip()
            address = entry_address.get().strip()
            interval = entry_interval.get().strip()
            
            if not name or not address:
                return
            
            try:
                interval = int(interval)
                if interval < 5:
                    interval = 5
                
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
                self.update_stats()
                self.target_table.update_targets(self.target_manager.targets)
                self.alert_history.add_alert(name, "Cible ajoutée")
                dialog.destroy()
                
            except ValueError:
                pass
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="#2d2d2d")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        btn_add = ctk.CTkButton(
            btn_frame, 
            text="Ajouter", 
            command=add_target,
            fg_color="#28a745",
            hover_color="#218838",
            width=100,
            height=35,
            corner_radius=8
        )
        btn_add.grid(row=0, column=0, padx=10)
        
        btn_cancel = ctk.CTkButton(
            btn_frame, 
            text="Annuler", 
            command=dialog.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100,
            height=35,
            corner_radius=8
        )
        btn_cancel.grid(row=0, column=1, padx=10)
    
    def delete_target(self, target_name):
        """Supprime une cible"""
        self.target_manager.remove_target(target_name)
        self.update_stats()
        self.target_table.update_targets(self.target_manager.targets)
        self.alert_history.add_alert(target_name, "Cible supprimée")
    
    def start_monitoring(self):
        """Démarre la surveillance"""
        if not self.target_manager.targets:
            return
        
        self.monitoring_active = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        
        # Démarrer le thread de surveillance
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.status_label.configure(text="Surveillance active", text_color="#28a745")
        self.alert_history.add_alert("Système", "Surveillance démarrée")
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.monitoring_active = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        
        self.status_label.configure(text="Surveillance arrêtée", text_color="#dc3545")
        self.alert_history.add_alert("Système", "Surveillance arrêtée")
    
    def monitoring_loop(self):
        """Boucle de surveillance"""
        while self.monitoring_active:
            targets = self.target_manager.targets.copy()
            
            for target_name, target in targets.items():
                if not self.monitoring_active:
                    break
                
                current_time = time.time()
                last_check = target.get('last_check_timestamp', 0)
                
                if current_time - last_check >= target['interval']:
                    result = self.monitor.ping_target(target['address'])
                    
                    if result['success']:
                        target['status'] = 'online'
                        target['response_time'] = result['response_time']
                        target['consecutive_failures'] = 0
                    else:
                        target['failures'] += 1
                        target['consecutive_failures'] += 1
                        
                        if target['consecutive_failures'] >= 3:
                            target['status'] = 'offline'
                            if target['consecutive_failures'] == 3:
                                self.trigger_alert(target)
                    
                    target['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    target['last_check_timestamp'] = current_time
                    
                    if target['status'] == 'offline':
                        self.history_logger.log_outage(target)
            
            time.sleep(1)
    
    def trigger_alert(self, target):
        """Déclenche une alerte"""
        self.alert_count += 1
        self.alert_system.trigger_alert(target)
        self.alert_history.add_alert(target['name'], "HORS LIGNE - 3 échecs consécutifs")
    
    def update_stats(self):
        """Met à jour les statistiques"""
        total = len(self.target_manager.targets)
        online = len([t for t in self.target_manager.targets.values() if t.get('status') == 'online'])
        offline = len([t for t in self.target_manager.targets.values() if t.get('status') == 'offline'])
        
        self.card_total.update_value(total)
        self.card_online.update_value(online)
        self.card_offline.update_value(offline)
        self.card_alerts.update_value(self.alert_count)
    
    def update_display(self):
        """Met à jour l'affichage périodiquement"""
        if self.monitoring_active:
            self.update_stats()
            self.target_table.update_targets(self.target_manager.targets)
        
        # Mettre à jour l'heure
        self.time_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        
        # Planifier la prochaine mise à jour
        self.after(1000, self.update_display)
    
    def on_closing(self):
        """Gère la fermeture de l'application"""
        self.stop_monitoring()
        self.target_manager.save_targets()
        self.destroy()


def main():
    """Point d'entrée principal"""
    app = NetPingMonitorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
