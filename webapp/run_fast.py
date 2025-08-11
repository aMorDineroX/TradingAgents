#!/usr/bin/env python3
"""
Script de démarrage rapide pour TradingAgents Web Interface
Configuration optimisée pour des analyses rapides avec Groq
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer TradingAgents
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Charger le fichier .env s'il existe
env_file = parent_dir / '.env'
if env_file.exists():
    print(f"📄 Chargement du fichier .env depuis: {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def setup_fast_environment():
    """Configurer l'environnement pour des analyses rapides"""
    
    # Vérifier la clé Groq
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ Clé GROQ_API_KEY manquante!")
        print("Veuillez définir votre clé Groq:")
        print("export GROQ_API_KEY=gsk_your_groq_key_here")
        return False
    
    # Forcer la configuration rapide
    os.environ['TRADING_MODE'] = 'fast'
    os.environ['LLM_PROVIDER'] = 'groq'
    os.environ['QUICK_THINK_LLM'] = 'llama-3.1-8b-instant'
    os.environ['DEEP_THINK_LLM'] = 'llama-3.1-8b-instant'  # Même modèle rapide pour tout
    os.environ['MAX_DEBATE_ROUNDS'] = '1'
    os.environ['MAX_RISK_ROUNDS'] = '1'
    os.environ['TEMPERATURE'] = '0.3'
    os.environ['MAX_TOKENS'] = '2000'
    
    print("✅ Configuration rapide activée")
    print(f"🔑 Groq API Key: {groq_key[:20]}...")
    print("⚡ Mode: Analyses ultra-rapides")
    print("🤖 Modèle: llama-3.1-8b-instant (pour tout)")
    print("🔄 Débats: 1 tour seulement")
    
    return True

def main():
    """Fonction principale"""
    print("⚡ TradingAgents Web Interface - Mode Rapide")
    print("=" * 60)
    
    # Configurer l'environnement
    if not setup_fast_environment():
        sys.exit(1)
    
    # Importer et démarrer l'application
    try:
        from app import app, socketio
        
        print("\n🚀 Démarrage en mode rapide:")
        print("   • Modèle unique: llama-3.1-8b-instant")
        print("   • Débats réduits: 1 tour")
        print("   • Température basse: 0.3")
        print("   • Tokens limités: 2000")
        
        print("\n📊 Interface disponible sur: http://localhost:5000")
        print("⚡ Analyses optimisées pour la vitesse")
        print("💡 Appuyez sur Ctrl+C pour arrêter")
        print("=" * 60)
        
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

if __name__ == "__main__":
    main()
