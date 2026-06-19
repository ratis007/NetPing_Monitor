#!/usr/bin/env python3
"""
Composants réutilisables pour NetPing Monitor
Créé avec CustomTkinter pour une interface moderne
"""

import customtkinter as ctk
from datetime import datetime


class StatCard(ctk.CTkFrame):
    """Carte de statistique avec icône et valeur"""
    
    def __init__(self, master, title, value, icon="📊", color="#4a90d9", **kwargs):
        super().__init__(
            master,
            fg_color=kwargs.get('fg_color', '#2d2d2d'),
            corner_radius=12,
            width=150,
            height=80
        )
        
        self.title = title
        self.value = value
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        # Icône
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI", 24),
            text_color=color
        )
        self.icon_label.grid(row=0, column=0, pady=(10, 5))
        
        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color="#b0b0b0"
        )
        self.title_label.grid(row=1, column=0, pady=(0, 5))
        
        # Valeur
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"
        )
        self.value_label.grid(row=2, column=0, pady=(0, 10))
    
    def update_value(self, new_value):
        """Met à jour la valeur de la carte"""
        self.value = new_value
        self.value_label.configure(text=str(new_value))


class StatusBadge(ctk.CTkLabel):
    """Badge de statut (Online/Offline/Instable)"""
    
    def __init__(self, master, status):
        self.status = status.lower()
        
        # Configuration des couleurs selon le statut
        if self.status == 'online':
            bg_color = '#28a745'
            text_color = '#ffffff'
            icon = '🟢'
        elif self.status == 'offline':
            bg_color = '#dc3545'
            text_color = '#ffffff'
            icon = '🔴'
        elif self.status == 'instable':
            bg_color = '#ffc107'
            text_color = '#000000'
            icon = '🟡'
        else:
            bg_color = '#6c757d'
            text_color = '#ffffff'
            icon = '⚪'
        
        super().__init__(
            master,
            text=f"{icon} {status.upper()}",
            font=("Segoe UI", 10, "bold"),
            fg_color=bg_color,
            text_color=text_color,
            corner_radius=6,
            padx=8,
            pady=4
        )


class ModernButton(ctk.CTkButton):
    """Bouton moderne avec effet hover"""
    
    def __init__(self, master, text, command=None, icon="", **kwargs):
        super().__init__(
            master,
            text=f"{icon} {text}" if icon else text,
            command=command,
            fg_color=kwargs.get('fg_color', '#4a90d9'),
            hover_color=kwargs.get('hover_color', '#357abd'),
            corner_radius=8,
            height=36,
            font=("Segoe UI", 11, "bold")
        )


class TargetTable(ctk.CTkFrame):
    """Tableau moderne pour afficher les cibles"""
    
    def __init__(self, master, targets, on_delete=None, **kwargs):
        super().__init__(
            master,
            fg_color='#2d2d2d',
            corner_radius=12,
            **kwargs
        )
        
        self.targets = targets
        self.on_delete = on_delete
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # En-têtes
        headers = ["Nom", "Adresse", "Statut", "Temps (ms)", "Dernier contrôle"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self,
                text=header,
                font=("Segoe UI", 10, "bold"),
                text_color="#b0b0b0",
                anchor="w",
                padx=10,
                pady=8
            )
            label.grid(row=0, column=i, sticky="ew")
        
        # Créer une frame scrollable pour les lignes
        self.entries_frame = ctk.CTkScrollableFrame(
            self,
            fg_color='#2d2d2d',
            corner_radius=0,
            height=200
        )
        self.entries_frame.grid(row=1, column=0, sticky="nsew")
        self.entries_frame.grid_columnconfigure(0, weight=1)
        
        # Afficher les cibles
        self.render_targets()
    
    def render_targets(self):
        """Rend les cibles dans le tableau"""
        # Nettoyer les anciennes entrées
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        
        # Afficher chaque cible
        for i, (name, target) in enumerate(self.targets.items()):
            self._add_target_row(i, name, target)
    
    def _add_target_row(self, row, name, target):
        """Ajoute une ligne pour une cible"""
        # Nom
        name_label = ctk.CTkLabel(
            self.entries_frame,
            text=name,
            font=("Segoe UI", 11),
            text_color="#ffffff",
            anchor="w",
            padx=10,
            pady=5
        )
        name_label.grid(row=row, column=0, sticky="ew")
        
        # Adresse
        address_label = ctk.CTkLabel(
            self.entries_frame,
            text=target.get('address', ''),
            font=("Segoe UI", 11),
            text_color="#b0b0b0",
            anchor="w",
            padx=10,
            pady=5
        )
        address_label.grid(row=row, column=1, sticky="ew")
        
        # Statut
        status = target.get('status', 'unknown')
        status_badge = StatusBadge(self.entries_frame, status)
        status_badge.grid(row=row, column=2, padx=10, pady=5)
        
        # Temps de réponse
        response_time = target.get('response_time', 0)
        time_label = ctk.CTkLabel(
            self.entries_frame,
            text=f"{response_time} ms" if response_time > 0 else "-",
            font=("Segoe UI", 11),
            text_color="#ffffff",
            anchor="w",
            padx=10,
            pady=5
        )
        time_label.grid(row=row, column=3, sticky="ew")
        
        # Dernier contrôle
        last_check = target.get('last_check', 'Jamais')
        last_check_label = ctk.CTkLabel(
            self.entries_frame,
            text=last_check,
            font=("Segoe UI", 10),
            text_color="#808080",
            anchor="w",
            padx=10,
            pady=5
        )
        last_check_label.grid(row=row, column=4, sticky="ew")
        
        # Bouton de suppression
        delete_btn = ctk.CTkButton(
            self.entries_frame,
            text="🗑",
            width=30,
            height=30,
            corner_radius=5,
            fg_color='#dc3545',
            hover_color='#c82333',
            command=lambda n=name: self.on_delete(n) if self.on_delete else None
        )
        delete_btn.grid(row=row, column=5, padx=10, pady=5)
    
    def update_targets(self, new_targets):
        """Met à jour les cibles affichées"""
        self.targets = new_targets
        self.render_targets()


class AlertHistory(ctk.CTkFrame):
    """Zone d'historique des alertes"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color='#2d2d2d',
            corner_radius=12,
            **kwargs
        )
        
        self.alerts = []
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre
        title_label = ctk.CTkLabel(
            self,
            text=" Historique des Alertes",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff",
            anchor="w",
            padx=15,
            pady=10
        )
        title_label.grid(row=0, column=0, sticky="ew")
        
        # Zone de liste des alertes
        self.alerts_text = ctk.CTkTextbox(
            self,
            fg_color='#1e1e1e',
            corner_radius=8,
            font=("Consolas", 10),
            height=150
        )
        self.alerts_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    def add_alert(self, target_name, message):
        """Ajoute une alerte à l'historique"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] ⚠ {target_name}: {message}\n"
        
        self.alerts_text.insert("end", alert_text)
        self.alerts_text.see("end")
    
    def clear_alerts(self):
        """Efface l'historique des alertes"""
        self.alerts_text.delete("1.0", "end")


class Header(ctk.CTkFrame):
    """En-tête de l'application"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color='#1e1e1e',
            height=70,
            corner_radius=0,
            **kwargs
        )
        
        # Configuration de la grille
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Titre de l'application
        title_label = ctk.CTkLabel(
            self,
            text=" NetPing Monitor",
            font=("Segoe UI", 24, "bold"),
            text_color="#ffffff",
            anchor="w",
            padx=20
        )
        title_label.grid(row=0, column=0, sticky="w")
