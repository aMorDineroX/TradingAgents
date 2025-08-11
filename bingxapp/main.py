"""
Application principale BingX
"""

import argparse
import json
import sys
from typing import List, Optional

from .config import BingXConfig
from .trading_bot import TradingBot


def test_connection():
    """Teste la connexion à l'API BingX"""
    print("🔄 Test de connexion à BingX...")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if bot.initialize():
        print("✅ Connexion réussie à BingX!")
        
        # Afficher les informations du compte
        balance = bot.get_account_balance()
        if balance:
            print("\n💰 Informations du compte:")
            print(json.dumps(balance, indent=2, ensure_ascii=False))
        
        return True
    else:
        print("❌ Échec de la connexion à BingX")
        return False


def get_market_data(symbol: str):
    """Récupère les données de marché pour un symbole"""
    print(f"📊 Récupération des données de marché pour {symbol}...")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible de se connecter à BingX")
        return
    
    market_data = bot.get_market_data(symbol)
    if market_data:
        print(f"\n📈 Données de marché pour {symbol}:")
        print(json.dumps(market_data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Impossible de récupérer les données pour {symbol}")


def show_positions():
    """Affiche les positions ouvertes"""
    print("📋 Récupération des positions ouvertes...")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible de se connecter à BingX")
        return
    
    positions = bot.get_positions()
    if positions:
        print(f"\n🎯 Positions ouvertes ({len(positions)}):")
        for i, position in enumerate(positions, 1):
            print(f"\n{i}. {position.get('symbol', 'N/A')}")
            print(f"   Quantité: {position.get('positionAmt', 'N/A')}")
            print(f"   Prix d'entrée: {position.get('entryPrice', 'N/A')}")
            print(f"   PnL: {position.get('unrealizedProfit', 'N/A')}")
    else:
        print("📭 Aucune position ouverte")


def place_order(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None):
    """Place un ordre"""
    print(f"📝 Placement d'un ordre {order_type} {side} de {quantity} {symbol}")
    if price:
        print(f"   Prix: {price}")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible de se connecter à BingX")
        return
    
    if order_type.upper() == 'MARKET':
        result = bot.place_market_order(symbol, side, quantity)
    elif order_type.upper() == 'LIMIT':
        if price is None:
            print("❌ Le prix est requis pour un ordre limite")
            return
        result = bot.place_limit_order(symbol, side, quantity, price)
    else:
        print(f"❌ Type d'ordre non supporté: {order_type}")
        return
    
    if result:
        print("✅ Ordre placé avec succès!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Échec du placement de l'ordre")


def monitor_symbols(symbols: List[str], interval: int = 60):
    """Démarre le monitoring des symboles"""
    print(f"👀 Démarrage du monitoring pour: {', '.join(symbols)}")
    print(f"⏱️  Intervalle: {interval} secondes")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible de se connecter à BingX")
        return
    
    try:
        bot.start_monitoring(symbols, interval)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du monitoring...")
        bot.stop()


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Application BingX Trading")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande test
    subparsers.add_parser('test', help='Teste la connexion à BingX')
    
    # Commande market
    market_parser = subparsers.add_parser('market', help='Récupère les données de marché')
    market_parser.add_argument('symbol', help='Symbole à analyser (ex: BTC-USDT)')
    
    # Commande positions
    subparsers.add_parser('positions', help='Affiche les positions ouvertes')
    
    # Commande order
    order_parser = subparsers.add_parser('order', help='Place un ordre')
    order_parser.add_argument('symbol', help='Symbole (ex: BTC-USDT)')
    order_parser.add_argument('side', choices=['BUY', 'SELL'], help='Côté de l\'ordre')
    order_parser.add_argument('type', choices=['MARKET', 'LIMIT'], help='Type d\'ordre')
    order_parser.add_argument('quantity', type=float, help='Quantité')
    order_parser.add_argument('--price', type=float, help='Prix (requis pour LIMIT)')
    
    # Commande monitor
    monitor_parser = subparsers.add_parser('monitor', help='Démarre le monitoring')
    monitor_parser.add_argument('symbols', nargs='+', help='Symboles à surveiller')
    monitor_parser.add_argument('--interval', type=int, default=60, help='Intervalle en secondes')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 Application BingX Trading")
    print("=" * 50)
    
    try:
        if args.command == 'test':
            test_connection()
        elif args.command == 'market':
            get_market_data(args.symbol)
        elif args.command == 'positions':
            show_positions()
        elif args.command == 'order':
            place_order(args.symbol, args.side, args.type, args.quantity, args.price)
        elif args.command == 'monitor':
            monitor_symbols(args.symbols, args.interval)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
