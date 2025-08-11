"""
Système de surveillance en temps réel pour TradingAgents
Monitoring des positions, alertes et ajustements automatiques
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import websocket
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MonitoringStatus(Enum):
    """Statuts de surveillance"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class Alert:
    """Alerte de surveillance"""
    id: str
    level: AlertLevel
    title: str
    message: str
    symbol: Optional[str] = None
    timestamp: datetime = None
    acknowledged: bool = False
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class MarketData:
    """Données de marché en temps réel"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None

@dataclass
class PositionMonitor:
    """Surveillance d'une position"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    last_update: datetime = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()

class MarketDataProvider:
    """Fournisseur de données de marché"""
    
    def __init__(self, provider_type: str = "finnhub"):
        self.provider_type = provider_type
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
        self.websocket_url = "wss://ws.finnhub.io"
        self.ws = None
        self.subscribed_symbols = set()
        
    def get_real_time_price(self, symbol: str) -> Optional[float]:
        """Obtenir le prix en temps réel d'un symbole"""
        try:
            if self.provider_type == "finnhub":
                url = f"{self.base_url}/quote"
                params = {"symbol": symbol, "token": self.api_key}
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('c')  # Current price
            
            # Fallback: prix simulé
            return self._get_simulated_price(symbol)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération prix {symbol}: {e}")
            return self._get_simulated_price(symbol)
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Obtenir les données de marché complètes"""
        try:
            if self.provider_type == "finnhub":
                url = f"{self.base_url}/quote"
                params = {"symbol": symbol, "token": self.api_key}
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    return MarketData(
                        symbol=symbol,
                        price=data.get('c', 0),
                        change=data.get('d', 0),
                        change_percent=data.get('dp', 0),
                        volume=0,  # Finnhub ne fournit pas le volume dans cette API
                        timestamp=datetime.now(),
                        high_24h=data.get('h', 0),
                        low_24h=data.get('l', 0)
                    )
            
            # Fallback: données simulées
            return self._get_simulated_market_data(symbol)
            
        except Exception as e:
            logger.error(f"❌ Erreur données marché {symbol}: {e}")
            return self._get_simulated_market_data(symbol)
    
    def _get_simulated_price(self, symbol: str) -> float:
        """Prix simulé pour les tests"""
        import random
        base_prices = {
            "SPY": 450.0,
            "QQQ": 380.0,
            "AAPL": 175.0,
            "MSFT": 340.0,
            "TSLA": 250.0,
            "NVDA": 500.0,
            "GOOGL": 140.0,
            "AMZN": 150.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        # Ajouter une variation aléatoire de ±2%
        variation = random.uniform(-0.02, 0.02)
        return base_price * (1 + variation)
    
    def _get_simulated_market_data(self, symbol: str) -> MarketData:
        """Données de marché simulées"""
        import random
        
        current_price = self._get_simulated_price(symbol)
        change = random.uniform(-5.0, 5.0)
        change_percent = (change / current_price) * 100
        
        return MarketData(
            symbol=symbol,
            price=current_price,
            change=change,
            change_percent=change_percent,
            volume=random.randint(1000000, 10000000),
            timestamp=datetime.now(),
            high_24h=current_price * 1.02,
            low_24h=current_price * 0.98
        )

class MonitoringSystem:
    """Système principal de surveillance"""
    
    def __init__(self):
        self.status = MonitoringStatus.STOPPED
        self.market_data_provider = MarketDataProvider()
        
        # Surveillance
        self.monitored_positions: Dict[str, PositionMonitor] = {}
        self.alerts: List[Alert] = []
        self.market_data_cache: Dict[str, MarketData] = {}
        
        # Threads de surveillance
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks
        self.on_alert: Optional[Callable] = None
        self.on_stop_trigger: Optional[Callable] = None
        self.on_position_update: Optional[Callable] = None
        
        # Configuration
        self.update_interval = 30  # secondes
        self.price_change_threshold = 0.05  # 5% pour alertes
        
        logger.info("📊 MonitoringSystem initialisé")
    
    def add_position_monitor(self, symbol: str, entry_price: float, quantity: float,
                           stop_loss: Optional[float] = None, take_profit: Optional[float] = None):
        """Ajouter une position à surveiller"""
        current_price = self.market_data_provider.get_real_time_price(symbol) or entry_price
        
        unrealized_pnl = (current_price - entry_price) * quantity
        unrealized_pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        monitor = PositionMonitor(
            symbol=symbol,
            entry_price=entry_price,
            current_price=current_price,
            quantity=quantity,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_percent=unrealized_pnl_percent,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        self.monitored_positions[symbol] = monitor
        logger.info(f"📈 Position ajoutée à la surveillance: {symbol}")
    
    def remove_position_monitor(self, symbol: str):
        """Retirer une position de la surveillance"""
        if symbol in self.monitored_positions:
            del self.monitored_positions[symbol]
            logger.info(f"📉 Position retirée de la surveillance: {symbol}")
    
    def update_position_stops(self, symbol: str, stop_loss: Optional[float] = None, 
                            take_profit: Optional[float] = None):
        """Mettre à jour les stops d'une position"""
        if symbol in self.monitored_positions:
            monitor = self.monitored_positions[symbol]
            if stop_loss is not None:
                monitor.stop_loss = stop_loss
            if take_profit is not None:
                monitor.take_profit = take_profit
            
            logger.info(f"🎯 Stops mis à jour pour {symbol}")
    
    def start_monitoring(self):
        """Démarrer la surveillance"""
        if self.status == MonitoringStatus.RUNNING:
            logger.warning("⚠️ La surveillance est déjà active")
            return
        
        self.status = MonitoringStatus.RUNNING
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 Surveillance démarrée")
    
    def stop_monitoring(self):
        """Arrêter la surveillance"""
        if self.status != MonitoringStatus.RUNNING:
            return
        
        self.status = MonitoringStatus.STOPPED
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("🛑 Surveillance arrêtée")
    
    def pause_monitoring(self):
        """Mettre en pause la surveillance"""
        if self.status == MonitoringStatus.RUNNING:
            self.status = MonitoringStatus.PAUSED
            logger.info("⏸️ Surveillance mise en pause")
    
    def resume_monitoring(self):
        """Reprendre la surveillance"""
        if self.status == MonitoringStatus.PAUSED:
            self.status = MonitoringStatus.RUNNING
            logger.info("▶️ Surveillance reprise")
    
    def _monitoring_worker(self):
        """Worker principal de surveillance"""
        logger.info("🔄 Worker de surveillance démarré")
        
        while not self.stop_event.is_set():
            try:
                if self.status == MonitoringStatus.RUNNING:
                    self._update_all_positions()
                    self._check_alerts()
                    self._check_stop_triggers()
                
                # Attendre avant la prochaine mise à jour
                self.stop_event.wait(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans le worker de surveillance: {e}")
                self.status = MonitoringStatus.ERROR
                break
        
        logger.info("🔄 Worker de surveillance arrêté")
    
    def _update_all_positions(self):
        """Mettre à jour toutes les positions surveillées"""
        for symbol, monitor in self.monitored_positions.items():
            try:
                # Obtenir le prix actuel
                current_price = self.market_data_provider.get_real_time_price(symbol)
                if current_price is None:
                    continue
                
                # Mettre à jour les données
                old_price = monitor.current_price
                monitor.current_price = current_price
                monitor.unrealized_pnl = (current_price - monitor.entry_price) * monitor.quantity
                monitor.unrealized_pnl_percent = ((current_price - monitor.entry_price) / monitor.entry_price) * 100
                monitor.last_update = datetime.now()
                
                # Vérifier les changements significatifs
                if old_price > 0:
                    price_change_percent = abs((current_price - old_price) / old_price)
                    if price_change_percent >= self.price_change_threshold:
                        self._create_alert(
                            AlertLevel.INFO,
                            f"Mouvement de prix significatif: {symbol}",
                            f"{symbol}: {old_price:.2f} → {current_price:.2f} ({price_change_percent:.1%})",
                            symbol
                        )
                
                # Callback pour mise à jour de position
                if self.on_position_update:
                    self.on_position_update(symbol, monitor)
                
            except Exception as e:
                logger.error(f"❌ Erreur mise à jour position {symbol}: {e}")
    
    def _check_alerts(self):
        """Vérifier les conditions d'alerte"""
        for symbol, monitor in self.monitored_positions.items():
            try:
                # Alerte de perte importante
                if monitor.unrealized_pnl_percent <= -10:
                    self._create_alert(
                        AlertLevel.WARNING,
                        f"Perte importante: {symbol}",
                        f"{symbol}: Perte de {monitor.unrealized_pnl_percent:.1f}% (${monitor.unrealized_pnl:.2f})",
                        symbol
                    )
                
                # Alerte de gain important
                elif monitor.unrealized_pnl_percent >= 20:
                    self._create_alert(
                        AlertLevel.INFO,
                        f"Gain important: {symbol}",
                        f"{symbol}: Gain de {monitor.unrealized_pnl_percent:.1f}% (${monitor.unrealized_pnl:.2f})",
                        symbol
                    )
                
            except Exception as e:
                logger.error(f"❌ Erreur vérification alertes {symbol}: {e}")
    
    def _check_stop_triggers(self):
        """Vérifier les déclenchements de stops"""
        for symbol, monitor in self.monitored_positions.items():
            try:
                current_price = monitor.current_price
                
                # Vérifier stop-loss
                if monitor.stop_loss and current_price <= monitor.stop_loss:
                    self._create_alert(
                        AlertLevel.CRITICAL,
                        f"Stop-loss déclenché: {symbol}",
                        f"{symbol}: Prix {current_price:.2f} ≤ Stop-loss {monitor.stop_loss:.2f}",
                        symbol
                    )
                    
                    if self.on_stop_trigger:
                        self.on_stop_trigger(symbol, 'stop_loss', current_price, monitor.stop_loss)
                
                # Vérifier take-profit
                elif monitor.take_profit and current_price >= monitor.take_profit:
                    self._create_alert(
                        AlertLevel.INFO,
                        f"Take-profit déclenché: {symbol}",
                        f"{symbol}: Prix {current_price:.2f} ≥ Take-profit {monitor.take_profit:.2f}",
                        symbol
                    )
                    
                    if self.on_stop_trigger:
                        self.on_stop_trigger(symbol, 'take_profit', current_price, monitor.take_profit)
                
            except Exception as e:
                logger.error(f"❌ Erreur vérification stops {symbol}: {e}")
    
    def _create_alert(self, level: AlertLevel, title: str, message: str, symbol: Optional[str] = None):
        """Créer une nouvelle alerte"""
        alert_id = f"alert_{int(datetime.now().timestamp())}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            symbol=symbol
        )
        
        self.alerts.append(alert)
        
        # Garder seulement les 100 dernières alertes
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.info(f"🚨 {level.value.upper()}: {title}")
        
        # Callback pour alerte
        if self.on_alert:
            self.on_alert(alert)
    
    def get_alerts(self, level: Optional[AlertLevel] = None, symbol: Optional[str] = None, 
                  limit: int = 50) -> List[Alert]:
        """Obtenir les alertes"""
        alerts = self.alerts
        
        # Filtrer par niveau
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # Filtrer par symbole
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        
        # Trier par timestamp décroissant et limiter
        alerts = sorted(alerts, key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_id: str):
        """Acquitter une alerte"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"✅ Alerte acquittée: {alert_id}")
                break
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Obtenir le statut de surveillance"""
        return {
            'status': self.status.value,
            'monitored_positions': len(self.monitored_positions),
            'total_alerts': len(self.alerts),
            'unacknowledged_alerts': len([a for a in self.alerts if not a.acknowledged]),
            'update_interval': self.update_interval,
            'last_update': datetime.now().isoformat()
        }
    
    def get_position_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé des positions surveillées"""
        if not self.monitored_positions:
            return {'total_positions': 0, 'total_pnl': 0, 'positions': []}
        
        total_pnl = sum(monitor.unrealized_pnl for monitor in self.monitored_positions.values())
        
        positions = []
        for symbol, monitor in self.monitored_positions.items():
            positions.append({
                'symbol': symbol,
                'current_price': monitor.current_price,
                'entry_price': monitor.entry_price,
                'quantity': monitor.quantity,
                'unrealized_pnl': monitor.unrealized_pnl,
                'unrealized_pnl_percent': monitor.unrealized_pnl_percent,
                'last_update': monitor.last_update.isoformat()
            })
        
        return {
            'total_positions': len(self.monitored_positions),
            'total_pnl': total_pnl,
            'positions': positions
        }

# Instance globale
monitoring_system = MonitoringSystem()
