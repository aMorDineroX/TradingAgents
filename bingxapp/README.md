# Application BingX Trading

Une application Python complète pour se connecter et trader sur l'exchange BingX.

## Fonctionnalités

- ✅ Connexion sécurisée à l'API BingX
- ✅ Récupération des données de marché en temps réel
- ✅ Placement d'ordres (Market et Limit)
- ✅ Gestion des positions
- ✅ Monitoring automatique des symboles
- ✅ Logging détaillé
- ✅ Interface en ligne de commande

## Installation

### Installation rapide
```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester la connexion
python -m bingxapp.main test
```

### Installation avec Makefile
```bash
# Installer et configurer
make install

# Tester la connexion
make test

# Voir toutes les commandes disponibles
make help
```

### Configuration des clés API

Les clés API sont déjà configurées dans le code, mais vous pouvez les surcharger :

1. **Avec des variables d'environnement :**
```bash
export BINGX_API_KEY="votre_api_key"
export BINGX_SECRET_KEY="votre_secret_key"
export BINGX_USE_TESTNET="false"  # true pour le testnet
```

2. **Avec un fichier .env :**
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Modifier les valeurs dans .env
nano .env
```

## Utilisation

### Interface en ligne de commande

#### Test de connexion
```bash
python -m bingxapp.main test
# ou avec Makefile
make test
```

#### Récupérer les données de marché
```bash
python -m bingxapp.main market BTC-USDT
# ou avec Makefile
make market
```

#### Voir les positions ouvertes
```bash
python -m bingxapp.main positions
# ou avec Makefile
make positions
```

#### Placer un ordre au marché ⚠️
```bash
python -m bingxapp.main order BTC-USDT BUY MARKET 0.001
# ou avec Makefile (avec confirmation)
make order-market SYMBOL=BTC-USDT SIDE=BUY QTY=0.001
```

#### Placer un ordre limite ⚠️
```bash
python -m bingxapp.main order BTC-USDT BUY LIMIT 0.001 --price 50000
# ou avec Makefile (avec confirmation)
make order-limit SYMBOL=BTC-USDT SIDE=BUY QTY=0.001 PRICE=50000
```

#### Monitoring en temps réel
```bash
python -m bingxapp.main monitor BTC-USDT ETH-USDT --interval 30
# ou avec Makefile
make monitor
```

### Exemples interactifs

```bash
# Lancer les exemples interactifs
python -m bingxapp.examples
# ou avec Makefile
make examples

# Exemples spécifiques
make info      # Informations du compte
make analyze   # Analyse des positions
make orderbook # Carnet d'ordres BTC-USDT
```

## Structure du projet

```
bingxapp/
├── __init__.py          # Module principal
├── config.py            # Configuration et clés API
├── client.py            # Client API BingX
├── trading_bot.py       # Bot de trading automatisé
├── main.py              # Interface en ligne de commande
├── requirements.txt     # Dépendances
└── README.md           # Documentation
```

## Configuration

### Clés API
Les clés API BingX sont configurées dans `config.py`. Vous pouvez les modifier directement ou utiliser des variables d'environnement.

### Paramètres
- `use_testnet`: Utiliser le testnet (false par défaut)
- `timeout`: Timeout des requêtes (30 secondes par défaut)

## Sécurité

⚠️ **Important** : Les clés API sont actuellement en dur dans le code. Pour un usage en production, il est recommandé de :
1. Utiliser des variables d'environnement
2. Chiffrer les clés sensibles
3. Utiliser un gestionnaire de secrets

## API BingX

Cette application utilise l'API BingX Perpetual Futures v2. Documentation officielle :
- https://bingx-api.github.io/docs/

### Endpoints utilisés
- `/openApi/swap/v2/server/time` - Heure du serveur
- `/openApi/swap/v2/user/balance` - Solde du compte
- `/openApi/swap/v2/user/positions` - Positions ouvertes
- `/openApi/swap/v2/quote/contracts` - Informations des contrats
- `/openApi/swap/v2/quote/ticker` - Prix en temps réel
- `/openApi/swap/v2/quote/depth` - Carnet d'ordres
- `/openApi/swap/v2/trade/order` - Placement/annulation d'ordres
- `/openApi/swap/v2/trade/openOrders` - Ordres ouverts

## Exemples d'utilisation

### Utilisation programmatique

```python
from bingxapp.config import BingXConfig
from bingxapp.trading_bot import TradingBot

# Initialiser le bot
config = BingXConfig.from_env()
bot = TradingBot(config)

# Tester la connexion
if bot.initialize():
    print("Connexion réussie!")
    
    # Récupérer le solde
    balance = bot.get_account_balance()
    print(f"Solde: {balance}")
    
    # Récupérer les données de marché
    market_data = bot.get_market_data("BTC-USDT")
    print(f"Prix BTC: {market_data}")
    
    # Placer un ordre
    order = bot.place_market_order("BTC-USDT", "BUY", 0.001)
    print(f"Ordre placé: {order}")
```

## Support

Pour toute question ou problème, consultez :
1. La documentation officielle BingX
2. Les logs de l'application
3. Les codes d'erreur de l'API

## Licence

Ce projet est sous licence MIT.
