#!/usr/bin/env python3
"""
Module de notifications pour NetPing Monitor
Envoie des alertes par email et WhatsApp
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
import threading
from typing import Dict, List, Optional, Callable
import requests


class NotificationConfig:
    """Configuration des notifications"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config_file = config_file
        self.config = {
            # Email
            'email_enabled': False,
            'email_smtp_server': 'smtp.gmail.com',
            'email_smtp_port': 587,
            'email_use_tls': True,
            'email_username': '',
            'email_password': '',
            'email_recipients': [],
            
            # WhatsApp
            'whatsapp_enabled': False,
            'whatsapp_api_url': '',
            'whatsapp_api_key': '',
            'whatsapp_recipients': [],
            
            # Seuils d'alerte
            'ping_threshold_critical': 200,
            'ping_threshold_warning': 100,
            'download_threshold_critical': 10,
            'download_threshold_warning': 50,
            'upload_threshold_critical': 5,
            'upload_threshold_warning': 20,
            
            # Alertes activées
            'alert_on_test_failure': True,
            'alert_on_ping_critical': True,
            'alert_on_download_low': True,
            'alert_on_upload_low': True,
            'alert_on_ip_change': True,
            'alert_on_missed_test': True,
            
            # Rate limiting
            'min_time_between_alerts': 300,  # 5 minutes
        }
        
        self.last_alert_time = {}
        self.lock = threading.Lock()
        
        self.load_config()
    
    def load_config(self):
        """Charge la configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
        except Exception as e:
            print(f"Erreur chargement config: {e}")
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
            return False
    
    def update(self, **kwargs):
        """Met à jour la configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self.save_config()
    
    def can_send_alert(self, alert_type: str) -> bool:
        """Vérifie si une alerte peut être envoyée (rate limiting)"""
        with self.lock:
            now = datetime.now().timestamp()
            last_time = self.last_alert_time.get(alert_type, 0)
            min_interval = self.config.get('min_time_between_alerts', 300)
            
            if now - last_time >= min_interval:
                self.last_alert_time[alert_type] = now
                return True
            return False


