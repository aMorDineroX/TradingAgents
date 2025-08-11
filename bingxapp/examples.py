"""
Exemples d'utilisation de l'application BingX
"""

import time
import json
from typing import List

from .config import BingXConfig
from .trading_bot import TradingBot


def exemple_surveillance_prix():
    """Exemple de surveillance des prix avec alertes"""
    print("🔍 Exemple: Surveillance des prix avec alertes")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible d'initialiser le bot")
        return
    
    # Symboles à surveiller
    symboles = ["BTC-USDT", "ETH-USDT"]
    
    # Seuils d'alerte (exemple)
    seuils = {
        "BTC-USDT": {"max": 125000, "min": 115000},
        "ETH-USDT": {"max": 4000, "min": 3500}
    }
    
    print(f"📊 Surveillance de {symboles} avec seuils d'alerte")
    
    for i in range(5):  # 5 vérifications
        print(f"\n--- Vérification {i+1} ---")
        
        for symbole in symboles:
            market_data = bot.get_market_data(symbole)
            
            if market_data and 'ticker' in market_data:
                ticker = market_data['ticker']['data']
                prix_actuel = float(ticker['lastPrice'])
                
                print(f"{symbole}: {prix_actuel:,.2f} USDT")
                
                # Vérifier les seuils
                if symbole in seuils:
                    if prix_actuel > seuils[symbole]["max"]:
                        print(f"🚨 ALERTE: {symbole} au-dessus du seuil max ({seuils[symbole]['max']})")
                    elif prix_actuel < seuils[symbole]["min"]:
                        print(f"🚨 ALERTE: {symbole} en-dessous du seuil min ({seuils[symbole]['min']})")
                    else:
                        print(f"✅ {symbole} dans la fourchette normale")
        
        if i < 4:  # Pas de pause à la dernière itération
            time.sleep(10)  # Attendre 10 secondes


def exemple_analyse_positions():
    """Exemple d'analyse des positions ouvertes"""
    print("📊 Exemple: Analyse des positions ouvertes")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible d'initialiser le bot")
        return
    
    positions = bot.get_positions()
    
    if not positions:
        print("📭 Aucune position ouverte")
        return
    
    print(f"🎯 Analyse de {len(positions)} positions:")
    
    total_pnl = 0
    positions_gagnantes = 0
    positions_perdantes = 0
    
    for position in positions:
        symbole = position.get('symbol', 'N/A')
        quantite = float(position.get('positionAmt', 0))
        pnl = float(position.get('unrealizedProfit', 0))
        
        total_pnl += pnl
        
        if pnl > 0:
            positions_gagnantes += 1
            status = "🟢 GAIN"
        elif pnl < 0:
            positions_perdantes += 1
            status = "🔴 PERTE"
        else:
            status = "⚪ NEUTRE"
        
        print(f"{status} {symbole}: {pnl:+.4f} USDT (Qty: {quantite})")
    
    print(f"\n📈 Résumé:")
    print(f"  Total PnL: {total_pnl:+.4f} USDT")
    print(f"  Positions gagnantes: {positions_gagnantes}")
    print(f"  Positions perdantes: {positions_perdantes}")
    print(f"  Taux de réussite: {positions_gagnantes/(len(positions))*100:.1f}%")


def exemple_carnet_ordres():
    """Exemple d'analyse du carnet d'ordres"""
    print("📖 Exemple: Analyse du carnet d'ordres")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible d'initialiser le bot")
        return
    
    symbole = "BTC-USDT"
    market_data = bot.get_market_data(symbole)
    
    if not market_data or 'orderbook' not in market_data:
        print("❌ Impossible de récupérer le carnet d'ordres")
        return
    
    orderbook = market_data['orderbook']['data']
    bids = orderbook['bids'][:5]  # Top 5 bids
    asks = orderbook['asks'][:5]  # Top 5 asks
    
    print(f"📖 Carnet d'ordres pour {symbole}:")
    print("\n🟢 ACHATS (Bids):")
    for i, (prix, quantite) in enumerate(bids, 1):
        print(f"  {i}. {float(prix):,.2f} USDT × {float(quantite):.4f}")
    
    print("\n🔴 VENTES (Asks):")
    for i, (prix, quantite) in enumerate(asks, 1):
        print(f"  {i}. {float(prix):,.2f} USDT × {float(quantite):.4f}")
    
    # Calculer le spread
    meilleur_bid = float(bids[0][0])
    meilleur_ask = float(asks[0][0])
    spread = meilleur_ask - meilleur_bid
    spread_pct = (spread / meilleur_bid) * 100
    
    print(f"\n💰 Spread: {spread:.2f} USDT ({spread_pct:.4f}%)")


def exemple_informations_compte():
    """Exemple d'affichage des informations du compte"""
    print("💰 Exemple: Informations détaillées du compte")
    
    config = BingXConfig.from_env()
    bot = TradingBot(config)
    
    if not bot.initialize():
        print("❌ Impossible d'initialiser le bot")
        return
    
    balance = bot.get_account_balance()
    
    if not balance or 'data' not in balance:
        print("❌ Impossible de récupérer les informations du compte")
        return
    
    data = balance['data']['balance']
    
    print("💰 Informations du compte:")
    print(f"  User ID: {data.get('userId', 'N/A')}")
    print(f"  Asset: {data.get('asset', 'N/A')}")
    print(f"  Solde total: {float(data.get('balance', 0)):,.4f} USDT")
    print(f"  Équité: {float(data.get('equity', 0)):,.4f} USDT")
    print(f"  PnL non réalisé: {float(data.get('unrealizedProfit', 0)):+.4f} USDT")
    print(f"  PnL réalisé: {float(data.get('realisedProfit', 0)):+.4f} USDT")
    print(f"  Marge disponible: {float(data.get('availableMargin', 0)):,.4f} USDT")
    print(f"  Marge utilisée: {float(data.get('usedMargin', 0)):,.4f} USDT")
    
    # Calculer quelques ratios
    balance_total = float(data.get('balance', 0))
    marge_utilisee = float(data.get('usedMargin', 0))
    
    if balance_total > 0:
        utilisation_marge = (marge_utilisee / balance_total) * 100
        print(f"  Utilisation de la marge: {utilisation_marge:.2f}%")


def main():
    """Fonction principale pour exécuter les exemples"""
    print("🚀 Exemples d'utilisation de l'application BingX")
    print("=" * 60)
    
    exemples = [
        ("1", "Informations du compte", exemple_informations_compte),
        ("2", "Analyse des positions", exemple_analyse_positions),
        ("3", "Carnet d'ordres", exemple_carnet_ordres),
        ("4", "Surveillance des prix", exemple_surveillance_prix),
    ]
    
    print("\nExemples disponibles:")
    for num, nom, _ in exemples:
        print(f"  {num}. {nom}")
    
    choix = input("\nChoisissez un exemple (1-4) ou 'all' pour tous: ").strip()
    
    if choix.lower() == 'all':
        for num, nom, fonction in exemples:
            print(f"\n{'='*60}")
            print(f"Exécution de l'exemple {num}: {nom}")
            print('='*60)
            try:
                fonction()
            except Exception as e:
                print(f"❌ Erreur dans l'exemple {num}: {e}")
            print("\n" + "="*60)
    else:
        for num, nom, fonction in exemples:
            if choix == num:
                print(f"\n{'='*60}")
                print(f"Exécution de l'exemple {num}: {nom}")
                print('='*60)
                try:
                    fonction()
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                break
        else:
            print("❌ Choix invalide")


if __name__ == '__main__':
    main()
