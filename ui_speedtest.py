#!/usr/bin/env python3
"""
Interface tableau de bord SpeedTest pour NetPing Monitor
Tableau de bord moderne avec graphiques et statistiques
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour Tkinter

from speedtest_ip_detector import IPDetector
from speedtest_runner import SpeedTestRunner
from speedtest_scheduler import SpeedTestScheduler
from speedtest_storage import SpeedTestStorage
from speedtest_notifier import SpeedTestNotifier
from ui_components import StatCard, StatusBadge, ModernButton


class SpeedTestDashboard(ctk.CTkFrame):
    """Tableau de bord SpeedTest complet"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color='#1e1e1e',
            **kwargs
        )
        
        # Initialisation des modules
        self.ip_detector = IPDetector()
        self.runner = SpeedTestRunner()
        self.storage = SpeedTestStorage()
        self.scheduler = SpeedTestScheduler()
        self.notifier = SpeedTestNotifier()
        
        # État
        self.is_testing = False
        self.test_thread = None
        self.last_ip_info = None
        
        # Démarrer le planificateur
        self.scheduler.start(on_test_due=self.on_scheduled_test)
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Créer l'interface
        self.setup_ui()
        
        # Mise à jour initiale
        self.update_display()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # === HEADER ===
        header_frame = ctk.CTkFrame(self, fg_color='#2d2d2d', corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        ctk.CTkLabel(
            header_frame,
            text="📶 Tableau de Bord SpeedTest",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # === CARTES RAPIDES ===
        self.cards_frame = ctk.CTkFrame(self, fg_color='#1e1e1e')
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Cartes statistiques
        self.card_ip = StatCard(
            self.cards_frame,
            title="IP Publique",
            value="-",
            icon="🌐",
            color="#4a90d9"
        )
        self.card_ip.grid(row=0, column=0, padx=5, pady=5)
        
        self.card_ping = StatCard(
            self.cards_frame,
            title="Ping Actuel",
            value="- ms",
            icon="⏱",
            color="#28a745"
        )
        self.card_ping.grid(row=0, column=1, padx=5, pady=5)
        
        self.card_download = StatCard(
            self.cards_frame,
            title="Download",
            value="- Mbps",
            icon="⬇️",
            color="#17a2b8"
        )
        self.card_download.grid(row=0, column=2, padx=5, pady=5)
        
        self.card_upload = StatCard(
            self.cards_frame,
            title="Upload",
            value="- Mbps",
            icon="⬆️",
            color="#fd7e14"
        )
        self.card_upload.grid(row=0, column=3, padx=5, pady=5)
        
        # === CONTENU PRINCIPAL ===
        self.main_content = ctk.CTkFrame(self, fg_color='#1e1e1e')
        self.main_content.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Boutons de contrôle
        control_frame = ctk.CTkFrame(self.main_content, fg_color='#2d2d2d', corner_radius=12)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Bouton Test Manuel
        self.btn_test = ctk.CTkButton(
            control_frame,
            text="⚡ Test Manuel",
            command=self.run_manual_test,
            fg_color="#28a745",
            hover_color="#218838",
            height=40,
            width=150,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_test.grid(row=0, column=0, padx=15, pady=15)
        
        # Bouton Test Rapide
        self.btn_quick = ctk.CTkButton(
            control_frame,
            text="⚡ Test Rapide",
            command=self.run_quick_test,
            fg_color="#17a2b8",
            hover_color="#138496",
            height=40,
            width=150,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_quick.grid(row=0, column=1, padx=15, pady=15)
        
        # Bouton Configuration
        self.btn_config = ctk.CTkButton(
            control_frame,
            text="⚙️ Configuration",
            command=self.show_config_dialog,
            fg_color="#6c757d",
            hover_color="#5a6268",
            height=40,
            width=150,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_config.grid(row=0, column=2, padx=15, pady=15)
        
        # Bouton Historique
        self.btn_history = ctk.CTkButton(
            control_frame,
            text="📊 Historique",
            command=self.show_history_dialog,
            fg_color="#6f42c1",
            hover_color="#59359a",
            height=40,
            width=150,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        self.btn_history.grid(row=0, column=3, padx=15, pady=15)
        
        # === TABLES ET GRAPHIQUES ===
        content_split = ctk.CTkFrame(self.main_content, fg_color='#1e1e1e')
        content_split.grid(row=1, column=0, sticky="nsew")
        content_split.grid_columnconfigure(0, weight=3)
        content_split.grid_columnconfigure(1, weight=2)
        content_split.grid_rowconfigure(0, weight=1)
        
        # Table historique
        history_frame = ctk.CTkFrame(content_split, fg_color='#2d2d2d', corner_radius=12)
        history_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            history_frame,
            text=" Historique des Tests (Aujourd'hui)",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        
        self.history_text = ctk.CTkTextbox(
            history_frame,
            fg_color='#1e1e1e',
            corner_radius=8,
            font=("Consolas", 10),
            height=200
        )
        self.history_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Statistiques
        stats_frame = ctk.CTkFrame(content_split, fg_color='#2d2d2d', corner_radius=12)
        stats_frame.grid(row=0, column=1, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            stats_frame,
            text=" Statistiques Journalières",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        
        self.stats_text = ctk.CTkTextbox(
            stats_frame,
            fg_color='#1e1e1e',
            corner_radius=8,
            font=("Consolas", 10),
            height=200
        )
        self.stats_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # === BARRE DE STATUT ===
        self.status_bar = ctk.CTkFrame(self, fg_color='#2d2d2d', height=40)
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
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
    
    def update_display(self):
        """Met à jour périodiquement l'affichage"""
        # Mettre à jour les cartes rapides
        latest = self.storage.get_latest_result()
        
        if latest:
            if latest.get('public_ip'):
                self.card_ip.update_value(latest.get('public_ip', '-'))
            
            if latest.get('ping') is not None:
                self.card_ping.update_value(f"{latest['ping']:.1f} ms")
            
            if latest.get('download') is not None:
                self.card_download.update_value(f"{latest['download']:.1f} Mbps")
            
            if latest.get('upload') is not None:
                self.card_upload.update_value(f"{latest['upload']:.1f} Mbps")
        
        # Mettre à jour l'historique
        self.update_history_display()
        
        # Mettre à jour les statistiques
        self.update_stats_display()
        
        # Mettre à jour l'heure
        self.time_label.configure(text=datetime.now().strftime('%H:%M:%S'))
        
        # Planifier la prochaine mise à jour
        self.after(5000, self.update_display)
    
    def update_history_display(self):
        """Met à jour l'affichage de l'historique"""
        results = self.storage.get_results_for_today()
        
        self.history_text.delete("1.0", "end")
        
        if not results:
            self.history_text.insert("end", "Aucun test effectué aujourd'hui")
            return
        
        for result in results[:20]:  # Limiter à 20 entrées
            time_str = result.get('time', '')
            status = result.get('status', 'unknown')
            ping = result.get('ping', '')
            download = result.get('download', '')
            upload = result.get('upload', '')
            
            line = f"{time_str} | "
            
            # Icône selon statut
            if status == 'good':
                line += "🟢 "
            elif status == 'warning':
                line += "🟡 "
            elif status == 'critical':
                line += "🔴 "
            elif status == 'error':
                line += "❌ "
            
            # Mesures
            if ping is not None:
                line += f"Ping: {ping:.1f}ms "
            if download is not None:
                line += f"DL: {download:.1f}Mbps "
            if upload is not None:
                line += f"UP: {upload:.1f}Mbps"
            
            line += "\n"
            self.history_text.insert("end", line)
    
    def update_stats_display(self):
        """Met à jour l'affichage des statistiques"""
        stats = self.storage.get_statistics(days=1)
        
        self.stats_text.delete("1.0", "end")
        
        if stats['total_tests'] == 0:
            self.stats_text.insert("end", "Pas de données")
            return
        
        text = f"Tests aujourd'hui: {stats['total_tests']}\n"
        text += f"Tests réussis: {stats['successful_tests']}\n"
        text += f"Tests échoués: {stats['failed_tests']}\n"
        text += f"Taux réussite: {stats['success_rate']}%\n\n"
        
        if stats['avg_ping'] is not None:
            text += f"Ping moyen: {stats['avg_ping']} ms\n"
            text += f"Ping min: {stats['min_ping']} ms\n"
            text += f"Ping max: {stats['max_ping']} ms\n\n"
        
        if stats['avg_download'] is not None:
            text += f"Download moyen: {stats['avg_download']} Mbps\n"
            text += f"Meilleur download: {stats['best_download']} Mbps\n"
            text += f"Plus faible download: {stats['worst_download']} Mbps\n\n"
        
        if stats['avg_upload'] is not None:
            text += f"Upload moyen: {stats['avg_upload']} Mbps\n"
            text += f"Meilleur upload: {stats['best_upload']} Mbps\n"
            text += f"Plus faible upload: {stats['worst_upload']} Mbps\n\n"
        
        if stats['ip_changes'] > 0:
            text += f"Changements IP: {stats['ip_changes']}\n"
        
        self.stats_text.insert("end", text)
    
    def run_manual_test(self):
        """Exécute un test manuel complet"""
        if self.is_testing:
            return
        
        self.status_label.configure(text="Test en cours...", text_color="#ffc107")
        self.btn_test.configure(state="disabled")
        self.is_testing = True
        
        def test_thread():
            try:
                result = self.runner.run_speedtest()
                
                # Sauvegarder
                self.storage.save_result(result)
                
                # Notifier si nécessaire
                self.notifier.check_and_notify(result)
                
                # Mettre à jour l'interface
                self.after(0, self.on_test_complete, result)
                
            except Exception as e:
                self.after(0, self.on_test_error, str(e))
        
        self.test_thread = threading.Thread(target=test_thread, daemon=True)
        self.test_thread.start()
    
    def run_quick_test(self):
        """Exécute un test rapide (ping uniquement)"""
        if self.is_testing:
            return
        
        self.status_label.configure(text="Test rapide en cours...", text_color="#ffc107")
        self.btn_quick.configure(state="disabled")
        self.is_testing = True
        
        def test_thread():
            try:
                result = self.runner.quick_test()
                
                # Mettre à jour les cartes
                self.after(0, self.on_quick_test_complete, result)
                
            except Exception as e:
                self.after(0, self.on_test_error, str(e))
        
        self.test_thread = threading.Thread(target=test_thread, daemon=True)
        self.test_thread.start()
    
    def on_test_complete(self, result: Dict):
        """Appelé quand un test complet est terminé"""
        self.is_testing = False
        self.btn_test.configure(state="normal")
        self.btn_quick.configure(state="normal")
        
        if result.get('success'):
            self.status_label.configure(text="Test réussi", text_color="#28a745")
            
            # Afficher les résultats
            status = result.get('status', 'unknown')
            message = result.get('status_message', '')
            
            if status == 'good':
                self.status_label.configure(text=f"✅ {message}", text_color="#28a745")
            elif status == 'warning':
                self.status_label.configure(text=f"⚠️ {message}", text_color="#ffc107")
            elif status == 'critical':
                self.status_label.configure(text=f"🔴 {message}", text_color="#dc3545")
            else:
                self.status_label.configure(text="Test terminé", text_color="#28a745")
        
        else:
            self.status_label.configure(text=f"Échec: {result.get('error', 'Inconnue')}", text_color="#dc3545")
        
        # Mettre à jour l'affichage
        self.update_history_display()
        self.update_stats_display()
    
    def on_quick_test_complete(self, result: Dict):
        """Appelé quand un test rapide est terminé"""
        self.is_testing = False
        self.btn_quick.configure(state="normal")
        
        if result.get('success'):
            self.status_label.configure(text=f"Test rapide réussi - Ping: {result['avg_ping']:.1f} ms", text_color="#28a745")
            self.card_ping.update_value(f"{result['avg_ping']:.1f} ms")
        else:
            self.status_label.configure(text=f"Échec test rapide: {result.get('error', 'Inconnue')}", text_color="#dc3545")
    
    def on_test_error(self, error: str):
        """Appelé quand un test rencontre une erreur"""
        self.is_testing = False
        self.btn_test.configure(state="normal")
        self.btn_quick.configure(state="normal")
        self.status_label.configure(text=f"Erreur: {error}", text_color="#dc3545")
    
    def on_scheduled_test(self, scheduled_test):
        """Appelé quand un test planifié est dû"""
        self.status_label.configure(text=f"⏰ Test planifié: {scheduled_test.get_time_string()}", text_color="#ffc107")
        self.run_manual_test()
    
    def show_config_dialog(self):
        """Affiche la boîte de dialogue de configuration"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configuration SpeedTest")
        dialog.geometry("700x500")
        dialog.configure(fg_color="#2d2d2d")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (700 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Onglets
        tabview = ctk.CTkTabview(dialog, fg_color="#2d2d2d")
        tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        tabview.add("Planification")
        tabview.add("Notifications")
        tabview.add("Seuils")
        
        # Onglet 1: Planification
        self._create_schedule_tab(tabview.tab("Planification"))
        
        # Onglet 2: Notifications
        self._create_notifications_tab(tabview.tab("Notifications"))
        
        # Onglet 3: Seuils
        self._create_thresholds_tab(tabview.tab("Seuils"))
    
    def _create_schedule_tab(self, parent):
        """Crée l'onglet de planification"""
        # Configurer la grille
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Frame principal
        schedule_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        schedule_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        schedule_frame.grid_columnconfigure(0, weight=1)
        schedule_frame.grid_rowconfigure(2, weight=1)
        
        # Titre
        ctk.CTkLabel(
            schedule_frame,
            text="📅 Planification des Tests Automatiques",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Liste des tests planifiés
        ctk.CTkLabel(
            schedule_frame,
            text="Tests planifiés:",
            font=("Segoe UI", 12),
            text_color="#b0b0b0"
        ).grid(row=1, column=0, sticky="w")
        
        # Scrollable frame pour les tests
        self.schedule_scroll = ctk.CTkScrollableFrame(
            schedule_frame,
            fg_color="#2d2d2d",
            corner_radius=8,
            width=400,
            height=200
        )
        self.schedule_scroll.grid(row=2, column=0, sticky="nsew", pady=(10, 20))
        
        # Charger la planification actuelle
        self.load_schedule_list()
        
        # Contrôles d'ajout
        add_frame = ctk.CTkFrame(schedule_frame, fg_color="#2d2d2d", corner_radius=8)
        add_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        add_frame.grid_columnconfigure(0, weight=1)
        add_frame.grid_columnconfigure(1, weight=1)
        add_frame.grid_columnconfigure(2, weight=1)
        add_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(
            add_frame,
            text="Heure:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=0, column=0, padx=(15, 5), pady=15)
        
        # Heure
        self.hour_var = ctk.StringVar(value="08")
        hour_entry = ctk.CTkEntry(
            add_frame,
            textvariable=self.hour_var,
            width=40,
            placeholder_text="HH"
        )
        hour_entry.grid(row=0, column=1, padx=5, pady=15)
        
        ctk.CTkLabel(
            add_frame,
            text=":",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=0, column=2)
        
        # Minutes
        self.minute_var = ctk.StringVar(value="00")
        minute_entry = ctk.CTkEntry(
            add_frame,
            textvariable=self.minute_var,
            width=40,
            placeholder_text="MM"
        )
        minute_entry.grid(row=0, column=3, padx=5, pady=15)
        
        # Toggle jour/quotidien
        self.daily_var = ctk.BooleanVar(value=True)
        daily_check = ctk.CTkCheckBox(
            add_frame,
            text="Quotidien",
            variable=self.daily_var,
            onvalue=True,
            offvalue=False,
            font=("Segoe UI", 11)
        )
        daily_check.grid(row=0, column=4, padx=(20, 10), pady=15)
        
        # Bouton ajouter
        add_btn = ctk.CTkButton(
            add_frame,
            text="➕ Ajouter",
            command=self.add_scheduled_test,
            fg_color="#28a745",
            hover_color="#218838",
            width=100,
            height=32
        )
        add_btn.grid(row=0, column=5, padx=10, pady=15)
        
        # Boutons de contrôle
        control_frame = ctk.CTkFrame(schedule_frame, fg_color="#1e1e1e")
        control_frame.grid(row=4, column=0, sticky="ew")
        
        # Sauvegarder
        save_btn = ctk.CTkButton(
            control_frame,
            text="💾 Sauvegarder",
            command=self.save_schedule,
            fg_color="#007bff",
            hover_color="#0056b3",
            width=120,
            height=35
        )
        save_btn.grid(row=0, column=0, padx=5, pady=10)
        
        # Activer/désactiver tout
        toggle_btn = ctk.CTkButton(
            control_frame,
            text="🔧 Activer/Désactiver Tout",
            command=self.toggle_all_tests,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=160,
            height=35
        )
        toggle_btn.grid(row=0, column=1, padx=5, pady=10)
        
        # Supprimer tout
        delete_btn = ctk.CTkButton(
            control_frame,
            text="🗑️ Supprimer Tout",
            command=self.delete_all_tests,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=120,
            height=35
        )
        delete_btn.grid(row=0, column=2, padx=5, pady=10)
    
    def _create_notifications_tab(self, parent):
        """Crée l'onglet des notifications"""
        # Configurer la grille
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Frame principal avec scroll
        notifications_scroll = ctk.CTkScrollableFrame(parent, fg_color="#1e1e1e", corner_radius=12)
        notifications_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        notifications_scroll.grid_columnconfigure(0, weight=1)
        
        # Section Email
        email_frame = ctk.CTkFrame(notifications_scroll, fg_color="#2d2d2d", corner_radius=8)
        email_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        email_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            email_frame,
            text="📧 Configuration Email",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Toggle Email
        self.email_enabled = ctk.BooleanVar(value=self.notifier.config.config.get('email_enabled', False))
        email_toggle = ctk.CTkCheckBox(
            email_frame,
            text="Activer les notifications par Email",
            variable=self.email_enabled,
            onvalue=True,
            offvalue=False,
            command=self.toggle_email_notifications,
            font=("Segoe UI", 11)
        )
        email_toggle.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Formulaire Email (désactivé si non activé)
        self.email_config_frame = ctk.CTkFrame(email_frame, fg_color="#3d3d3d", corner_radius=8)
        self.email_config_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.email_config_frame.grid_columnconfigure(1, weight=1)
        
        # Champs SMTP
        row = 0
        ctk.CTkLabel(
            self.email_config_frame,
            text="Serveur SMTP:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=(15, 5))
        
        self.smtp_server = ctk.CTkEntry(
            self.email_config_frame,
            placeholder_text="smtp.gmail.com"
        )
        self.smtp_server.grid(row=row, column=1, sticky="ew", padx=5, pady=(15, 5))
        self.smtp_server.insert(0, self.notifier.config.config.get('email_smtp_server', ''))
        
        row += 1
        ctk.CTkLabel(
            self.email_config_frame,
            text="Port:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.smtp_port = ctk.CTkEntry(
            self.email_config_frame,
            placeholder_text="587",
            width=80
        )
        self.smtp_port.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.smtp_port.insert(0, str(self.notifier.config.config.get('email_smtp_port', 587)))
        
        row += 1
        ctk.CTkLabel(
            self.email_config_frame,
            text="Email:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.email_username = ctk.CTkEntry(
            self.email_config_frame,
            placeholder_text="votre.email@gmail.com"
        )
        self.email_username.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.email_username.insert(0, self.notifier.config.config.get('email_username', ''))
        
        row += 1
        ctk.CTkLabel(
            self.email_config_frame,
            text="Mot de passe:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.email_password = ctk.CTkEntry(
            self.email_config_frame,
            placeholder_text="Mot de passe",
            show="*"
        )
        self.email_password.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        row += 1
        ctk.CTkLabel(
            self.email_config_frame,
            text="Destinataires:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.email_recipients = ctk.CTkTextbox(
            self.email_config_frame,
            height=60,
            width=300
        )
        self.email_recipients.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        recipients = self.notifier.config.config.get('email_recipients', [])
        if recipients:
            self.email_recipients.insert("end", "\n".join(recipients))
        
        # Test Email
        row += 1
        test_email_btn = ctk.CTkButton(
            self.email_config_frame,
            text="📧 Tester Email",
            command=self.test_email_config,
            fg_color="#17a2b8",
            hover_color="#138496",
            width=100,
            height=30
        )
        test_email_btn.grid(row=row, column=1, sticky="e", padx=5, pady=(15, 15))
        
        # Section WhatsApp
        whatsapp_frame = ctk.CTkFrame(notifications_scroll, fg_color="#2d2d2d", corner_radius=8)
        whatsapp_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        whatsapp_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            whatsapp_frame,
            text="📱 Configuration WhatsApp",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Toggle WhatsApp
        self.whatsapp_enabled = ctk.BooleanVar(value=self.notifier.config.config.get('whatsapp_enabled', False))
        whatsapp_toggle = ctk.CTkCheckBox(
            whatsapp_frame,
            text="Activer les notifications WhatsApp",
            variable=self.whatsapp_enabled,
            onvalue=True,
            offvalue=False,
            command=self.toggle_whatsapp_notifications,
            font=("Segoe UI", 11)
        )
        whatsapp_toggle.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Formulaire WhatsApp
        self.whatsapp_config_frame = ctk.CTkFrame(whatsapp_frame, fg_color="#3d3d3d", corner_radius=8)
        self.whatsapp_config_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.whatsapp_config_frame.grid_columnconfigure(1, weight=1)
        
        # Champs WhatsApp
        row = 0
        ctk.CTkLabel(
            self.whatsapp_config_frame,
            text="URL API:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=(15, 5))
        
        self.whatsapp_api_url = ctk.CTkEntry(
            self.whatsapp_config_frame,
            placeholder_text="https://api.whatsapp.com/send"
        )
        self.whatsapp_api_url.grid(row=row, column=1, sticky="ew", padx=5, pady=(15, 5))
        self.whatsapp_api_url.insert(0, self.notifier.config.config.get('whatsapp_api_url', ''))
        
        row += 1
        ctk.CTkLabel(
            self.whatsapp_config_frame,
            text="Clé API:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.whatsapp_api_key = ctk.CTkEntry(
            self.whatsapp_config_frame,
            placeholder_text="Votre clé API",
            show="*"
        )
        self.whatsapp_api_key.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        row += 1
        ctk.CTkLabel(
            self.whatsapp_config_frame,
            text="Destinataires:",
            font=("Segoe UI", 11),
            text_color="#ffffff"
        ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.whatsapp_recipients = ctk.CTkTextbox(
            self.whatsapp_config_frame,
            height=60,
            width=300
        )
        self.whatsapp_recipients.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        recipients = self.notifier.config.config.get('whatsapp_recipients', [])
        if recipients:
            self.whatsapp_recipients.insert("end", "\n".join(recipients))
        
        # Test WhatsApp
        row += 1
        test_whatsapp_btn = ctk.CTkButton(
            self.whatsapp_config_frame,
            text="📱 Tester WhatsApp",
            command=self.test_whatsapp_config,
            fg_color="#28a745",
            hover_color="#218838",
            width=100,
            height=30
        )
        test_whatsapp_btn.grid(row=row, column=1, sticky="e", padx=5, pady=(15, 15))
        
        # Mettre à jour l'état initial
        self.toggle_email_notifications()
        self.toggle_whatsapp_notifications()
    
    def _create_thresholds_tab(self, parent):
        """Crée l'onglet des seuils"""
        # Configurer la grille
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Frame principal avec scroll
        thresholds_scroll = ctk.CTkScrollableFrame(parent, fg_color="#1e1e1e", corner_radius=12)
        thresholds_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        thresholds_scroll.grid_columnconfigure(0, weight=1)
        
        # Titre
        ctk.CTkLabel(
            thresholds_scroll,
            text="⚡ Configuration des Seuils d'Alerte",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).grid(row=0, column=0, sticky="w", pady=(0, 25))
        
        # Seuils Ping
        ping_frame = ctk.CTkFrame(thresholds_scroll, fg_color="#2d2d2d", corner_radius=8)
        ping_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            ping_frame,
            text="⏱ Seuils Ping (en ms)",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        ping_form = ctk.CTkFrame(ping_frame, fg_color="#3d3d3d", corner_radius=8)
        ping_form.pack(fill="x", padx=20, pady=(0, 20))
        ping_form.grid_columnconfigure(1, weight=1)
        
        # Ping Critique
        ctk.CTkLabel(
            ping_form,
            text="Ping Critique (>):",
            font=("Segoe UI", 11),
            text_color="#dc3545"
        ).grid(row=0, column=0, sticky="w", padx=(15, 5), pady=(15, 5))
        
        self.ping_critical = ctk.CTkEntry(
            ping_form,
            placeholder_text="200",
            width=80
        )
        self.ping_critical.grid(row=0, column=1, sticky="w", padx=5, pady=(15, 5))
        self.ping_critical.insert(0, str(self.notifier.config.config.get('ping_threshold_critical', 200)))
        
        # Ping Warning
        ctk.CTkLabel(
            ping_form,
            text="Ping Warning (>):",
            font=("Segoe UI", 11),
            text_color="#ffc107"
        ).grid(row=1, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.ping_warning = ctk.CTkEntry(
            ping_form,
            placeholder_text="100",
            width=80
        )
        self.ping_warning.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.ping_warning.insert(0, str(self.notifier.config.config.get('ping_threshold_warning', 100)))
        
        # Seuils Download
        download_frame = ctk.CTkFrame(thresholds_scroll, fg_color="#2d2d2d", corner_radius=8)
        download_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            download_frame,
            text="⬇️ Seuils Download (en Mbps)",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        download_form = ctk.CTkFrame(download_frame, fg_color="#3d3d3d", corner_radius=8)
        download_form.pack(fill="x", padx=20, pady=(0, 20))
        download_form.grid_columnconfigure(1, weight=1)
        
        # Download Critique (<)
        ctk.CTkLabel(
            download_form,
            text="Download Critique (<):",
            font=("Segoe UI", 11),
            text_color="#dc3545"
        ).grid(row=0, column=0, sticky="w", padx=(15, 5), pady=(15, 5))
        
        self.download_critical = ctk.CTkEntry(
            download_form,
            placeholder_text="10",
            width=80
        )
        self.download_critical.grid(row=0, column=1, sticky="w", padx=5, pady=(15, 5))
        self.download_critical.insert(0, str(self.notifier.config.config.get('download_threshold_critical', 10)))
        
        # Download Warning (<)
        ctk.CTkLabel(
            download_form,
            text="Download Warning (<):",
            font=("Segoe UI", 11),
            text_color="#ffc107"
        ).grid(row=1, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.download_warning = ctk.CTkEntry(
            download_form,
            placeholder_text="50",
            width=80
        )
        self.download_warning.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.download_warning.insert(0, str(self.notifier.config.config.get('download_threshold_warning', 50)))
        
        # Seuils Upload
        upload_frame = ctk.CTkFrame(thresholds_scroll, fg_color="#2d2d2d", corner_radius=8)
        upload_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            upload_frame,
            text="⬆️ Seuils Upload (en Mbps)",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        upload_form = ctk.CTkFrame(upload_frame, fg_color="#3d3d3d", corner_radius=8)
        upload_form.pack(fill="x", padx=20, pady=(0, 20))
        upload_form.grid_columnconfigure(1, weight=1)
        
        # Upload Critique (<)
        ctk.CTkLabel(
            upload_form,
            text="Upload Critique (<):",
            font=("Segoe UI", 11),
            text_color="#dc3545"
        ).grid(row=0, column=0, sticky="w", padx=(15, 5), pady=(15, 5))
        
        self.upload_critical = ctk.CTkEntry(
            upload_form,
            placeholder_text="5",
            width=80
        )
        self.upload_critical.grid(row=0, column=1, sticky="w", padx=5, pady=(15, 5))
        self.upload_critical.insert(0, str(self.notifier.config.config.get('upload_threshold_critical', 5)))
        
        # Upload Warning (<)
        ctk.CTkLabel(
            upload_form,
            text="Upload Warning (<):",
            font=("Segoe UI", 11),
            text_color="#ffc107"
        ).grid(row=1, column=0, sticky="w", padx=(15, 5), pady=5)
        
        self.upload_warning = ctk.CTkEntry(
            upload_form,
            placeholder_text="20",
            width=80
        )
        self.upload_warning.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.upload_warning.insert(0, str(self.notifier.config.config.get('upload_threshold_warning', 20)))
        
        # Alertes activées
        alerts_frame = ctk.CTkFrame(thresholds_scroll, fg_color="#2d2d2d", corner_radius=8)
        alerts_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            alerts_frame,
            text="🔔 Alertes Activées",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        alerts_form = ctk.CTkFrame(alerts_frame, fg_color="#3d3d3d", corner_radius=8)
        alerts_form.pack(fill="x", padx=20, pady=(0, 20))
        alerts_form.grid_columnconfigure(0, weight=1)
        alerts_form.grid_columnconfigure(1, weight=1)
        
        # Checkboxes pour les alertes
        self.alert_test_failure = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_test_failure', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Test échoué",
            variable=self.alert_test_failure,
            font=("Segoe UI", 11)
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.alert_ping_critical = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_ping_critical', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Ping critique",
            variable=self.alert_ping_critical,
            font=("Segoe UI", 11)
        ).grid(row=0, column=1, sticky="w", padx=15, pady=(15, 5))
        
        self.alert_download_low = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_download_low', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Download faible",
            variable=self.alert_download_low,
            font=("Segoe UI", 11)
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.alert_upload_low = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_upload_low', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Upload faible",
            variable=self.alert_upload_low,
            font=("Segoe UI", 11)
        ).grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        self.alert_ip_change = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_ip_change', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Changement IP",
            variable=self.alert_ip_change,
            font=("Segoe UI", 11)
        ).grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        self.alert_missed_test = ctk.BooleanVar(value=self.notifier.config.config.get('alert_on_missed_test', True))
        ctk.CTkCheckBox(
            alerts_form,
            text="Test manqué",
            variable=self.alert_missed_test,
            font=("Segoe UI", 11)
        ).grid(row=2, column=1, sticky="w", padx=15, pady=5)
        
        # Bouton de sauvegarde
        save_btn = ctk.CTkButton(
            thresholds_scroll,
            text="💾 Sauvegarder la Configuration",
            command=self.save_thresholds,
            fg_color="#28a745",
            hover_color="#218838",
            height=40,
            width=250
        )
        save_btn.grid(row=5, column=0, pady=20)
    
    def show_history_dialog(self):
        """Affiche la boîte de dialogue d'historique"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Historique des Tests SpeedTest")
        dialog.geometry("800x600")
        dialog.configure(fg_color="#2d2d2d")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (800 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Titre
        ctk.CTkLabel(
            dialog,
            text="📊 Historique des Tests SpeedTest",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=20)
        
        # Onglets pour différentes périodes
        tabview = ctk.CTkTabview(dialog, fg_color="#1e1e1e", width=750, height=450)
        tabview.pack(pady=(0, 20))
        tabview.add("Aujourd'hui")
        tabview.add("7 derniers jours")
        tabview.add("30 derniers jours")
        
        # Onglet Aujourd'hui
        today_results = self.storage.get_results_for_today()
        self._populate_history_tab(tabview.tab("Aujourd'hui"), today_results, "Aujourd'hui")
        
        # Onglet 7 derniers jours
        week_results = self.storage.get_results_for_last_n_days(7)
        self._populate_history_tab(tabview.tab("7 derniers jours"), week_results, "7 derniers jours")
        
        # Onglet 30 derniers jours
        month_results = self.storage.get_results_for_last_n_days(30)
        self._populate_history_tab(tabview.tab("30 derniers jours"), month_results, "30 derniers jours")
        
        # Boutons d'action
        button_frame = ctk.CTkFrame(dialog, fg_color="#1e1e1e")
        button_frame.pack(pady=(0, 20))
        
        ctk.CTkButton(
            button_frame,
            text="📊 Exporter Excel",
            command=self.export_history,
            fg_color="#28a745",
            hover_color="#218838",
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="📈 Générer Graphique",
            command=self.generate_history_chart,
            fg_color="#007bff",
            hover_color="#0056b3",
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Fermer",
            command=dialog.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=120
        ).pack(side="left", padx=10)
    
    def generate_report(self):
        """Génère un rapport Excel"""
        from speedtest_excel_exporter import SpeedTestExcelExporter
        
        exporter = SpeedTestExcelExporter()
        results = self.storage.get_results_for_today()
        
        if not results:
            self.status_label.configure(text="Aucun résultat à exporter", text_color="#ffc107")
            return
        
        filepath = exporter.generate_daily_report(results)
        
        if filepath:
            self.status_label.configure(text=f"✅ Rapport créé: {filepath}", text_color="#28a745")
        else:
            self.status_label.configure(text="❌ Erreur création rapport", text_color="#dc3545")
    
    def stop(self):
        """Arrête tous les composants"""
        self.scheduler.stop()


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU DASHBOARD SPEEDTEST")
    print("=" * 60)
    
    app = ctk.CTk()
    app.title("Test Dashboard SpeedTest")
    app.geometry("1000x600")
    app.configure(fg_color="#1e1e1e")
    
    dashboard = SpeedTestDashboard(app)
    dashboard.pack(fill="both", expand=True, padx=10, pady=10)
    
    print("\nDashboard lancé. Fermez la fenêtre pour terminer.")
    
    try:
        app.mainloop()
    finally:
        dashboard.stop()
    
    print("\nTest terminé.")

    def load_schedule_list(self):
        """Charge la liste des tests planifiés"""
        for widget in self.schedule_scroll.winfo_children():
            widget.destroy()
        
        tests = self.scheduler.get_all_tests()
        
        if not tests:
            ctk.CTkLabel(
                self.schedule_scroll,
                text="Aucun test planifié",
                font=("Segoe UI", 11),
                text_color="#999999"
            ).pack(pady=20)
            return
        
        for i, test in enumerate(tests):
            test_frame = ctk.CTkFrame(self.schedule_scroll, fg_color="#3d3d3d", corner_radius=6)
            test_frame.pack(fill="x", pady=5, padx=5)
            
            enabled = ctk.BooleanVar(value=test.enabled)
            
            def create_toggle_callback(idx, var):
                def callback():
                    self.scheduler.toggle_test(idx, var.get())
                return callback
            
            toggle = ctk.CTkCheckBox(
                test_frame,
                text=f"{test.hour:02d}:{test.minute:02d} {'(Quotidien)' if test.daily else ''}",
                variable=enabled,
                command=create_toggle_callback(i, enabled),
                font=("Segoe UI", 11)
            )
            toggle.pack(side="left", padx=10, pady=10)
            
            # Bouton supprimer
            ctk.CTkButton(
                test_frame,
                text="🗑️",
                width=30,
                height=30,
                fg_color="#dc3545",
                hover_color="#c82333",
                command=lambda idx=i: self.delete_scheduled_test(idx)
            ).pack(side="right", padx=10, pady=10)
    
    def add_scheduled_test(self):
        """Ajoute un nouveau test planifié"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            daily = self.daily_var.get()
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Heure invalide")
            
            self.scheduler.add_test(hour, minute, enabled=True, daily=daily)
            self.load_schedule_list()
            
        except ValueError:
            self.status_label.configure(text="❌ Heure invalide", text_color="#dc3545")
    
    def delete_scheduled_test(self, idx):
        """Supprime un test planifié"""
        self.scheduler.delete_test(idx)
        self.load_schedule_list()
    
    def save_schedule(self):
        """Sauvegarde la planification"""
        self.scheduler.save_config()
        self.status_label.configure(text="✅ Planification sauvegardée", text_color="#28a745")
    
    def toggle_all_tests(self):
        """Active/désactive tous les tests"""
        tests = self.scheduler.get_all_tests()
        all_enabled = all(t.enabled for t in tests)
        
        for i, test in enumerate(tests):
            self.scheduler.toggle_test(i, not all_enabled)
        
        self.load_schedule_list()
        self.status_label.configure(
            text=f"✅ Tous les tests {'activés' if not all_enabled else 'désactivés'}",
            text_color="#28a745"
        )
    
    def delete_all_tests(self):
        """Supprime tous les tests"""
        self.scheduler.clear_all()
        self.load_schedule_list()
        self.status_label.configure(text="✅ Tous les tests supprimés", text_color="#28a745")
    
    def toggle_email_notifications(self):
        """Active/désactive les notifications email"""
        enabled = self.email_enabled.get()
        state = "normal" if enabled else "disabled"
        
        for child in self.email_config_frame.winfo_children():
            if isinstance(child, (ctk.CTkEntry, ctk.CTkTextbox)):
                child.configure(state=state)
    
    def toggle_whatsapp_notifications(self):
        """Active/désactive les notifications WhatsApp"""
        enabled = self.whatsapp_enabled.get()
        state = "normal" if enabled else "disabled"
        
        for child in self.whatsapp_config_frame.winfo_children():
            if isinstance(child, (ctk.CTkEntry, ctk.CTkTextbox)):
                child.configure(state=state)
    
    def test_email_config(self):
        """Teste la configuration email"""
        self.notifier.configure_email(
            smtp_server=self.smtp_server.get(),
            smtp_port=int(self.smtp_port.get()),
            username=self.email_username.get(),
            password=self.email_password.get(),
            recipients=[r.strip() for r in self.email_recipients.get("1.0", "end").split("\n") if r.strip()],
            use_tls=True
        )
        
        success = self.notifier.test_email()
        
        if success:
            self.status_label.configure(text="✅ Configuration email testée avec succès", text_color="#28a745")
        else:
            self.status_label.configure(text="❌ Échec test email - vérifiez la configuration", text_color="#dc3545")
    
    def test_whatsapp_config(self):
        """Teste la configuration WhatsApp"""
        self.notifier.configure_whatsapp(
            api_url=self.whatsapp_api_url.get(),
            api_key=self.whatsapp_api_key.get(),
            recipients=[r.strip() for r in self.whatsapp_recipients.get("1.0", "end").split("\n") if r.strip()]
        )
        
        success = self.notifier.test_whatsapp()
        
        if success:
            self.status_label.configure(text="✅ Configuration WhatsApp testée avec succès", text_color="#28a745")
        else:
            self.status_label.configure(text="❌ Échec test WhatsApp - vérifiez la configuration", text_color="#dc3545")
    
    def save_thresholds(self):
        """Sauvegarde les seuils d'alerte"""
        try:
            self.notifier.update_thresholds(
                ping_critical=int(self.ping_critical.get()),
                ping_warning=int(self.ping_warning.get()),
                download_critical=float(self.download_critical.get()),
                download_warning=float(self.download_warning.get()),
                upload_critical=float(self.upload_critical.get()),
                upload_warning=float(self.upload_warning.get())
            )
            
            self.notifier.enable_alerts(
                test_failure=self.alert_test_failure.get(),
                ping_critical=self.alert_ping_critical.get(),
                download_low=self.alert_download_low.get(),
                upload_low=self.alert_upload_low.get(),
                ip_change=self.alert_ip_change.get(),
                missed_test=self.alert_missed_test.get()
            )
            
            self.runner.set_thresholds(
                ping_critical=int(self.ping_critical.get()),
                ping_warning=int(self.ping_warning.get()),
                download_critical=float(self.download_critical.get()),
                download_warning=float(self.download_warning.get()),
                upload_critical=float(self.upload_critical.get()),
                upload_warning=float(self.upload_warning.get())
            )
            
            self.status_label.configure(text="✅ Seuils sauvegardés", text_color="#28a745")
            
        except ValueError as e:
            self.status_label.configure(text=f"❌ Erreur: {str(e)}", text_color="#dc3545")
    
    def _populate_history_tab(self, parent, results, period):
        """Remplit un onglet d'historique"""
        if not results:
            ctk.CTkLabel(
                parent,
                text=f"Aucun test dans cette période ({period})",
                font=("Segoe UI", 12),
                text_color="#999999"
            ).pack(pady=50)
            return
        
        # Texte formaté
        textbox = ctk.CTkTextbox(parent, fg_color="#1e1e1e", font=("Consolas", 10))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        header = f"Historique: {period}\n{'='*60}\n\n"
        textbox.insert("end", header)
        
        for result in results:
            date = result.get('date', '')
            time = result.get('time', '')
            status = result.get('status', '')
            ip = result.get('public_ip', '')
            ping = result.get('ping', '')
            download = result.get('download', '')
            upload = result.get('upload', '')
            
            line = f"{date} {time} | {status:10} | "
            
            # Icône selon statut
            if status == 'good':
                line += "🟢 "
            elif status == 'warning':
                line += "🟡 "
            elif status == 'critical':
                line += "🔴 "
            elif status == 'error':
                line += "❌ "
            elif status == 'missed':
                line += "⏰ "
            else:
                line += "❓ "
            
            # Données
            line += f"IP: {ip} "
            
            if ping is not None:
                line += f"Ping: {ping:.1f}ms "
            if download is not None:
                line += f"DL: {download:.1f}Mbps "
            if upload is not None:
                line += f"UP: {upload:.1f}Mbps"
            
            line += "\n"
            textbox.insert("end", line)
        
        textbox.configure(state="disabled")
    
    def export_history(self):
        """Exporte l'historique"""
        from speedtest_excel_exporter import SpeedTestExcelExporter
        
        exporter = SpeedTestExcelExporter()
        all_results = self.storage.get_results_for_last_n_days(30)
        
        if not all_results:
            self.status_label.configure(text="❌ Aucune donnée à exporter", text_color="#dc3545")
            return
        
        # Dates
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        filepath = exporter.generate_custom_report(
            all_results,
            "Rapport Historique SpeedTest",
            start_date,
            end_date
        )
        
        if filepath:
            self.status_label.configure(text=f"✅ Rapport exporté: {filepath}", text_color="#28a745")
        else:
            self.status_label.configure(text="❌ Échec export", text_color="#dc3545")
    
    def generate_history_chart(self):
        """Génère un graphique d'historique"""
        import matplotlib.pyplot as plt
        from datetime import datetime
        
        results = self.storage.get_results_for_last_n_days(7)
        
        if not results:
            self.status_label.configure(text="❌ Pas assez de données pour le graphique", text_color="#dc3545")
            return
        
        # Extraire données
        times = []
        pings = []
        downloads = []
        uploads = []
        
        for result in results:
            try:
                date_time = datetime.strptime(f"{result['date']} {result['time']}", "%Y-%m-%d %H:%M:%S")
                times.append(date_time)
                
                if result.get('ping'):
                    pings.append(result['ping'])
                if result.get('download'):
                    downloads.append(result['download'])
                if result.get('upload'):
                    uploads.append(result['upload'])
            except:
                continue
        
        # Créer graphique
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Ping
        if pings:
            ax1.plot(times[:len(pings)], pings, 'b-', label='Ping')
            ax1.set_ylabel('Ping (ms)', color='b')
            ax1.tick_params(axis='y', labelcolor='b')
            ax1.set_title('Évolution du Ping (7 derniers jours)')
            ax1.grid(True, alpha=0.3)
        
        # Download/Upload
        if downloads or uploads:
            ax2.plot(times[:len(downloads)], downloads, 'g-', label='Download')
            ax2.plot(times[:len(uploads)], uploads, 'r-', label='Upload')
            ax2.set_xlabel('Date/Heure')
            ax2.set_ylabel('Débit (Mbps)', color='g')
            ax2.tick_params(axis='y', labelcolor='g')
            ax2.set_title('Évolution du Débit (7 derniers jours)')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        
        plt.tight_layout()
        
        # Sauvegarder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"speedtest_chart_{timestamp}.png"
        plt.savefig(filename, dpi=100)
        
        self.status_label.configure(text=f"✅ Graphique généré: {filename}", text_color="#28a745")
        
        # Fermer pour éviter les fuites mémoire
        plt.close('all')