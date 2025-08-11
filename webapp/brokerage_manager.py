"""
Gestionnaire d'intégration avec les APIs de courtage
Support pour Alpaca, Interactive Brokers, TD Ameritrade, etc.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokerType(Enum):
    """Types de courtiers supportés"""
    ALPACA = "alpaca"
    INTERACTIVE_BROKERS = "interactive_brokers"
    TD_AMERITRADE = "td_ameritrade"
    PAPER_TRADING = "paper_trading"

class OrderType(Enum):
    """Types d'ordres"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    """Côtés d'ordre"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Statuts d'ordre"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Position:
    """Position de trading"""
    symbol: str
    quantity: float
    avg_price: float
    market_value: float
    unrealized_pnl: float
    side: str  # "long" ou "short"
    
@dataclass
class Order:
    """Ordre de trading"""
    id: str
    symbol: str
    quantity: float
    side: OrderSide
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BrokerageInterface(ABC):
    """Interface abstraite pour les courtiers"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Se connecter au courtier"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Obtenir les informations du compte"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Obtenir les positions actuelles"""
        pass
    
    @abstractmethod
    def get_buying_power(self) -> float:
        """Obtenir le pouvoir d'achat"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, quantity: float, side: OrderSide, 
                   order_type: OrderType = OrderType.MARKET, 
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Order:
        """Placer un ordre"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Annuler un ordre"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtenir le statut d'un ordre"""
        pass

