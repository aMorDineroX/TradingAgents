# Makefile pour l'application BingX Trading

.PHONY: help install test clean run-examples

# Variables
PYTHON = python
MODULE = bingxapp

help: ## Affiche cette aide
	@echo "🚀 Application BingX Trading - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Installe l'application et ses dépendances
	@echo "📦 Installation de l'application BingX..."
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✅ Installation terminée"

test: ## Teste la connexion à BingX
	@echo "🧪 Test de connexion à BingX..."
	cd .. && $(PYTHON) -m $(MODULE).main test

test-full: ## Exécute tous les tests
	@echo "🧪 Tests complets..."
	cd .. && $(PYTHON) $(MODULE)/test_app.py

market: ## Récupère les données de marché pour BTC-USDT
	@echo "📊 Données de marché BTC-USDT..."
	cd .. && $(PYTHON) -m $(MODULE).main market BTC-USDT

positions: ## Affiche les positions ouvertes
	@echo "📋 Positions ouvertes..."
	cd .. && $(PYTHON) -m $(MODULE).main positions

examples: ## Lance les exemples interactifs
	@echo "📚 Exemples d'utilisation..."
	cd .. && $(PYTHON) -m $(MODULE).examples

monitor: ## Démarre le monitoring (BTC-USDT et ETH-USDT)
	@echo "👀 Monitoring BTC-USDT et ETH-USDT..."
	@echo "🛑 Appuyez sur Ctrl+C pour arrêter"
	cd .. && $(PYTHON) -m $(MODULE).main monitor BTC-USDT ETH-USDT

monitor-btc: ## Démarre le monitoring pour BTC-USDT uniquement
	@echo "👀 Monitoring BTC-USDT..."
	@echo "🛑 Appuyez sur Ctrl+C pour arrêter"
	cd .. && $(PYTHON) -m $(MODULE).main monitor BTC-USDT

clean: ## Nettoie les fichiers temporaires
	@echo "🧹 Nettoyage..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Nettoyage terminé"

info: ## Affiche les informations du compte
	@echo "💰 Informations du compte..."
	cd .. && $(PYTHON) -c "from $(MODULE).examples import exemple_informations_compte; exemple_informations_compte()"

analyze: ## Analyse les positions ouvertes
	@echo "📊 Analyse des positions..."
	cd .. && $(PYTHON) -c "from $(MODULE).examples import exemple_analyse_positions; exemple_analyse_positions()"

orderbook: ## Affiche le carnet d'ordres BTC-USDT
	@echo "📖 Carnet d'ordres BTC-USDT..."
	cd .. && $(PYTHON) -c "from $(MODULE).examples import exemple_carnet_ordres; exemple_carnet_ordres()"

# Commandes avancées
setup: ## Configuration initiale complète
	@echo "🔧 Configuration initiale..."
	$(PYTHON) $(MODULE)/setup.py

dev-install: ## Installation pour le développement
	@echo "🛠️  Installation développement..."
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

# Commandes de trading (attention !)
order-market: ## Place un ordre au marché (exemple: make order-market SYMBOL=BTC-USDT SIDE=BUY QTY=0.001)
	@echo "⚠️  Placement d'un ordre au marché..."
	@echo "Symbole: $(SYMBOL), Côté: $(SIDE), Quantité: $(QTY)"
	@read -p "Êtes-vous sûr ? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) -m $(MODULE).main order $(SYMBOL) $(SIDE) MARKET $(QTY)

order-limit: ## Place un ordre limite (exemple: make order-limit SYMBOL=BTC-USDT SIDE=BUY QTY=0.001 PRICE=50000)
	@echo "⚠️  Placement d'un ordre limite..."
	@echo "Symbole: $(SYMBOL), Côté: $(SIDE), Quantité: $(QTY), Prix: $(PRICE)"
	@read -p "Êtes-vous sûr ? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) -m $(MODULE).main order $(SYMBOL) $(SIDE) LIMIT $(QTY) --price $(PRICE)

# Aide détaillée
help-trading: ## Aide pour les commandes de trading
	@echo "⚠️  COMMANDES DE TRADING - UTILISEZ AVEC PRÉCAUTION !"
	@echo ""
	@echo "📝 Ordre au marché:"
	@echo "   make order-market SYMBOL=BTC-USDT SIDE=BUY QTY=0.001"
	@echo ""
	@echo "📝 Ordre limite:"
	@echo "   make order-limit SYMBOL=BTC-USDT SIDE=BUY QTY=0.001 PRICE=50000"
	@echo ""
	@echo "⚠️  Ces commandes placent de vrais ordres sur votre compte !"

help-examples: ## Aide pour les exemples
	@echo "📚 EXEMPLES DISPONIBLES:"
	@echo ""
	@echo "🔸 make info      - Informations du compte"
	@echo "🔸 make analyze   - Analyse des positions"
	@echo "🔸 make orderbook - Carnet d'ordres"
	@echo "🔸 make examples  - Exemples interactifs"
