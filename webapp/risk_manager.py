"""
Gestionnaire de risques automatisé pour TradingAgents
Implémente stop-loss, take-profit, limites de position et sizing
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Niveaux de risque"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class StopLossType(Enum):
    """Types de stop-loss"""
    FIXED_PERCENTAGE = "fixed_percentage"
    TRAILING = "trailing"
    ATR_BASED = "atr_based"

@dataclass
class RiskParameters:
    """Paramètres de gestion des risques"""
    max_position_size: float = 0.05  # 5% du portefeuille max par position
    max_portfolio_risk: float = 0.20  # 20% du portefeuille max en risque
    stop_loss_percentage: float = 0.02  # 2% stop-loss par défaut
    take_profit_percentage: float = 0.06  # 6% take-profit par défaut
    max_daily_loss: float = 0.03  # 3% perte max par jour
    max_drawdown: float = 0.10  # 10% drawdown max
    risk_level: RiskLevel = RiskLevel.MODERATE
    use_trailing_stop: bool = True
    trailing_stop_percentage: float = 0.015  # 1.5% trailing stop
    max_positions: int = 10  # Nombre max de positions simultanées
    correlation_limit: float = 0.7  # Limite de corrélation entre positions

@dataclass
class RiskMetrics:
    """Métriques de risque en temps réel"""
    current_portfolio_value: float
    current_cash: float
    total_exposure: float
    daily_pnl: float
    unrealized_pnl: float
    max_drawdown_current: float
    risk_utilization: float  # % du risque utilisé
    position_count: int
    largest_position_percentage: float
    
@dataclass
class PositionRisk:
    """Risque d'une position individuelle"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    unrealized_pnl: float
    risk_amount: float
    position_size_percentage: float
    days_held: int