class AlpacaBroker(BrokerageInterface):
    """Intégration avec Alpaca Markets"""
    
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.client = None
        
    def connect(self) -> bool:
        """Se connecter à Alpaca"""
        try:
            # Ici, nous utiliserions la bibliothèque alpaca-trade-api
            # Pour l'instant, simulons la connexion
            logger.info(f"🔗 Connexion à Alpaca ({'Paper' if self.paper else 'Live'})...")
            
            # Simulation de connexion réussie
            self.client = {"connected": True, "account": "simulated"}
            logger.info("✅ Connexion Alpaca réussie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Alpaca: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Obtenir les informations du compte Alpaca"""
        if not self.client:
            raise Exception("Non connecté à Alpaca")
        
        # Simulation des informations de compte
        return {
            "account_number": "ALPACA123456",
            "buying_power": 100000.0,
            "cash": 50000.0,
            "portfolio_value": 150000.0,
            "day_trade_count": 0,
            "pattern_day_trader": False
        }
    
    def get_positions(self) -> List[Position]:
        """Obtenir les positions Alpaca"""
        if not self.client:
            raise Exception("Non connecté à Alpaca")
        
        # Simulation de positions
        return [
            Position("SPY", 100, 450.0, 45000.0, 500.0, "long"),
            Position("QQQ", 50, 380.0, 19000.0, -200.0, "long")
        ]
    
    def get_buying_power(self) -> float:
        """Obtenir le pouvoir d'achat Alpaca"""
        account_info = self.get_account_info()
        return account_info["buying_power"]
    
    def place_order(self, symbol: str, quantity: float, side: OrderSide, 
                   order_type: OrderType = OrderType.MARKET, 
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Order:
        """Placer un ordre Alpaca"""
        if not self.client:
            raise Exception("Non connecté à Alpaca")
        
        # Simulation de placement d'ordre
        order_id = f"alpaca_{int(datetime.now().timestamp())}"
        
        order = Order(
            id=order_id,
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            price=price,
            stop_price=stop_price
        )
        
        logger.info(f"📋 Ordre placé: {side.value} {quantity} {symbol} ({order_type.value})")
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Annuler un ordre Alpaca"""
        logger.info(f"❌ Ordre annulé: {order_id}")
        return True
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtenir le statut d'un ordre Alpaca"""
        # Simulation - en réalité, on interrogerait l'API
        return OrderStatus.FILLED

class PaperTradingBroker(BrokerageInterface):
    """Courtier de trading simulé pour les tests"""
    
    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.connected = False
        
    def connect(self) -> bool:
        """Se connecter au trading simulé"""
        self.connected = True
        logger.info("✅ Trading simulé activé")
        return True
    
    def get_account_info(self) -> Dict[str, Any]:
        """Obtenir les informations du compte simulé"""
        portfolio_value = self.cash + sum(pos.market_value for pos in self.positions.values())
        
        return {
            "account_number": "PAPER_TRADING",
            "buying_power": self.cash,
            "cash": self.cash,
            "portfolio_value": portfolio_value,
            "day_trade_count": 0,
            "pattern_day_trader": False
        }
    
    def get_positions(self) -> List[Position]:
        """Obtenir les positions simulées"""
        return list(self.positions.values())
    
    def get_buying_power(self) -> float:
        """Obtenir le pouvoir d'achat simulé"""
        return self.cash
    
    def place_order(self, symbol: str, quantity: float, side: OrderSide, 
                   order_type: OrderType = OrderType.MARKET, 
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Order:
        """Placer un ordre simulé"""
        order_id = f"paper_{int(datetime.now().timestamp())}"
        
        # Simuler un prix de marché (en réalité, on utiliserait des données réelles)
        market_price = price or self._get_simulated_price(symbol)
        
        order = Order(
            id=order_id,
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            price=price,
            stop_price=stop_price,
            status=OrderStatus.FILLED,
            filled_at=datetime.now(),
            filled_price=market_price
        )
        
        # Exécuter l'ordre immédiatement (simulation)
        self._execute_order(order)
        self.orders[order_id] = order
        
        logger.info(f"📋 Ordre simulé exécuté: {side.value} {quantity} {symbol} @ ${market_price:.2f}")
        return order
    
    def _get_simulated_price(self, symbol: str) -> float:
        """Obtenir un prix simulé pour un symbole"""
        # Prix simulés pour les tests
        prices = {
            "SPY": 450.0,
            "QQQ": 380.0,
            "AAPL": 175.0,
            "MSFT": 340.0,
            "TSLA": 250.0
        }
        return prices.get(symbol, 100.0)
    
    def _execute_order(self, order: Order):
        """Exécuter un ordre simulé"""
        total_cost = order.quantity * order.filled_price
        
        if order.side == OrderSide.BUY:
            if self.cash >= total_cost:
                self.cash -= total_cost
                
                # Ajouter ou mettre à jour la position
                if order.symbol in self.positions:
                    pos = self.positions[order.symbol]
                    new_quantity = pos.quantity + order.quantity
                    new_avg_price = ((pos.quantity * pos.avg_price) + total_cost) / new_quantity
                    pos.quantity = new_quantity
                    pos.avg_price = new_avg_price
                    pos.market_value = new_quantity * order.filled_price
                else:
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=order.quantity,
                        avg_price=order.filled_price,
                        market_value=total_cost,
                        unrealized_pnl=0.0,
                        side="long"
                    )
            else:
                raise Exception("Fonds insuffisants")
                
        elif order.side == OrderSide.SELL:
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                if pos.quantity >= order.quantity:
                    self.cash += total_cost
                    pos.quantity -= order.quantity
                    
                    if pos.quantity == 0:
                        del self.positions[order.symbol]
                    else:
                        pos.market_value = pos.quantity * order.filled_price
                else:
                    raise Exception("Position insuffisante")
            else:
                raise Exception("Aucune position à vendre")
    
    def cancel_order(self, order_id: str) -> bool:
        """Annuler un ordre simulé"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            return True
        return False
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtenir le statut d'un ordre simulé"""
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.REJECTED

class BrokerageManager:
    """Gestionnaire principal des courtiers"""
    
    def __init__(self):
        self.brokers: Dict[str, BrokerageInterface] = {}
        self.active_broker: Optional[str] = None
        
    def add_broker(self, name: str, broker: BrokerageInterface) -> bool:
        """Ajouter un courtier"""
        try:
            if broker.connect():
                self.brokers[name] = broker
                if self.active_broker is None:
                    self.active_broker = name
                logger.info(f"✅ Courtier ajouté: {name}")
                return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du courtier {name}: {e}")
        return False
    
    def set_active_broker(self, name: str) -> bool:
        """Définir le courtier actif"""
        if name in self.brokers:
            self.active_broker = name
            logger.info(f"🎯 Courtier actif: {name}")
            return True
        return False
    
    def get_active_broker(self) -> Optional[BrokerageInterface]:
        """Obtenir le courtier actif"""
        if self.active_broker and self.active_broker in self.brokers:
            return self.brokers[self.active_broker]
        return None
    
    def execute_trade_signal(self, signal: Dict[str, Any]) -> Optional[Order]:
        """Exécuter un signal de trading"""
        broker = self.get_active_broker()
        if not broker:
            logger.error("❌ Aucun courtier actif")
            return None
        
        try:
            symbol = signal['ticker']
            decision = signal['decision'].upper()
            
            # Déterminer la quantité basée sur la gestion des risques
            quantity = self._calculate_position_size(broker, symbol, signal)
            
            if decision == 'BUY':
                return broker.place_order(symbol, quantity, OrderSide.BUY)
            elif decision == 'SELL':
                return broker.place_order(symbol, quantity, OrderSide.SELL)
            else:  # HOLD
                logger.info(f"📊 Signal HOLD pour {symbol} - Aucune action")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution du signal: {e}")
            return None
    
    def _calculate_position_size(self, broker: BrokerageInterface, symbol: str, signal: Dict[str, Any]) -> float:
        """Calculer la taille de position basée sur la gestion des risques"""
        # Logique de base - à améliorer avec des règles de gestion des risques
        buying_power = broker.get_buying_power()
        risk_percentage = signal.get('risk_percentage', 0.02)  # 2% par défaut
        
        # Utiliser 2% du capital par position
        position_value = buying_power * risk_percentage
        
        # Simuler un prix (en réalité, on obtiendrait le prix du marché)
        price = 100.0  # À remplacer par le prix réel
        
        quantity = position_value / price
        return max(1, int(quantity))  # Au moins 1 action

# Instance globale
brokerage_manager = BrokerageManager()

# Ajouter le courtier de trading simulé par défaut
paper_broker = PaperTradingBroker()
brokerage_manager.add_broker("paper_trading", paper_broker)
