#!/usr/bin/env python3
"""
Script de configuration pour TradingAgents Web Interface
Crée tous les répertoires nécessaires et vérifie la configuration
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Créer tous les répertoires nécessaires"""
    directories = [
        "results",
        "configs", 
        "templates",
        "static",
        "static/css",
        "static/js"
    ]
    
    print("📁 Création des répertoires nécessaires...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Tous les répertoires ont été créés")

def check_files():
    """Vérifier que tous les fichiers nécessaires existent"""
    required_files = [
        "app.py",
        "config_manager.py", 
        "run.py",
        "requirements.txt",
        "templates/base.html",
        "templates/index.html",
        "templates/dashboard.html",
        "templates/config.html",
        "static/css/custom.css",
        "static/js/app.js"
    ]
    
    print("\n📄 Vérification des fichiers...")
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANQUANT")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} fichier(s) manquant(s)")
        return False
    else:
        print("\n✅ Tous les fichiers requis sont présents")
        return True

def check_environment():
    """Vérifier les variables d'environnement"""
    print("\n🔑 Vérification des variables d'environnement...")
    
    # Charger le fichier .env s'il existe
    env_file = Path("../.env")
    if env_file.exists():
        print(f"📄 Chargement du fichier .env depuis: {env_file.absolute()}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Vérifier les clés
    required_keys = ['FINNHUB_API_KEY']
    llm_keys = ['OPENAI_API_KEY', 'GROQ_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    
    # Vérifier les clés obligatoires
    missing_required = []
    for key in required_keys:
        if os.getenv(key):
            print(f"   ✅ {key}")
        else:
            print(f"   ❌ {key} - MANQUANT")
            missing_required.append(key)
    
    # Vérifier qu'au moins une clé LLM est présente
    llm_found = False
    for key in llm_keys:
        if os.getenv(key):
            print(f"   ✅ {key}")
            llm_found = True
        else:
            print(f"   ⚪ {key} - optionnel")
    
    if not llm_found:
        print("   ❌ Aucune clé LLM trouvée")
        missing_required.append("Au moins une clé LLM")
    
    return len(missing_required) == 0

def main():
    """Fonction principale"""
    print("🔧 Configuration de TradingAgents Web Interface")
    print("=" * 60)
    
    # Créer les répertoires
    create_directories()
    
    # Vérifier les fichiers
    files_ok = check_files()
    
    # Vérifier l'environnement
    env_ok = check_environment()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 60)
    
    if files_ok and env_ok:
        print("🎉 Configuration complète ! Vous pouvez démarrer l'application:")
        print("   python run.py")
        print("   ou")
        print("   python run_groq.py")
    else:
        print("⚠️  Configuration incomplète:")
        if not files_ok:
            print("   - Certains fichiers sont manquants")
        if not env_ok:
            print("   - Variables d'environnement manquantes")
        print("\nVeuillez corriger ces problèmes avant de démarrer l'application.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
