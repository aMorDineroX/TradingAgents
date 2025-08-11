"""
Bot de trading pour BingX
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .client import BingXClient
from .config import BingXConfig


class TradingBot:
    """Bot de trading automatisé pour BingX"""
    
    def __init__(self, config: BingXConfig):
        self.config = config
        self.client = BingXClient(config)
        self.is_running = False
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Statistiques
        self.stats = {
            'orders_placed': 0,
            'orders_filled': 0,
            'total_pnl': 0.0,
            'start_time': None
        }
    
    def initialize(self) -> bool:
        """Initialise le bot et vérifie la connectivité"""
        self.logger.info("Initialisation du bot de trading BingX...")
        
        # Test de connectivité
        if not self.client.test_connectivity():
            self.logger.error("Impossible de se connecter à l'API BingX")
            return False
            
        # Vérification du compte
        try:
            account_info = self.client.get_account_info()
            self.logger.info(f"Compte connecté avec succès")
            self.logger.info(f"Informations du compte: {json.dumps(account_info, indent=2)}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du compte: {e}")
            return False
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Récupère le solde du compte"""
        try:
            return self.client.get_account_info()
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du solde: {e}")
            return {}
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Récupère les données de marché pour un symbole"""
        try:
            ticker = self.client.get_ticker(symbol)
            orderbook = self.client.get_orderbook(symbol, limit=10)
            
            return {
                'ticker': ticker,
                'orderbook': orderbook,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des données de marché: {e}")
            return {}
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict[str, Any]]:
        """Place un ordre au marché"""
        try:
            self.logger.info(f"Placement d'un ordre {side} de {quantity} {symbol}")
            
            result = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=quantity
            )
            
            self.stats['orders_placed'] += 1
            self.logger.info(f"Ordre placé avec succès: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du placement de l'ordre: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict[str, Any]]:
        """Place un ordre à cours limité"""
        try:
            self.logger.info(f"Placement d'un ordre limite {side} de {quantity} {symbol} à {price}")
            
            result = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                quantity=quantity,
                price=price
            )
            
            self.stats['orders_placed'] += 1
            self.logger.info(f"Ordre limite placé avec succès: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du placement de l'ordre limite: {e}")
            return None
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """Annule tous les ordres ouverts pour un symbole"""
        try:
            orders = self.client.get_orders(symbol)
            
            if 'data' in orders and orders['data']:
                for order in orders['data']:
                    order_id = order.get('orderId')
                    if order_id:
                        self.client.cancel_order(symbol, order_id)
                        self.logger.info(f"Ordre {order_id} annulé")
                        
                return True
            else:
                self.logger.info("Aucun ordre ouvert à annuler")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annulation des ordres: {e}")
            return False
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Récupère les positions ouvertes"""
        try:
            positions = self.client.get_positions()
            return positions.get('data', [])
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des positions: {e}")
            return []
    
    def close_position(self, symbol: str, quantity: float) -> Optional[Dict[str, Any]]:
        """Ferme une position"""
        try:
            positions = self.get_positions()
            
            for position in positions:
                if position.get('symbol') == symbol:
                    side = 'SELL' if float(position.get('positionAmt', 0)) > 0 else 'BUY'
                    
                    return self.place_market_order(symbol, side, quantity)
                    
            self.logger.warning(f"Aucune position trouvée pour {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de position: {e}")
            return None
    
    def start_monitoring(self, symbols: List[str], interval: int = 60):
        """Démarre le monitoring des symboles"""
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        self.logger.info(f"Démarrage du monitoring pour {symbols}")
        
        try:
            while self.is_running:
                for symbol in symbols:
                    market_data = self.get_market_data(symbol)
                    if market_data:
                        self.logger.info(f"Données de marché pour {symbol}: {market_data['ticker']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Arrêt du monitoring demandé par l'utilisateur")
        except Exception as e:
            self.logger.error(f"Erreur dans le monitoring: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Arrête le bot"""
        self.is_running = False
        self.logger.info("Bot arrêté")
        
        # Affichage des statistiques
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            self.logger.info(f"Statistiques de session:")
            self.logger.info(f"  - Durée: {duration}")
            self.logger.info(f"  - Ordres placés: {self.stats['orders_placed']}")
            self.logger.info(f"  - Ordres exécutés: {self.stats['orders_filled']}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du bot"""
        return self.stats.copy()