class EmailNotifier:
    """Gestionnaire de notifications par email"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send_email(self, subject: str, body: str, recipients: List[str] = None) -> bool:
        """
        Envoie un email
        
        Args:
            subject: Sujet
            body: Corps du message
            recipients: Destinataires (optionnel)
            
        Returns:
            True si envoyé
        """
        if not self.config.config.get('email_enabled'):
            return False
        
        recipients = recipients or self.config.config.get('email_recipients', [])
        
        if not recipients:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[NetPing Monitor] {subject}"
            msg['From'] = self.config.config.get('email_username')
            msg['To'] = ', '.join(recipients)
            
            # Corps texte
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Corps HTML
            html = self._format_html_email(subject, body)
            html_part = MIMEText(html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Envoyer
            smtp_server = self.config.config.get('email_smtp_server')
            smtp_port = self.config.config.get('email_smtp_port')
            username = self.config.config.get('email_username')
            password = self.config.config.get('email_password')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if self.config.config.get('email_use_tls'):
                    server.starttls()
                server.login(username, password)
                server.sendmail(username, recipients, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return False
    
    def _format_html_email(self, subject: str, body: str) -> str:
        """Formate le corps HTML de l'email"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4472C4; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; }}
                .critical {{ background: #f8d7da; border-left-color: #dc3545; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NetPing Monitor</h1>
                    <p>{subject}</p>
                </div>
                <div class="content">
                    <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{body}</pre>
                </div>
                <div class="footer">
                    <p>NetPing Monitor - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_speedtest_alert(self, result: Dict, alert_type: str) -> bool:
        """
        Envoie une alerte SpeedTest
        
        Args:
            result: Résultat du test
            alert_type: Type d'alerte
            
        Returns:
            True si envoyé
        """
        subjects = {
            'test_failure': 'SpeedTest Échoué',
            'ping_critical': 'Ping Critique',
            'download_low': 'Download Faible',
            'upload_low': 'Upload Faible',
            'ip_change': 'Changement IP',
            'missed_test': 'Test Manqué'
        }
        
        subject = subjects.get(alert_type, 'Alerte SpeedTest')
        
        body = f"""
Alerte: {subject}
Date: {result.get('date', 'N/A')} {result.get('time', 'N/A')}

"""
        
        if alert_type == 'test_failure':
            body += f"Le test SpeedTest a échoué.\nErreur: {result.get('error', 'Inconnue')}"
        
        elif alert_type == 'ping_critical':
            body += f"""Ping critique détecté!
Ping actuel: {result.get('ping', 'N/A')} ms
Seuil critique: {self.config.config.get('ping_threshold_critical')} ms
"""
        
        elif alert_type == 'download_low':
            body += f"""Download faible détecté!
Download actuel: {result.get('download', 'N/A')} Mbps
Seuil critique: {self.config.config.get('download_threshold_critical')} Mbps
"""
        
        elif alert_type == 'upload_low':
            body += f"""Upload faible détecté!
Upload actuel: {result.get('upload', 'N/A')} Mbps
Seuil critique: {self.config.config.get('upload_threshold_critical')} Mbps
"""
        
        elif alert_type == 'ip_change':
            body += f"""Changement d'IP publique détecté!
Nouvelle IP: {result.get('public_ip', 'N/A')}
ISP: {result.get('isp', 'N/A')}
Localisation: {result.get('city', '')}, {result.get('country', '')}
"""
        
        body += f"""

---
IP Publique: {result.get('public_ip', 'N/A')}
ISP: {result.get('isp', 'N/A')}
Ping: {result.get('ping', 'N/A')} ms
Download: {result.get('download', 'N/A')} Mbps
Upload: {result.get('upload', 'N/A')} Mbps
Statut: {result.get('status', 'N/A')}
"""
        
        return self.send_email(subject, body)


class WhatsAppNotifier:
    """Gestionnaire de notifications WhatsApp"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send_message(self, message: str, recipients: List[str] = None) -> bool:
        """
        Envoie un message WhatsApp
        
        Args:
            message: Message à envoyer
            recipients: Destinataires (optionnel)
            
        Returns:
            True si envoyé
        """
        if not self.config.config.get('whatsapp_enabled'):
            return False
        
        recipients = recipients or self.config.config.get('whatsapp_recipients', [])
        
        if not recipients:
            return False
        
        api_url = self.config.config.get('whatsapp_api_url')
        api_key = self.config.config.get('whatsapp_api_key')
        
        if not api_url:
            return False
        
        try:
            # Support pour différentes APIs WhatsApp
            # Peut être adapté selon l'API utilisée (Twilio, WhatsApp Business API, etc.)
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            for recipient in recipients:
                payload = {
                    'to': recipient,
                    'message': message
                }
                
                response = requests.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code not in (200, 201):
                    print(f"Erreur WhatsApp: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Erreur envoi WhatsApp: {e}")
            return False
    
    def send_speedtest_alert(self, result: Dict, alert_type: str) -> bool:
        """
        Envoie une alerte SpeedTest par WhatsApp
        
        Args:
            result: Résultat du test
            alert_type: Type d'alerte
            
        Returns:
            True si envoyé
        """
        emoji = {
            'test_failure': '❌',
            'ping_critical': '⚠️',
            'download_low': '📉',
            'upload_low': '📉',
            'ip_change': '🔄',
            'missed_test': '⏰'
        }
        
        titles = {
            'test_failure': 'SpeedTest Échoué',
            'ping_critical': 'Ping Critique',
            'download_low': 'Download Faible',
            'upload_low': 'Upload Faible',
            'ip_change': 'Changement IP',
            'missed_test': 'Test Manqué'
        }
        
        title = titles.get(alert_type, 'Alerte')
        icon = emoji.get(alert_type, '⚠️')
        
        message = f"""{icon} *{title}*

📅 {result.get('date', 'N/A')} {result.get('time', 'N/A')}
🌐 IP: {result.get('public_ip', 'N/A')}
📡 ISP: {result.get('isp', 'N/A')}
"""
        
        if result.get('ping') is not None:
            message += f"⏱ Ping: {result.get('ping')} ms\n"
        
        if result.get('download') is not None:
            message += f"⬇️ Download: {result.get('download'):.1f} Mbps\n"
        
        if result.get('upload') is not None:
            message += f"⬆️ Upload: {result.get('upload'):.1f} Mbps\n"
        
        message += f"\n_Status: {result.get('status', 'N/A')}_"
        
        return self.send_message(message)


class SpeedTestNotifier:
    """Gestionnaire principal des notifications SpeedTest"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config = NotificationConfig(config_file)
        self.email_notifier = EmailNotifier(self.config)
        self.whatsapp_notifier = WhatsAppNotifier(self.config)
        self.previous_ip = None
        self.on_alert_sent: Optional[Callable] = None
    
    def check_and_notify(self, result: Dict) -> List[str]:
        """
        Vérifie les conditions d'alerte et envoie les notifications
        
        Args:
            result: Résultat du SpeedTest
            
        Returns:
            Liste des alertes envoyées
        """
        alerts_sent = []
        
        # 1. Test échoué
        if not result.get('success'):
            if self.config.config.get('alert_on_test_failure'):
                if self.config.can_send_alert('test_failure'):
                    self._send_alerts(result, 'test_failure')
                    alerts_sent.append('test_failure')
            return alerts_sent
        
        # 2. Ping critique
        ping = result.get('ping', 0)
        if ping > self.config.config.get('ping_threshold_critical', 200):
            if self.config.config.get('alert_on_ping_critical'):
                if self.config.can_send_alert('ping_critical'):
                    self._send_alerts(result, 'ping_critical')
                    alerts_sent.append('ping_critical')
        
        # 3. Download faible
        download = result.get('download', 0)
        if download < self.config.config.get('download_threshold_critical', 10):
            if self.config.config.get('alert_on_download_low'):
                if self.config.can_send_alert('download_low'):
                    self._send_alerts(result, 'download_low')
                    alerts_sent.append('download_low')
        
        # 4. Upload faible
        upload = result.get('upload', 0)
        if upload < self.config.config.get('upload_threshold_critical', 5):
            if self.config.config.get('alert_on_upload_low'):
                if self.config.can_send_alert('upload_low'):
                    self._send_alerts(result, 'upload_low')
                    alerts_sent.append('upload_low')
        
        # 5. Changement IP
        current_ip = result.get('public_ip')
        if self.previous_ip and current_ip and current_ip != self.previous_ip:
            if self.config.config.get('alert_on_ip_change'):
                if self.config.can_send_alert('ip_change'):
                    self._send_alerts(result, 'ip_change')
                    alerts_sent.append('ip_change')
        
        # Mettre à jour l'IP précédente
        if current_ip:
            self.previous_ip = current_ip
        
        return alerts_sent
    
    def _send_alerts(self, result: Dict, alert_type: str):
        """Envoie les alertes sur tous les canaux activés"""
        # Email
        self.email_notifier.send_speedtest_alert(result, alert_type)
        
        # WhatsApp
        self.whatsapp_notifier.send_speedtest_alert(result, alert_type)
        
        # Callback
        if self.on_alert_sent:
            try:
                self.on_alert_sent(alert_type, result)
            except Exception as e:
                print(f"Erreur callback: {e}")
    
    def notify_missed_test(self, scheduled_time: str):
        """
        Notifie un test manqué
        
        Args:
            scheduled_time: Heure prévue du test
        """
        if not self.config.config.get('alert_on_missed_test'):
            return
        
        if not self.config.can_send_alert('missed_test'):
            return
        
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': scheduled_time,
            'status': 'missed',
            'error': 'Test non exécuté à l\'heure prévue'
        }
        
        self._send_alerts(result, 'missed_test')
    
    def update_thresholds(self, ping_critical: int = None, ping_warning: int = None,
                         download_critical: float = None, download_warning: float = None,
                         upload_critical: float = None, upload_warning: float = None):
        """Met à jour les seuils d'alerte"""
        updates = {}
        if ping_critical is not None:
            updates['ping_threshold_critical'] = ping_critical
        if ping_warning is not None:
            updates['ping_threshold_warning'] = ping_warning
        if download_critical is not None:
            updates['download_threshold_critical'] = download_critical
        if download_warning is not None:
            updates['download_threshold_warning'] = download_warning
        if upload_critical is not None:
            updates['upload_threshold_critical'] = upload_critical
        if upload_warning is not None:
            updates['upload_threshold_warning'] = upload_warning
        
        self.config.update(**updates)
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, recipients: List[str], use_tls: bool = True):
        """Configure les notifications par email"""
        self.config.update(
            email_enabled=True,
            email_smtp_server=smtp_server,
            email_smtp_port=smtp_port,
            email_username=username,
            email_password=password,
            email_recipients=recipients,
            email_use_tls=use_tls
        )
    
    def configure_whatsapp(self, api_url: str, api_key: str, recipients: List[str]):
        """Configure les notifications WhatsApp"""
        self.config.update(
            whatsapp_enabled=True,
            whatsapp_api_url=api_url,
            whatsapp_api_key=api_key,
            whatsapp_recipients=recipients
        )
    
    def enable_alerts(self, test_failure: bool = None, ping_critical: bool = None,
                     download_low: bool = None, upload_low: bool = None,
                     ip_change: bool = None, missed_test: bool = None):
        """Active/désactive les types d'alertes"""
        updates = {}
        if test_failure is not None:
            updates['alert_on_test_failure'] = test_failure
        if ping_critical is not None:
            updates['alert_on_ping_critical'] = ping_critical
        if download_low is not None:
            updates['alert_on_download_low'] = download_low
        if upload_low is not None:
            updates['alert_on_upload_low'] = upload_low
        if ip_change is not None:
            updates['alert_on_ip_change'] = ip_change
        if missed_test is not None:
            updates['alert_on_missed_test'] = missed_test
        
        self.config.update(**updates)
    
    def test_email(self) -> bool:
        """Teste l'envoi d'email"""
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'public_ip': 'Test',
            'isp': 'Test ISP',
            'ping': 50,
            'download': 100,
            'upload': 50,
            'status': 'test'
        }
        return self.email_notifier.send_speedtest_alert(result, 'test_failure')
    
    def test_whatsapp(self) -> bool:
        """Teste l'envoi WhatsApp"""
        message = f"Test NetPing Monitor - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        return self.whatsapp_notifier.send_message(message)


