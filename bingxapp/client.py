"""
Client BingX pour les opérations de trading
"""

import hashlib
import hmac
import time
import json
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
import logging

from .config import BingXConfig


class BingXClient:
    """Client pour l'API BingX"""
    
    def __init__(self, config: BingXConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
        
        # Configuration du logging
        self.logger = logging.getLogger(__name__)
        
    def _generate_signature(self, query_string: str) -> str:
        """Génère la signature HMAC pour l'authentification"""
        return hmac.new(
            self.config.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_timestamp(self) -> int:
        """Retourne le timestamp actuel en millisecondes"""
        return int(time.time() * 1000)
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     signed: bool = False) -> Dict[str, Any]:
        """Effectue une requête à l'API BingX"""

        if params is None:
            params = {}

        # Ajouter le timestamp pour les requêtes signées
        if signed:
            params['timestamp'] = self._get_timestamp()

        # Construire l'URL
        url = f"{self.config.api_url}{endpoint}"

        # Préparer les headers
        headers = {
            'X-BX-APIKEY': self.config.api_key,
        }

        # Signer la requête si nécessaire
        if signed:
            query_string = urlencode(sorted(params.items()))
            signature = self._generate_signature(query_string)
            params['signature'] = signature

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                if signed:
                    # Pour les requêtes POST signées, utiliser form data
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    response = self.session.post(url, data=params, headers=headers)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = self.session.post(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la requête à {url}: {e}")
            self.logger.error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            self.logger.error(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur de décodage JSON: {e}")
            raise
    
    def get_server_time(self) -> Dict[str, Any]:
        """Récupère l'heure du serveur"""
        return self._make_request('GET', '/openApi/swap/v2/server/time')
    
    def get_account_info(self) -> Dict[str, Any]:
        """Récupère les informations du compte"""
        return self._make_request('GET', '/openApi/swap/v2/user/balance', signed=True)
    
    def get_positions(self) -> Dict[str, Any]:
        """Récupère les positions ouvertes"""
        return self._make_request('GET', '/openApi/swap/v2/user/positions', signed=True)
    
    def get_symbol_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les informations sur les symboles"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/openApi/swap/v2/quote/contracts', params=params)
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Récupère le ticker pour un symbole"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/openApi/swap/v2/quote/ticker', params=params)
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Récupère le carnet d'ordres"""
        params = {'symbol': symbol, 'limit': limit}
        return self._make_request('GET', '/openApi/swap/v2/quote/depth', params=params)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """Place un ordre"""
        params = {
            'symbol': symbol,
            'side': side.upper(),  # BUY ou SELL
            'type': order_type.upper(),  # MARKET, LIMIT, etc.
            'quantity': str(quantity)
        }
        
        if price is not None:
            params['price'] = str(price)
            
        # Ajouter d'autres paramètres optionnels
        for key, value in kwargs.items():
            if value is not None:
                params[key] = str(value)
                
        return self._make_request('POST', '/openApi/swap/v2/trade/order', params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Annule un ordre"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/openApi/swap/v2/trade/order', params, signed=True)
    
    def get_orders(self, symbol: str, status: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les ordres"""
        params = {'symbol': symbol}
        if status:
            params['status'] = status
        return self._make_request('GET', '/openApi/swap/v2/trade/openOrders', params, signed=True)
    
    def test_connectivity(self) -> bool:
        """Teste la connectivité avec l'API"""
        try:
            result = self.get_server_time()
            self.logger.info(f"Réponse du serveur: {result}")
            return 'data' in result and 'serverTime' in result.get('data', {})
        except Exception as e:
            self.logger.error(f"Test de connectivité échoué: {e}")
            return False
