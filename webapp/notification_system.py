"""
Système de notifications et alertes pour TradingAgents
Support pour email, SMS, webhook, Slack, Discord, etc.
"""

import os
import json
import smtplib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    CONSOLE = "console"

class NotificationPriority(Enum):
    """Priorités de notification"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NotificationConfig:
    """Configuration d'un canal de notification"""
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = None
    min_priority: NotificationPriority = NotificationPriority.NORMAL
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}

@dataclass
class Notification:
    """Notification à envoyer"""
    id: str
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    sent_channels: List[NotificationChannel] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.sent_channels is None:
            self.sent_channels = []

class EmailNotifier:
    """Notificateur email"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email', self.username)
        self.to_emails = config.get('to_emails', [])
        
        if isinstance(self.to_emails, str):
            self.to_emails = [self.to_emails]
    
    def send(self, notification: Notification) -> bool:
        """Envoyer une notification par email"""
        try:
            if not self.username or not self.password or not self.to_emails:
                logger.warning("⚠️ Configuration email incomplète")
                return False
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[TradingAgents] {notification.title}"
            
            # Corps du message
            body = f"""
{notification.message}

Priorité: {notification.priority.value.upper()}
Timestamp: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---
TradingAgents Automated Trading System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"📧 Email envoyé: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False

class WebhookNotifier:
    """Notificateur webhook"""
    
    def __init__(self, config: Dict[str, Any]):
        self.url = config.get('url')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.method = config.get('method', 'POST')
        self.timeout = config.get('timeout', 10)
    
    def send(self, notification: Notification) -> bool:
        """Envoyer une notification via webhook"""
        try:
            if not self.url:
                logger.warning("⚠️ URL webhook non configurée")
                return False
            
            # Préparer les données
            payload = {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority.value,
                'timestamp': notification.timestamp.isoformat(),
                'data': notification.data
            }
            
            # Envoyer la requête
            response = requests.request(
                method=self.method,
                url=self.url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"🔗 Webhook envoyé: {notification.title}")
                return True
            else:
                logger.error(f"❌ Webhook échec: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur webhook: {e}")
            return False