# Test du module
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE NOTIFIER")
    print("=" * 60)
    
    notifier = SpeedTestNotifier("test_notification_config.json")
    
    # Configuration test
    print("\n1. Configuration des seuils...")
    notifier.update_thresholds(
        ping_critical=200,
        ping_warning=100,
        download_critical=10,
        download_warning=50
    )
    print("   ✅ Seuils configurés")
    
    # Activer les alertes
    print("\n2. Activation des alertes...")
    notifier.enable_alerts(
        test_failure=True,
        ping_critical=True,
        download_low=True,
        ip_change=True
    )
    print("   ✅ Alertes activées")
    
    # Test de vérification d'alerte
    print("\n3. Test de vérification d'alerte...")
    
    # Résultat critique
    critical_result = {
        'date': '2026-06-22',
        'time': '12:00:00',
        'success': True,
        'public_ip': '41.243.13.114',
        'isp': 'Orange',
        'city': 'Paris',
        'ping': 250,  # Critique
        'download': 5,  # Critique
        'upload': 3,  # Critique
        'status': 'critical'
    }
    
    alerts = notifier.check_and_notify(critical_result)
    print(f"   Alertes envoyées: {alerts}")
    
    # Test changement IP
    print("\n4. Test changement IP...")
    notifier.previous_ip = '1.2.3.4'
    
    ip_change_result = {
        'date': '2026-06-22',
        'time': '12:30:00',
        'success': True,
        'public_ip': '5.6.7.8',  # Nouvelle IP
        'isp': 'Orange',
        'ping': 30,
        'download': 100,
        'upload': 50,
        'status': 'good'
    }
    
    alerts = notifier.check_and_notify(ip_change_result)
    print(f"   Alertes envoyées: {alerts}")
    
    # Statut
    print("\n5. Configuration actuelle:")
    for key, value in notifier.config.config.items():
        if 'password' not in key and 'api_key' not in key:
            print(f"   {key}: {value}")
    
    # Nettoyer
    if os.path.exists("test_notification_config.json"):
        os.remove("test_notification_config.json")
    
    print("\nTest terminé.")
