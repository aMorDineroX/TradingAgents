#!/usr/bin/env python3
"""
Script de démarrage pour TradingAgents Web Interface
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
    print("⚠️  Fichier .env non trouvé, utilisation des variables d'environnement système")

# Vérifier les variables d'environnement requises
required_env_vars = ['FINNHUB_API_KEY']
optional_llm_keys = ['OPENAI_API_KEY', 'GROQ_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']

# Vérifier qu'au moins une clé LLM est présente
llm_key_found = any(os.getenv(key) for key in optional_llm_keys)
missing_vars = []

for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars or not llm_key_found:
    if missing_vars:
        print("⚠️  Variables d'environnement manquantes:")
        for var in missing_vars:
            print(f"   - {var}")

    if not llm_key_found:
        print("⚠️  Aucune clé API LLM trouvée. Vous devez définir au moins une de ces variables:")
        for key in optional_llm_keys:
            status = "✅" if os.getenv(key) else "❌"
            print(f"   {status} {key}")

    print("\nVeuillez définir ces variables avant de démarrer l'application.")
    print("Exemples:")
    if missing_vars:
        for var in missing_vars:
            print(f"export {var}=your_api_key_here")
    if not llm_key_found:
        print("export GROQ_API_KEY=gsk_your_groq_key_here")
        print("# ou")
        print("export OPENAI_API_KEY=sk_your_openai_key_here")
    sys.exit(1)

# Importer et démarrer l'application
try:
    from app import app, socketio
    
    print("🚀 Démarrage de TradingAgents Web Interface...")
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
