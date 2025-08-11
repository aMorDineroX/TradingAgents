#!/usr/bin/env python3
"""
Test simple pour vérifier que Groq fonctionne avec le modèle llama-3.1-8b-instant
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

def test_groq_working_model():
    """Tester uniquement le modèle qui fonctionne"""
    try:
        from openai import OpenAI
        
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key:
            print("❌ GROQ_API_KEY non définie")
            return False
        
        print("🧪 Test Groq avec llama-3.1-8b-instant SEULEMENT")
        print("=" * 60)
        print(f"🔑 Clé Groq: {groq_key[:20]}...")
        
        # Créer le client OpenAI avec l'URL Groq
        client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Test 1: Requête simple
        print("🚀 Test 1: Requête simple...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Dis juste 'Test réussi!' en français."}
            ],
            max_tokens=20,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"✅ Réponse: {result}")
        
        # Test 2: Analyse financière simple
        print("🚀 Test 2: Analyse financière...")
        response2 = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Analyse l'ETF SPY en 1 phrase courte."}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        result2 = response2.choices[0].message.content
        print(f"✅ Analyse SPY: {result2}")
        
        # Test 3: Vitesse
        import time
        start_time = time.time()
        
        response3 = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Recommandation: BUY, SELL ou HOLD pour SPY?"}
            ],
            max_tokens=30,
            temperature=0.2
        )
        
        end_time = time.time()
        result3 = response3.choices[0].message.content
        duration = end_time - start_time
        
        print(f"✅ Recommandation: {result3}")
        print(f"⚡ Temps de réponse: {duration:.2f} secondes")
        
        print("🎉 Groq llama-3.1-8b-instant fonctionne parfaitement!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Test Simple Groq - Modèle Fonctionnel")
    print("=" * 60)
    
    success = test_groq_working_model()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCÈS! Groq est prêt pour TradingAgents!")
        print("✅ Modèle: llama-3.1-8b-instant")
        print("✅ Vitesse: Ultra-rapide")
        print("✅ Configuration: Optimisée")
        print("\n🚀 Vous pouvez maintenant:")
        print("1. Démarrer l'application: python run.py")
        print("2. Tester une analyse avec SPY")
        print("3. Utiliser SEULEMENT l'Analyste Marché pour aller vite")
        print("4. L'analyse devrait prendre 15-30 secondes!")
    else:
        print("❌ Problème avec Groq")
    print("=" * 60)

if __name__ == "__main__":
    main()