class RiskManager:
    """Gestionnaire principal des risques"""
    
    def __init__(self, config_file: str = "risk_config.json"):
        self.config_file = config_file
        self.parameters = RiskParameters()
        self.active_stops: Dict[str, Dict[str, Any]] = {}
        self.daily_start_value: Optional[float] = None
        self.daily_start_date: Optional[str] = None
        
        # Charger la configuration
        self.load_config()
        
        # Thread pour surveiller les risques
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        logger.info("🛡️ RiskManager initialisé")
    
    def load_config(self):
        """Charger la configuration des risques"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Mettre à jour les paramètres
                for key, value in config_data.items():
                    if hasattr(self.parameters, key):
                        if key == 'risk_level':
                            setattr(self.parameters, key, RiskLevel(value))
                        else:
                            setattr(self.parameters, key, value)
                
                logger.info("✅ Configuration des risques chargée")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la config: {e}")
    
    def save_config(self):
        """Sauvegarder la configuration des risques"""
        try:
            config_data = asdict(self.parameters)
            config_data['risk_level'] = config_data['risk_level'].value
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("✅ Configuration des risques sauvegardée")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def update_parameters(self, **kwargs):
        """Mettre à jour les paramètres de risque"""
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
        
        self.save_config()
        logger.info("✅ Paramètres de risque mis à jour")
    
    def validate_trade(self, symbol: str, quantity: float, price: float, 
                      side: str, portfolio_value: float, positions: List[Any]) -> Tuple[bool, str]:
        """Valider un trade avant exécution"""
        try:
            trade_value = quantity * price
            
            # 1. Vérifier la taille de position
            position_percentage = trade_value / portfolio_value
            if position_percentage > self.parameters.max_position_size:
                return False, f"Position trop importante: {position_percentage:.2%} > {self.parameters.max_position_size:.2%}"
            
            # 2. Vérifier le nombre max de positions
            if side.upper() == 'BUY' and len(positions) >= self.parameters.max_positions:
                return False, f"Nombre max de positions atteint: {len(positions)}"
            
            # 3. Vérifier l'exposition totale
            current_exposure = sum(pos.market_value for pos in positions if hasattr(pos, 'market_value'))
            new_exposure = current_exposure + (trade_value if side.upper() == 'BUY' else -trade_value)
            exposure_percentage = new_exposure / portfolio_value
            
            if exposure_percentage > self.parameters.max_portfolio_risk:
                return False, f"Exposition trop élevée: {exposure_percentage:.2%} > {self.parameters.max_portfolio_risk:.2%}"
            
            # 4. Vérifier les pertes journalières
            if not self._check_daily_loss_limit(portfolio_value):
                return False, "Limite de perte journalière atteinte"
            
            return True, "Trade validé"
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la validation: {e}")
            return False, f"Erreur de validation: {str(e)}"
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              portfolio_value: float, confidence: float = 0.5) -> float:
        """Calculer la taille de position optimale"""
        try:
            # Ajuster la taille basée sur la confiance et le niveau de risque
            base_risk = self.parameters.max_position_size
            
            # Ajustement basé sur le niveau de risque
            risk_multipliers = {
                RiskLevel.CONSERVATIVE: 0.5,
                RiskLevel.MODERATE: 1.0,
                RiskLevel.AGGRESSIVE: 1.5
            }
            
            risk_multiplier = risk_multipliers[self.parameters.risk_level]
            adjusted_risk = base_risk * risk_multiplier * confidence
            
            # Calculer la quantité
            position_value = portfolio_value * adjusted_risk
            quantity = position_value / entry_price
            
            # Arrondir à l'entier le plus proche (pour les actions)
            return max(1, int(quantity))
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul taille position: {e}")
            return 1
    
    def set_stop_loss(self, symbol: str, entry_price: float, quantity: float, 
                     side: str, stop_type: StopLossType = StopLossType.FIXED_PERCENTAGE) -> Optional[float]:
        """Définir un stop-loss pour une position"""
        try:
            if side.upper() == 'BUY':
                if stop_type == StopLossType.FIXED_PERCENTAGE:
                    stop_price = entry_price * (1 - self.parameters.stop_loss_percentage)
                elif stop_type == StopLossType.TRAILING:
                    stop_price = entry_price * (1 - self.parameters.trailing_stop_percentage)
                else:
                    stop_price = entry_price * (1 - self.parameters.stop_loss_percentage)
            else:  # SELL
                if stop_type == StopLossType.FIXED_PERCENTAGE:
                    stop_price = entry_price * (1 + self.parameters.stop_loss_percentage)
                elif stop_type == StopLossType.TRAILING:
                    stop_price = entry_price * (1 + self.parameters.trailing_stop_percentage)
                else:
                    stop_price = entry_price * (1 + self.parameters.stop_loss_percentage)
            
            # Enregistrer le stop-loss
            self.active_stops[symbol] = {
                'stop_price': stop_price,
                'entry_price': entry_price,
                'quantity': quantity,
                'side': side,
                'type': stop_type.value,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"🛑 Stop-loss défini pour {symbol}: ${stop_price:.2f}")
            return stop_price
            
        except Exception as e:
            logger.error(f"❌ Erreur définition stop-loss: {e}")
            return None
    
    def set_take_profit(self, symbol: str, entry_price: float, side: str) -> Optional[float]:
        """Définir un take-profit pour une position"""
        try:
            if side.upper() == 'BUY':
                take_profit_price = entry_price * (1 + self.parameters.take_profit_percentage)
            else:  # SELL
                take_profit_price = entry_price * (1 - self.parameters.take_profit_percentage)
            
            # Ajouter le take-profit aux stops actifs
            if symbol in self.active_stops:
                self.active_stops[symbol]['take_profit_price'] = take_profit_price
            else:
                self.active_stops[symbol] = {
                    'take_profit_price': take_profit_price,
                    'entry_price': entry_price,
                    'side': side,
                    'created_at': datetime.now().isoformat()
                }
            
            logger.info(f"🎯 Take-profit défini pour {symbol}: ${take_profit_price:.2f}")
            return take_profit_price
            
        except Exception as e:
            logger.error(f"❌ Erreur définition take-profit: {e}")
            return None
    
    def check_stop_triggers(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """Vérifier si des stops doivent être déclenchés"""
        triggered_stops = []
        
        for symbol, stop_data in self.active_stops.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            side = stop_data.get('side', 'BUY').upper()
            
            # Vérifier stop-loss
            if 'stop_price' in stop_data:
                stop_price = stop_data['stop_price']
                
                if side == 'BUY' and current_price <= stop_price:
                    triggered_stops.append({
                        'symbol': symbol,
                        'type': 'stop_loss',
                        'trigger_price': current_price,
                        'stop_price': stop_price,
                        'action': 'SELL'
                    })
                elif side == 'SELL' and current_price >= stop_price:
                    triggered_stops.append({
                        'symbol': symbol,
                        'type': 'stop_loss',
                        'trigger_price': current_price,
                        'stop_price': stop_price,
                        'action': 'BUY'
                    })
            
            # Vérifier take-profit
            if 'take_profit_price' in stop_data:
                take_profit_price = stop_data['take_profit_price']
                
                if side == 'BUY' and current_price >= take_profit_price:
                    triggered_stops.append({
                        'symbol': symbol,
                        'type': 'take_profit',
                        'trigger_price': current_price,
                        'take_profit_price': take_profit_price,
                        'action': 'SELL'
                    })
                elif side == 'SELL' and current_price <= take_profit_price:
                    triggered_stops.append({
                        'symbol': symbol,
                        'type': 'take_profit',
                        'trigger_price': current_price,
                        'take_profit_price': take_profit_price,
                        'action': 'BUY'
                    })
        
        return triggered_stops
    
    def calculate_risk_metrics(self, portfolio_value: float, positions: List[Any]) -> RiskMetrics:
        """Calculer les métriques de risque actuelles"""
        try:
            # Calculer l'exposition totale
            total_exposure = sum(getattr(pos, 'market_value', 0) for pos in positions)
            
            # Calculer le P&L non réalisé
            unrealized_pnl = sum(getattr(pos, 'unrealized_pnl', 0) for pos in positions)
            
            # Calculer le P&L journalier
            daily_pnl = self._calculate_daily_pnl(portfolio_value)
            
            # Calculer la plus grande position
            largest_position = 0
            if positions:
                largest_position = max(getattr(pos, 'market_value', 0) for pos in positions)
            largest_position_percentage = largest_position / portfolio_value if portfolio_value > 0 else 0
            
            # Calculer l'utilisation du risque
            risk_utilization = total_exposure / (portfolio_value * self.parameters.max_portfolio_risk) if portfolio_value > 0 else 0
            
            return RiskMetrics(
                current_portfolio_value=portfolio_value,
                current_cash=portfolio_value - total_exposure,
                total_exposure=total_exposure,
                daily_pnl=daily_pnl,
                unrealized_pnl=unrealized_pnl,
                max_drawdown_current=0.0,  # À implémenter
                risk_utilization=risk_utilization,
                position_count=len(positions),
                largest_position_percentage=largest_position_percentage
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul métriques: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def _check_daily_loss_limit(self, current_portfolio_value: float) -> bool:
        """Vérifier la limite de perte journalière"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Initialiser la valeur de début de journée si nécessaire
            if self.daily_start_date != today:
                self.daily_start_value = current_portfolio_value
                self.daily_start_date = today
                return True
            
            if self.daily_start_value is None:
                return True
            
            # Calculer la perte journalière
            daily_loss = (self.daily_start_value - current_portfolio_value) / self.daily_start_value
            
            return daily_loss <= self.parameters.max_daily_loss
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification perte journalière: {e}")
            return True
    
    def _calculate_daily_pnl(self, current_portfolio_value: float) -> float:
        """Calculer le P&L journalier"""
        if self.daily_start_value is None:
            return 0.0
        
        return current_portfolio_value - self.daily_start_value
    
    def start_monitoring(self):
        """Démarrer la surveillance des risques"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._risk_monitor_worker, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 Surveillance des risques démarrée")
    
    def stop_monitoring(self):
        """Arrêter la surveillance des risques"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("🔍 Surveillance des risques arrêtée")
    
    def _risk_monitor_worker(self):
        """Worker de surveillance des risques"""
        while self.monitoring_active:
            try:
                # Ici, on vérifierait les risques en temps réel
                # Pour l'instant, on simule
                time.sleep(30)  # Vérifier toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la surveillance des risques: {e}")
                break
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé des risques"""
        return {
            'parameters': asdict(self.parameters),
            'active_stops_count': len(self.active_stops),
            'monitoring_active': self.monitoring_active,
            'daily_start_value': self.daily_start_value,
            'daily_start_date': self.daily_start_date
        }

# Instance globale
risk_manager = RiskManager()
