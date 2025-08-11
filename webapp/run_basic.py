#!/usr/bin/env python3
"""
Version de base de l'application sans les systèmes d'automatisation
Pour tester l'interface principale en cas de problèmes d'imports
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

def main():
    """Fonction principale"""
    print("🚀 TradingAgents Web Interface - Mode de Base")
    print("=" * 60)
    
    try:
        # Imports de base
        from flask import Flask, render_template, request, jsonify
        from flask_socketio import SocketIO, emit
        import threading
        import time
        import json
        from datetime import datetime
        
        print("✅ Imports Flask réussis")
        
        # Essayer d'importer TradingAgents
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            print("✅ TradingAgents disponible")
            tradingagents_available = True
        except ImportError as e:
            print(f"⚠️ TradingAgents non disponible: {e}")
            tradingagents_available = False
        
        # Essayer d'importer la base de données
        try:
            from database import get_db_manager, init_database
            print("✅ Base de données disponible")
            database_available = True
        except ImportError as e:
            print(f"⚠️ Base de données non disponible: {e}")
            database_available = False
        
        # Créer l'application Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        
        print("✅ Application Flask créée")
        
        # Routes de base
        @app.route('/')
        def index():
            """Page d'accueil"""
            return render_template('index.html')
        
        @app.route('/api/status')
        def api_status():
            """API de statut"""
            return jsonify({
                'status': 'running',
                'tradingagents_available': tradingagents_available,
                'database_available': database_available,
                'automation_available': False,  # Désactivé en mode de base
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/api/test_analysis')
        def test_analysis():
            """Test d'analyse simple"""
            if not tradingagents_available:
                return jsonify({'error': 'TradingAgents non disponible'}), 500
            
            try:
                # Test simple avec configuration par défaut
                config = DEFAULT_CONFIG.copy()
                config.update({
                    'llm_provider': 'openai',
                    'quick_think_llm': 'llama-3.1-8b-instant',
                    'deep_think_llm': 'llama-3.1-8b-instant',
                    'backend_url': 'https://api.groq.com/openai/v1',
                    'openai_api_key': os.getenv('GROQ_API_KEY')
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration TradingAgents OK',
                    'config': {
                        'provider': config.get('llm_provider'),
                        'model': config.get('quick_think_llm')
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/automation')
        def automation_placeholder():
            """Page d'automatisation (placeholder)"""
            return """
            <html>
            <head><title>Automatisation - Non Disponible</title></head>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1>🚧 Automatisation Non Disponible</h1>
                <p>Les systèmes d'automatisation ne sont pas encore chargés.</p>
                <p>Utilisez <code>python run.py</code> pour la version complète.</p>
                <a href="/">← Retour aux analyses</a>
            </body>
            </html>
            """
        
        print("\n🌐 Démarrage du serveur web...")
        print("📊 Interface disponible sur: http://localhost:5000")
        print("🔧 Mode de base (sans automatisation)")
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
        print("\n💡 Solutions possibles:")
        print("1. Installer les dépendances: pip install -r requirements.txt")
        print("2. Vérifier que vous êtes dans le bon environnement virtuel")
        print("3. Vérifier que TradingAgents est installé dans le projet parent")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
