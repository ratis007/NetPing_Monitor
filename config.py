#!/usr/bin/env python3
"""
Configuration pour NetPing Monitor
Gère les paramètres d'apparence et le mode sombre
"""

import customtkinter as ctk


# Thème par défaut
THEME_DARK = {
    'background': '#1e1e1e',
    'secondary_background': '#2d2d2d',
    'tertiary_background': '#3d3d3d',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'accent_color': '#4a90d9',
    'success_color': '#28a745',
    'danger_color': '#dc3545',
    'warning_color': '#ffc107',
    'card_radius': '12',
    'button_radius': '8',
    'entry_radius': '8',
}


class ThemeManager:
    """Gestionnaire de thème pour l'application"""
    
    def __init__(self):
        self.current_theme = 'dark'
        self.colors = THEME_DARK.copy()
    
    def set_dark_mode(self):
        """Active le mode sombre"""
        self.current_theme = 'dark'
        self.colors = THEME_DARK.copy()
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')  # Thème bleu pour le accent
    
    def set_light_mode(self):
        """Active le mode clair"""
        self.current_theme = 'light'
        ctk.set_appearance_mode('light')
        ctk.set_default_color_theme('blue')
    
    def get_color(self, color_name):
        """Récupère une couleur du thème"""
        return self.colors.get(color_name, '#000000')
    
    def get_style(self):
        """Récupère un dictionnaire de styles pour les widgets"""
        return {
            'fg_color': self.colors['secondary_background'],
            'bg_color': self.colors['background'],
            'text_color': self.colors['text_primary'],
            'corner_radius': self.colors['card_radius'],
            'button_color': self.colors['accent_color'],
        }


# Instanciation globale
theme_manager = ThemeManager()
