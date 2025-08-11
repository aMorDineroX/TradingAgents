#!/usr/bin/env python3
"""
Script de démarrage pour TradingAgents Web Interface (Mode Test)
Version de test qui définit des clés API factices pour tester l'interface
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer TradingAgents
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Définir des clés API factices pour les tests
os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-interface-testing-only'
os.environ['FINNHUB_API_KEY'] = 'test-finnhub-key-for-interface-testing'

print("🧪 Mode Test - Clés API factices définies")
print("⚠️  ATTENTION: Ce mode est uniquement pour tester l'interface web")
print("⚠️  Les analyses réelles ne fonctionneront pas sans vraies clés API")

# Importer et démarrer l'application
try:
    from app import app, socketio
    
    print("🚀 Démarrage de TradingAgents Web Interface (Mode Test)...")
    print("📊 Interface disponible sur: http://localhost:5000")
    print("🔧 Mode debug activé")
    print("💡 Appuyez sur Ctrl+C pour arrêter")
    
    # Démarrer l'application
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        allow_unsafe_werkzeug=True
    )
    
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("Assurez-vous que toutes les dépendances sont installées:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erreur lors du démarrage: {e}")
    sys.exit(1)