class SlackNotifier:
    """Notificateur Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#trading')
        self.username = config.get('username', 'TradingAgents')
        self.icon_emoji = config.get('icon_emoji', ':robot_face:')
    
    def send(self, notification: Notification) -> bool:
        """Envoyer une notification Slack"""
        try:
            if not self.webhook_url:
                logger.warning("⚠️ Webhook Slack non configuré")
                return False
            
            # Déterminer la couleur basée sur la priorité
            color_map = {
                NotificationPriority.LOW: '#36a64f',      # Vert
                NotificationPriority.NORMAL: '#2196F3',   # Bleu
                NotificationPriority.HIGH: '#ff9800',     # Orange
                NotificationPriority.CRITICAL: '#f44336'  # Rouge
            }
            
            color = color_map.get(notification.priority, '#2196F3')
            
            # Préparer le message Slack
            payload = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': self.icon_emoji,
                'attachments': [{
                    'color': color,
                    'title': notification.title,
                    'text': notification.message,
                    'fields': [
                        {
                            'title': 'Priorité',
                            'value': notification.priority.value.upper(),
                            'short': True
                        },
                        {
                            'title': 'Timestamp',
                            'value': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'short': True
                        }
                    ],
                    'footer': 'TradingAgents',
                    'ts': int(notification.timestamp.timestamp())
                }]
            }
            
            # Envoyer à Slack
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"💬 Slack envoyé: {notification.title}")
                return True
            else:
                logger.error(f"❌ Slack échec: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur Slack: {e}")
            return False

class DiscordNotifier:
    """Notificateur Discord"""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url')
        self.username = config.get('username', 'TradingAgents')
        self.avatar_url = config.get('avatar_url')
    
    def send(self, notification: Notification) -> bool:
        """Envoyer une notification Discord"""
        try:
            if not self.webhook_url:
                logger.warning("⚠️ Webhook Discord non configuré")
                return False
            
            # Déterminer la couleur basée sur la priorité
            color_map = {
                NotificationPriority.LOW: 0x36a64f,      # Vert
                NotificationPriority.NORMAL: 0x2196F3,   # Bleu
                NotificationPriority.HIGH: 0xff9800,     # Orange
                NotificationPriority.CRITICAL: 0xf44336  # Rouge
            }
            
            color = color_map.get(notification.priority, 0x2196F3)
            
            # Préparer le message Discord
            payload = {
                'username': self.username,
                'embeds': [{
                    'title': notification.title,
                    'description': notification.message,
                    'color': color,
                    'fields': [
                        {
                            'name': 'Priorité',
                            'value': notification.priority.value.upper(),
                            'inline': True
                        },
                        {
                            'name': 'Timestamp',
                            'value': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'inline': True
                        }
                    ],
                    'footer': {
                        'text': 'TradingAgents'
                    },
                    'timestamp': notification.timestamp.isoformat()
                }]
            }
            
            if self.avatar_url:
                payload['avatar_url'] = self.avatar_url
            
            # Envoyer à Discord
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info(f"🎮 Discord envoyé: {notification.title}")
                return True
            else:
                logger.error(f"❌ Discord échec: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur Discord: {e}")
            return False

class ConsoleNotifier:
    """Notificateur console (pour debug)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.use_colors = config.get('use_colors', True)
    
    def send(self, notification: Notification) -> bool:
        """Afficher une notification dans la console"""
        try:
            # Codes couleur ANSI
            colors = {
                NotificationPriority.LOW: '\033[92m',      # Vert
                NotificationPriority.NORMAL: '\033[94m',   # Bleu
                NotificationPriority.HIGH: '\033[93m',     # Jaune
                NotificationPriority.CRITICAL: '\033[91m'  # Rouge
            }
            
            reset_color = '\033[0m'
            
            if self.use_colors:
                color = colors.get(notification.priority, '\033[94m')
                print(f"{color}[{notification.priority.value.upper()}] {notification.title}{reset_color}")
                print(f"{color}{notification.message}{reset_color}")
            else:
                print(f"[{notification.priority.value.upper()}] {notification.title}")
                print(notification.message)
            
            print(f"Timestamp: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur console: {e}")
            return False

