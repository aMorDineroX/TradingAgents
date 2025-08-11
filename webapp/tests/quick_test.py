#!/usr/bin/env python3
"""
Test Rapide TradingAgents Interface Moderne
Vérification rapide que tout fonctionne correctement
"""

import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"

def print_status(message, status="info"):
    """Afficher un message avec statut"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_server_connection():
    """Tester la connexion au serveur"""
    print_status("Test de connexion au serveur...")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_status("Serveur accessible", "success")
            return True
        else:
            print_status(f"Serveur répond avec le code {response.status_code}", "warning")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"Impossible de se connecter: {e}", "error")
        print_status("Démarrez l'application avec: python run.py", "info")
        return False

def test_main_pages():
    """Tester les pages principales"""
    print_status("Test des pages principales...")
    
    pages = {
        "/": "Page d'accueil",
        "/automation": "Automatisation", 
        "/backtesting": "Backtesting",
        "/demo": "Démonstration",
        "/config": "Configuration"
    }
    
    all_ok = True
    
    for url, name in pages.items():
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=5)
            if response.status_code == 200:
                print_status(f"{name} - OK", "success")
            else:
                print_status(f"{name} - Erreur {response.status_code}", "error")
                all_ok = False
        except Exception as e:
            print_status(f"{name} - Exception: {e}", "error")
            all_ok = False
    
    return all_ok

def test_api_endpoints():
    """Tester les endpoints API"""
    print_status("Test des API endpoints...")
    
    endpoints = {
        "/api/status": "Statut système",
        "/api/list_results": "Liste des résultats",
        "/api/automation/status": "Statut automatisation",
        "/api/brokerage/status": "Statut courtage"
    }
    
    all_ok = True
    
    for url, name in endpoints.items():
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=5)
            if response.status_code == 200:
                print_status(f"{name} - OK", "success")
            else:
                print_status(f"{name} - Erreur {response.status_code}", "warning")
                # Les API peuvent retourner des erreurs si les services ne sont pas configurés
        except Exception as e:
            print_status(f"{name} - Exception: {e}", "error")
            all_ok = False
    
    return all_ok

def test_static_assets():
    """Tester les assets statiques"""
    print_status("Test des assets statiques...")
    
    assets = {
        "/static/css/modern-design.css": "CSS moderne",
        "/static/css/navigation.css": "CSS navigation",
        "/static/js/modern-ui.js": "JavaScript UI",
        "/static/js/charts.js": "JavaScript graphiques"
    }
    
    all_ok = True
    
    for url, name in assets.items():
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=5)
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print_status(f"{name} - OK ({size_kb:.1f}KB)", "success")
            else:
                print_status(f"{name} - Erreur {response.status_code}", "error")
                all_ok = False
        except Exception as e:
            print_status(f"{name} - Exception: {e}", "error")
            all_ok = False
    
    return all_ok

def test_performance_basic():
    """Test de performance basique"""
    print_status("Test de performance basique...")
    
    # Tester le temps de réponse de la page d'accueil
    start_time = time.time()
    try:
        response = requests.get(BASE_URL, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            if response_time < 2.0:
                print_status(f"Temps de réponse: {response_time:.2f}s - Excellent", "success")
            elif response_time < 5.0:
                print_status(f"Temps de réponse: {response_time:.2f}s - Acceptable", "warning")
            else:
                print_status(f"Temps de réponse: {response_time:.2f}s - Lent", "error")
                return False
        else:
            print_status(f"Erreur de réponse: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"Erreur test performance: {e}", "error")
        return False
    
    return True

def test_modern_interface():
    """Tester spécifiquement l'interface moderne"""
    print_status("Test de l'interface moderne...")
    
    try:
        # Tester la page d'accueil moderne
        response = requests.get(f"{BASE_URL}/?modern=true", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Vérifier la présence d'éléments modernes
            modern_elements = [
                "modern-design.css",
                "charts.js",
                "advanced-ux.js",
                "hero-section",
                "navbar"
            ]
            
            found_elements = []
            for element in modern_elements:
                if element in content:
                    found_elements.append(element)
            
            if len(found_elements) >= 3:
                print_status(f"Interface moderne détectée ({len(found_elements)}/{len(modern_elements)} éléments)", "success")
                return True
            else:
                print_status(f"Interface moderne partielle ({len(found_elements)}/{len(modern_elements)} éléments)", "warning")
                return False
        else:
            print_status(f"Erreur chargement interface: {response.status_code}", "error")
            return False
            
    except Exception as e:
        print_status(f"Erreur test interface: {e}", "error")
        return False

def run_quick_test():
    """Exécuter le test rapide complet"""
    print("🧪" + "=" * 50)
    print("   TEST RAPIDE TRADINGAGENTS INTERFACE MODERNE")
    print("=" * 52)
    print()
    
    tests = [
        ("Connexion serveur", test_server_connection),
        ("Pages principales", test_main_pages),
        ("API endpoints", test_api_endpoints),
        ("Assets statiques", test_static_assets),
        ("Performance basique", test_performance_basic),
        ("Interface moderne", test_modern_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Erreur inattendue: {e}", "error")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 52)
    print("📊 RÉSUMÉ DU TEST RAPIDE")
    print("=" * 52)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
    
    print()
    print(f"📈 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print_status("🎉 TOUS LES TESTS RAPIDES SONT PASSÉS!", "success")
        print_status("L'interface TradingAgents fonctionne correctement.", "info")
        return True
    else:
        print_status(f"⚠️ {total - passed} test(s) ont échoué", "warning")
        print_status("Vérifiez les erreurs ci-dessus ou lancez les tests complets.", "info")
        return False

def main():
    """Fonction principale"""
    success = run_quick_test()
    
    print("\n" + "=" * 52)
    if success:
        print("✅ Interface prête! Vous pouvez maintenant:")
        print("   • Ouvrir http://localhost:5000 dans votre navigateur")
        print("   • Tester les fonctionnalités sur /demo")
        print("   • Lancer les tests complets avec: python run_all_tests.py")
    else:
        print("❌ Problèmes détectés. Actions recommandées:")
        print("   • Vérifiez que l'application est démarrée: python run.py")
        print("   • Consultez les logs d'erreur")
        print("   • Lancez les tests détaillés: python run_all_tests.py")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
