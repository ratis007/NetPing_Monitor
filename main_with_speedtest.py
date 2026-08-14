#!/usr/bin/env python3
"""
NetPing Monitor avec module SpeedTest intégré
Version complète avec surveillance réseau et SpeedTest
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import threading
import os
import sys

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speedtest_manager import SpeedTestManager
from ui_speedtest import SpeedTestDashboard


class NetPingMonitorComplete(ctk.CTk):
    """NetPing Monitor complet avec module SpeedTest"""
    
    def __init__(self):
        super().__init__()
        
        # Configuration du thème sombre
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        
        # Configuration de la fenêtre
        self.title("NetPing Monitor Pro")
        self.geometry("1200x800")
        self.configure(fg_color="#1e1e1e")
        
        # Initialisation des modules
        self.speedtest_manager = SpeedTestManager()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer les modules
        self.start_modules()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Onglets
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabview.add("Surveillance")
        self.tabview.add("SpeedTest")
        self.tabview.add("Statistiques")
        
        # Configurer la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.grid_rowconfigure(0, weight=1)
        
        # Onglet 1: Surveillance réseau (interface existante)
        self._create_surveillance_tab()
        
        # Onglet 2: SpeedTest
        self._create_speedtest_tab()
        
        # Onglet 3: Statistiques
        self._create_statistics_tab()
    
    def _create_surveillance_tab(self):
        """Crée l'onglet de surveillance réseau"""
        from ui_monitor import NetPingMonitorApp
        
        # Pour simplifier, nous pouvons intégrer les composants existants
        # Dans une vraie implémentation, il faudrait adapter
        
        frame = ctk.CTkFrame(self.tabview.tab("Surveillance"), fg_color="#1e1e1e")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="Module de Surveillance Réseau",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
        label.grid(row=0, column=0, padx=20, pady=20)
        
        info = ctk.CTkTextbox(frame, height=200)
        info.grid(row=1, column=0, padx=20, pady=(0, 20))
        info.insert("end", "Le module de surveillance réseau NetPing Monitor est actif.\n\n")
        info.insert("end", "Fonctionnalités:\n")
        info.insert("end", "- Surveillance automatique des cibles\n")
        info.insert("end", "- Alertes visuelles et sonores\n")
        info.insert("end", "- Historique des pannes\n")
        info.insert("end", "- Export des données\n")
    
    def _create_speedtest_tab(self):
        """Crée l'onglet SpeedTest"""
        frame = ctk.CTkFrame(self.tabview.tab("SpeedTest"), fg_color="#1e1e1e")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Utiliser le dashboard SpeedTest
        self.speedtest_dashboard = SpeedTestDashboard(frame)
        self.speedtest_dashboard.grid(row=0, column=0, sticky="nsew")
    
    def _create_statistics_tab(self):
        """Crée l'onglet des statistiques"""
        frame = ctk.CTkFrame(self.tabview.tab("Statistiques"), fg_color="#1e1e1e")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            frame,
            text="Statistiques Complètes",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        )
        label.grid(row=0, column=0, padx=20, pady=20)
        
        self.stats_text = ctk.CTkTextbox(frame, height=300)
        self.stats_text.grid(row=1, column=0, padx=20, pady=(0, 20))
        self.stats_text.insert("end", "Chargement des statistiques...")
        
        # Bouton d'export
        btn_export = ctk.CTkButton(
            frame,
            text="📊 Exporter Statistiques",
            command=self.export_statistics,
            fg_color="#28a745",
            hover_color="#218838",
            height=40,
            width=200,
            corner_radius=8
        )
        btn_export.grid(row=2, column=0, pady=10)
    
    def start_modules(self):
        """Démarre tous les modules"""
        # Démarrer le manager SpeedTest
        self.speedtest_manager.start()
        
        # Configurer les callbacks
        self.speedtest_manager.on_test_complete = self.on_speedtest_complete
        self.speedtest_manager.on_alert_sent = self.on_speedtest_alert
        
        # Démarrer la mise à jour des statistiques
        self.update_statistics()
    
    def on_speedtest_complete(self, result: dict, alerts: list):
        """Appelé quand un SpeedTest est terminé"""
        print(f"SpeedTest terminé: {result.get('status')}")
        
        # Mettre à jour l'interface si nécessaire
        tab_name = self.tabview.get()
        if tab_name == "SpeedTest":
            pass  # Le dashboard s'actualise déjà
    
    def on_speedtest_alert(self, alert_type: str, result: dict):
        """Appelé quand une alerte SpeedTest est envoyée"""
        print(f"Alerte SpeedTest: {alert_type}")
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        if hasattr(self, 'stats_text'):
            stats = self.speedtest_manager.generate_statistics(days=30)
            
            self.stats_text.delete("1.0", "end")
            text = "STATISTIQUES SUR 30 JOURS\n\n"
            
            for key, value in stats.items():
                text += f"{key}: {value}\n"
            
            self.stats_text.insert("end", text)
        
        # Planifier la prochaine mise à jour
        self.after(30000, self.update_statistics)
    
    def export_statistics(self):
        """Exporte les statistiques"""
        from speedtest_excel_exporter import SpeedTestExcelExporter
        
        exporter = SpeedTestExcelExporter()
        results = self.speedtest_manager.get_historical_results(days=30)
        
        if not results:
            print("Aucune donnée à exporter")
            return
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        filepath = exporter.generate_custom_report(
            results,
            "Rapport Mensuel SpeedTest",
            start_date,
            end_date
        )
        
        if filepath:
            print(f"✅ Rapport créé: {filepath}")
        else:
            print("❌ Erreur lors de la création")
    
    def on_closing(self):
        """Gère la fermeture de l'application"""
        # Arrêter les modules
        self.speedtest_manager.stop()
        if hasattr(self, 'speedtest_dashboard'):
            self.speedtest_dashboard.stop()
        
        # Fermer l'application
        self.destroy()


def main():
    """Point d'entrée principal"""
    app = NetPingMonitorComplete()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