class NotificationSystem:
    """Système principal de notifications"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.config_file = config_file
        self.channels: Dict[NotificationChannel, NotificationConfig] = {}
        self.notifiers: Dict[NotificationChannel, Any] = {}
        self.notification_history: List[Notification] = []
        
        # Charger la configuration
        self.load_config()
        
        # Initialiser les notificateurs
        self.initialize_notifiers()
        
        logger.info("📢 NotificationSystem initialisé")
    
    def load_config(self):
        """Charger la configuration des notifications"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                for channel_name, channel_config in config_data.items():
                    try:
                        channel = NotificationChannel(channel_name)
                        min_priority = NotificationPriority(channel_config.get('min_priority', 'normal'))
                        
                        self.channels[channel] = NotificationConfig(
                            channel=channel,
                            enabled=channel_config.get('enabled', True),
                            config=channel_config.get('config', {}),
                            min_priority=min_priority
                        )
                    except ValueError:
                        logger.warning(f"⚠️ Canal inconnu ignoré: {channel_name}")
                
                logger.info("✅ Configuration notifications chargée")
            else:
                # Configuration par défaut
                self.channels[NotificationChannel.CONSOLE] = NotificationConfig(
                    channel=NotificationChannel.CONSOLE,
                    enabled=True,
                    config={'use_colors': True},
                    min_priority=NotificationPriority.LOW
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement config notifications: {e}")
    
    def save_config(self):
        """Sauvegarder la configuration des notifications"""
        try:
            config_data = {}
            for channel, config in self.channels.items():
                config_data[channel.value] = {
                    'enabled': config.enabled,
                    'config': config.config,
                    'min_priority': config.min_priority.value
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("✅ Configuration notifications sauvegardée")
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde config notifications: {e}")
    
    def initialize_notifiers(self):
        """Initialiser les notificateurs"""
        notifier_classes = {
            NotificationChannel.EMAIL: EmailNotifier,
            NotificationChannel.WEBHOOK: WebhookNotifier,
            NotificationChannel.SLACK: SlackNotifier,
            NotificationChannel.DISCORD: DiscordNotifier,
            NotificationChannel.CONSOLE: ConsoleNotifier
        }
        
        for channel, config in self.channels.items():
            if config.enabled and channel in notifier_classes:
                try:
                    self.notifiers[channel] = notifier_classes[channel](config.config)
                    logger.info(f"✅ Notificateur {channel.value} initialisé")
                except Exception as e:
                    logger.error(f"❌ Erreur init notificateur {channel.value}: {e}")
    
    def send_notification(self, title: str, message: str, 
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         channels: Optional[List[NotificationChannel]] = None,
                         data: Optional[Dict[str, Any]] = None) -> str:
        """Envoyer une notification"""
        notification_id = f"notif_{int(datetime.now().timestamp())}"
        
        # Déterminer les canaux à utiliser
        if channels is None:
            channels = [ch for ch, config in self.channels.items() 
                       if config.enabled and priority.value >= config.min_priority.value]
        
        notification = Notification(
            id=notification_id,
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            data=data
        )
        
        # Envoyer sur chaque canal
        for channel in channels:
            if channel in self.notifiers:
                try:
                    success = self.notifiers[channel].send(notification)
                    if success:
                        notification.sent_channels.append(channel)
                except Exception as e:
                    logger.error(f"❌ Erreur envoi {channel.value}: {e}")
        
        # Ajouter à l'historique
        self.notification_history.append(notification)
        
        # Garder seulement les 1000 dernières notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        logger.info(f"📢 Notification envoyée: {title} ({len(notification.sent_channels)} canaux)")
        return notification_id
    
    def configure_channel(self, channel: NotificationChannel, enabled: bool = True,
                         config: Optional[Dict[str, Any]] = None,
                         min_priority: NotificationPriority = NotificationPriority.NORMAL):
        """Configurer un canal de notification"""
        if config is None:
            config = {}
        
        self.channels[channel] = NotificationConfig(
            channel=channel,
            enabled=enabled,
            config=config,
            min_priority=min_priority
        )
        
        # Réinitialiser le notificateur
        if enabled:
            notifier_classes = {
                NotificationChannel.EMAIL: EmailNotifier,
                NotificationChannel.WEBHOOK: WebhookNotifier,
                NotificationChannel.SLACK: SlackNotifier,
                NotificationChannel.DISCORD: DiscordNotifier,
                NotificationChannel.CONSOLE: ConsoleNotifier
            }
            
            if channel in notifier_classes:
                try:
                    self.notifiers[channel] = notifier_classes[channel](config)
                    logger.info(f"✅ Canal {channel.value} configuré")
                except Exception as e:
                    logger.error(f"❌ Erreur config canal {channel.value}: {e}")
        else:
            if channel in self.notifiers:
                del self.notifiers[channel]
        
        self.save_config()
    
    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtenir l'historique des notifications"""
        notifications = sorted(self.notification_history, key=lambda n: n.timestamp, reverse=True)
        
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'priority': n.priority.value,
                'timestamp': n.timestamp.isoformat(),
                'sent_channels': [ch.value for ch in n.sent_channels]
            }
            for n in notifications[:limit]
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut du système de notifications"""
        return {
            'total_channels': len(self.channels),
            'active_channels': len([c for c in self.channels.values() if c.enabled]),
            'total_notifications': len(self.notification_history),
            'channels': {
                ch.value: {
                    'enabled': config.enabled,
                    'min_priority': config.min_priority.value,
                    'initialized': ch in self.notifiers
                }
                for ch, config in self.channels.items()
            }
        }

# Instance globale
notification_system = NotificationSystem()
