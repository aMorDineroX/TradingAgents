#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Test Simple pour l'Interface Moderne TradingAgents
Point d'entrée facile pour tester l'interface
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Afficher la bannière"""
    print("🧪" + "=" * 60)
    print("   TESTS INTERFACE MODERNE TRADINGAGENTS")
    print("=" * 62)
    print()

def check_server():
    """Vérifier si le serveur est en cours d'exécution"""
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Démarrer le serveur si nécessaire"""
    if check_server():
        print("✅ Serveur déjà en cours d'exécution")
        return True
    
    print("🚀 Démarrage du serveur...")
    try:
        # Démarrer le serveur en arrière-plan
        subprocess.Popen([sys.executable, "run.py"], 
                        cwd=Path(__file__).parent,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        # Attendre que le serveur démarre
        for i in range(15):
            if check_server():
                print("✅ Serveur démarré avec succès")
                return True
            time.sleep(1)
            print(f"   Attente... ({i+1}/15)")
        
        print("❌ Impossible de démarrer le serveur")
        return False
        
    except Exception as e:
        print(f"❌ Erreur démarrage: {e}")
        return False

def run_quick_test():
    """Exécuter le test rapide"""
    print("🏃‍♂️ Exécution du test rapide...")
    try:
        result = subprocess.run([
            sys.executable, "tests/quick_test.py"
        ], cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur test rapide: {e}")
        return False

def run_full_tests():
    """Exécuter tous les tests"""
    print("🔬 Exécution de la suite complète...")
    try:
        result = subprocess.run([
            sys.executable, "tests/run_all_tests.py"
        ], cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur tests complets: {e}")
        return False

def open_demo():
    """Ouvrir la page de démonstration"""
    import webbrowser
    try:
        webbrowser.open("http://localhost:5000/demo")
        print("🌐 Page de démonstration ouverte dans le navigateur")
        return True
    except Exception as e:
        print(f"❌ Impossible d'ouvrir le navigateur: {e}")
        print("   Ouvrez manuellement: http://localhost:5000/demo")
        return False

def show_menu():
    """Afficher le menu principal"""
    print("\n📋 Que voulez-vous faire ?")
    print("1. 🏃‍♂️ Test rapide (recommandé)")
    print("2. 🔬 Tests complets")
    print("3. 🌐 Ouvrir la démonstration")
    print("4. 🚀 Juste démarrer le serveur")
    print("5. ❌ Quitter")
    print()

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier les dépendances de base
    try:
        import requests
    except ImportError:
        print("❌ Module 'requests' manquant")
        print("   Installez avec: pip install requests")
        return 1
    
    while True:
        show_menu()
        
        try:
            choice = input("Votre choix (1-5): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            return 0
        
        if choice == "1":
            # Test rapide
            print("\n" + "="*50)
            if not start_server():
                continue
            
            success = run_quick_test()
            
            if success:
                print("\n🎉 Test rapide réussi!")
                print("💡 Conseil: Ouvrez http://localhost:5000/demo pour voir l'interface")
                
                demo_choice = input("\nOuvrir la démonstration maintenant ? (o/N): ").strip().lower()
                if demo_choice in ['o', 'oui', 'y', 'yes']:
                    open_demo()
            else:
                print("\n⚠️ Problèmes détectés dans le test rapide")
                full_choice = input("Lancer les tests complets pour plus de détails ? (o/N): ").strip().lower()
                if full_choice in ['o', 'oui', 'y', 'yes']:
                    run_full_tests()
        
        elif choice == "2":
            # Tests complets
            print("\n" + "="*50)
            if not start_server():
                continue
            
            print("⚠️ Les tests complets peuvent prendre plusieurs minutes...")
            confirm = input("Continuer ? (o/N): ").strip().lower()
            if confirm in ['o', 'oui', 'y', 'yes']:
                success = run_full_tests()
                if success:
                    print("\n🎉 Tous les tests sont passés!")
                else:
                    print("\n⚠️ Certains tests ont échoué - voir les détails ci-dessus")
        
        elif choice == "3":
            # Démonstration
            print("\n" + "="*50)
            if not start_server():
                continue
            
            open_demo()
            print("\n💡 La page de démonstration contient:")
            print("   • Tous les composants UI modernes")
            print("   • Tests interactifs")
            print("   • Exemples de graphiques")
            print("   • Palette de couleurs")
        
        elif choice == "4":
            # Juste démarrer le serveur
            print("\n" + "="*50)
            if start_server():
                print("\n✅ Serveur démarré!")
                print("🌐 Accédez à l'interface: http://localhost:5000")
                print("🎨 Page de démonstration: http://localhost:5000/demo")
                print("🤖 Automatisation: http://localhost:5000/automation")
                print("📈 Backtesting: http://localhost:5000/backtesting")
        
        elif choice == "5":
            # Quitter
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide, veuillez entrer 1, 2, 3, 4 ou 5")
        
        # Pause avant de réafficher le menu
        input("\nAppuyez sur Entrée pour continuer...")
        print("\n" + "="*62)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interruption détectée, au revoir!")
        sys.exit(0)
