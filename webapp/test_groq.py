#!/usr/bin/env python3
"""
Test rapide pour vérifier que Groq fonctionne avec TradingAgents
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Charger le fichier .env
env_file = parent_dir / '.env'
if env_file.exists():
    print(f"📄 Chargement du fichier .env depuis: {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def test_groq_connection():
    """Tester la connexion Groq via l'API OpenAI compatible"""
    try:
        from openai import OpenAI
        
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key:
            print("❌ GROQ_API_KEY non définie")
            return False
        
        print("🧪 Test de connexion Groq via API compatible OpenAI")
        print("=" * 60)
        print(f"🔑 Clé Groq: {groq_key[:20]}...")
        
        # Créer le client OpenAI avec l'URL Groq
        client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Test simple
        print("🚀 Test d'une requête simple...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Dis juste 'Groq fonctionne!' en une phrase."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ Réponse reçue: {result}")
        
        # Test avec un autre modèle disponible
        print("🚀 Test avec Mixtral...")
        response2 = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "user", "content": "Analyse brièvement l'action SPY en 2 phrases."}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        result2 = response2.choices[0].message.content
        print(f"✅ Analyse SPY: {result2}")
        
        print("🎉 Groq fonctionne parfaitement!")
        return True
        
    except ImportError:
        print("❌ Module openai non installé. Installez avec: pip install openai")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_tradingagents_config():
    """Tester la configuration TradingAgents avec Groq"""
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("\n🔧 Test de configuration TradingAgents")
        print("=" * 60)
        
        # Configuration pour Groq
        groq_config = DEFAULT_CONFIG.copy()
        groq_config.update({
            'llm_provider': 'openai',  # Groq via API compatible
            'quick_think_llm': 'llama-3.1-8b-instant',
            'deep_think_llm': 'llama-3.1-8b-instant',  # Même modèle rapide
            'backend_url': 'https://api.groq.com/openai/v1',
            'openai_api_key': os.getenv('GROQ_API_KEY'),
            'max_debate_rounds': 1,  # Rapide pour les tests
            'max_risk_discuss_rounds': 1
        })
        
        print("✅ Configuration Groq créée:")
        print(f"   Provider: {groq_config['llm_provider']}")
        print(f"   Modèle rapide: {groq_config['quick_think_llm']}")
        print(f"   Modèle avancé: {groq_config['deep_think_llm']}")
        print(f"   URL: {groq_config['backend_url']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'importation TradingAgents: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Test de compatibilité Groq avec TradingAgents")
    print("=" * 70)
    
    # Test 1: Connexion Groq
    groq_ok = test_groq_connection()
    
    # Test 2: Configuration TradingAgents
    config_ok = test_tradingagents_config()
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    if groq_ok and config_ok:
        print("🎉 Tous les tests sont passés!")
        print("✅ Groq est prêt à être utilisé avec TradingAgents")
        print("\nVous pouvez maintenant:")
        print("1. Redémarrer l'application: python run.py")
        print("2. Tester une analyse avec SPY")
        print("3. L'analyse devrait utiliser Groq automatiquement")
    elif groq_ok:
        print("⚠️ Groq fonctionne mais problème de configuration TradingAgents")
    else:
        print("❌ Problème avec Groq")
        print("Vérifiez votre clé API dans le fichier .env")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
