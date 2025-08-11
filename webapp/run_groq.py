#!/usr/bin/env python3
"""
Script de démarrage pour TradingAgents Web Interface avec Groq
Configuration optimisée pour utiliser Groq comme fournisseur LLM
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
    print("✅ Variables d'environnement chargées depuis .env")
else:
    print("⚠️  Fichier .env non trouvé")

def setup_groq_environment():
    """Configurer l'environnement pour Groq"""
    
    # Vérifier la clé Groq
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ Clé GROQ_API_KEY manquante!")
        print("Veuillez définir votre clé Groq:")
        print("export GROQ_API_KEY=gsk_your_groq_key_here")
        return False
    
    # Vérifier la clé FinnHub (optionnelle pour les tests)
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    if not finnhub_key:
        print("⚠️  Clé FINNHUB_API_KEY manquante - utilisation de données de test")
        print("Pour des données réelles, obtenez une clé gratuite sur https://finnhub.io/register")
        # Définir une clé de test
        os.environ['FINNHUB_API_KEY'] = 'test-key-for-groq-demo'
    
    print("✅ Configuration Groq validée")
    print(f"🔑 Groq API Key: {groq_key[:20]}...")
    if finnhub_key and finnhub_key != 'test-key-for-groq-demo':
        print(f"🔑 FinnHub API Key: {finnhub_key[:10]}...")
    
    return True

def main():
    """Fonction principale"""
    print("🚀 TradingAgents Web Interface - Configuration Groq")
    print("=" * 60)
    
    # Configurer l'environnement
    if not setup_groq_environment():
        sys.exit(1)
    
    # Importer et démarrer l'application
    try:
        from app import app, socketio
        
        print("\n🎯 Démarrage avec les modèles Groq:")
        print("   • Modèle rapide: llama-3.1-8b-instant")
        print("   • Modèle avancé: llama-3.1-70b-versatile")
        print("   • Backend: https://api.groq.com/openai/v1")
        
        print("\n📊 Interface disponible sur: http://localhost:5000")
        print("🔧 Mode debug activé")
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
