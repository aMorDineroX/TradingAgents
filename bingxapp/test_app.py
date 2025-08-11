"""
Script de test pour l'application BingX
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bingxapp.config import BingXConfig
from bingxapp.client import BingXClient
from bingxapp.trading_bot import TradingBot


def test_config():
    """Test de la configuration"""
    print("🔧 Test de la configuration...")
    
    config = BingXConfig.from_env()
    print(f"✅ API URL: {config.api_url}")
    print(f"✅ Use Testnet: {config.use_testnet}")
    print(f"✅ Timeout: {config.timeout}")
    print(f"✅ API Key: {config.api_key[:10]}...")
    print(f"✅ Secret Key: {config.secret_key[:10]}...")


def test_client():
    """Test du client BingX"""
    print("\n🔌 Test du client BingX...")
    
    config = BingXConfig.from_env()
    client = BingXClient(config)
    
    # Test de connectivité
    if client.test_connectivity():
        print("✅ Connectivité OK")
        
        try:
            # Test de l'heure du serveur
            server_time = client.get_server_time()
            print(f"✅ Heure du serveur: {server_time}")
            
            # Test des informations de symboles
            symbols = client.get_symbol_info()
            print(f"✅ Nombre de symboles disponibles: {len(symbols.get('data', []))}")
            
        except Exception as e:
            print(f"❌ Erreur lors des tests du client: {e}")
    else:
        print("❌ Échec de la connectivité")


def test_bot():
    """Test du bot de trading"""
    print("\n🤖 Test du bot de trading...")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if bot.initialize():
        print("✅ Bot initialisé avec succès")
        
        try:
            # Test du solde
            balance = bot.get_account_balance()
            print(f"✅ Solde récupéré: {len(balance)} éléments")
            
            # Test des données de marché
            market_data = bot.get_market_data("BTC-USDT")
            if market_data:
                print("✅ Données de marché récupérées")
            else:
                print("⚠️  Aucune donnée de marché")
            
            # Test des positions
            positions = bot.get_positions()
            print(f"✅ Positions récupérées: {len(positions)} positions")
            
        except Exception as e:
            print(f"❌ Erreur lors des tests du bot: {e}")
    else:
        print("❌ Échec de l'initialisation du bot")


def main():
    """Fonction principale de test"""
    print("🚀 Tests de l'application BingX")
    print("=" * 50)
    
    try:
        test_config()
        test_client()
        test_bot()
        
        print("\n✅ Tous les tests terminés!")
        print("\n📋 Commandes disponibles:")
        print("  python -m bingxapp.main test")
        print("  python -m bingxapp.main market BTC-USDT")
        print("  python -m bingxapp.main positions")
        print("  python -m bingxapp.main monitor BTC-USDT ETH-USDT")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
