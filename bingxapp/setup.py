"""
Script d'installation et de configuration pour l'application BingX
"""

import os
import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Installe les dépendances requises"""
    print("📦 Installation des dépendances...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        return False


def create_env_file():
    """Crée le fichier .env à partir de l'exemple"""
    print("🔧 Configuration de l'environnement...")
    
    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print("⚠️  Le fichier .env existe déjà")
        response = input("Voulez-vous le remplacer ? (y/N): ").strip().lower()
        if response != 'y':
            print("📄 Conservation du fichier .env existant")
            return True
    
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Fichier .env créé avec succès")
        print("📝 Vous pouvez modifier les valeurs dans .env selon vos besoins")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")
        return False


def test_installation():
    """Teste l'installation"""
    print("🧪 Test de l'installation...")
    
    try:
        # Import des modules
        from .config import BingXConfig
        from .client import BingXClient
        from .trading_bot import TradingBot
        
        print("✅ Modules importés avec succès")
        
        # Test de configuration
        config = BingXConfig.from_env()
        print("✅ Configuration chargée")
        
        # Test de connectivité
        client = BingXClient(config)
        if client.test_connectivity():
            print("✅ Connectivité BingX OK")
        else:
            print("⚠️  Problème de connectivité BingX")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def show_usage_examples():
    """Affiche des exemples d'utilisation"""
    print("\n📚 Exemples d'utilisation:")
    print("=" * 50)
    
    examples = [
        ("Test de connexion", "python -m bingxapp.main test"),
        ("Données de marché", "python -m bingxapp.main market BTC-USDT"),
        ("Positions ouvertes", "python -m bingxapp.main positions"),
        ("Monitoring", "python -m bingxapp.main monitor BTC-USDT ETH-USDT"),
        ("Exemples interactifs", "python -m bingxapp.examples"),
    ]
    
    for description, command in examples:
        print(f"\n🔸 {description}:")
        print(f"   {command}")
    
    print("\n📖 Pour plus d'informations, consultez le README.md")


def main():
    """Fonction principale d'installation"""
    print("🚀 Installation de l'application BingX Trading")
    print("=" * 60)
    
    steps = [
        ("Installation des dépendances", install_dependencies),
        ("Configuration de l'environnement", create_env_file),
        ("Test de l'installation", test_installation),
    ]
    
    success = True
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            success = False
            break
    
    if success:
        print("\n🎉 Installation terminée avec succès !")
        show_usage_examples()
    else:
        print("\n❌ Installation échouée")
        print("Veuillez vérifier les erreurs ci-dessus et réessayer")
        sys.exit(1)


if __name__ == '__main__':
    main()
