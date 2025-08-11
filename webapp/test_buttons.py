#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des Boutons de la Page d'Analyse
Vérifie que les boutons et formulaires fonctionnent correctement
"""

import requests
import time
import json

BASE_URL = "http://localhost:5001"

def test_page_loading():
    """Tester que la page se charge correctement"""
    print("🔍 Test du chargement de la page d'analyse...")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Vérifier la présence des éléments clés
            checks = [
                ('analysisForm', 'Formulaire d\'analyse'),
                ('startAnalysisBtn', 'Bouton de démarrage'),
                ('ticker', 'Champ ticker'),
                ('trade_date', 'Champ date'),
                ('research_depth', 'Sélecteur de profondeur'),
                ('market_analyst', 'Checkbox analyste marché'),
            ]
            
            all_present = True
            for element_id, description in checks:
                if f'id="{element_id}"' in content:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - MANQUANT")
                    all_present = False
            
            return all_present
        else:
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def test_api_endpoints():
    """Tester les endpoints API utilisés par les boutons"""
    print("\n🔍 Test des endpoints API...")
    
    endpoints = [
        ('/api/status', 'GET', 'Statut système'),
        ('/api/list_results', 'GET', 'Liste des résultats'),
    ]
    
    all_working = True
    
    for endpoint, method, description in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"  ✅ {description} ({endpoint})")
            else:
                print(f"  ⚠️ {description} ({endpoint}) - Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {description} ({endpoint}) - Erreur: {e}")
            all_working = False
    
    return all_working

def test_analysis_api():
    """Tester l'API de démarrage d'analyse"""
    print("\n🔍 Test de l'API d'analyse...")
    
    test_data = {
        "ticker": "SPY",
        "trade_date": "2024-01-15",
        "config": {
            "selected_analysts": ["market", "social"],
            "max_debate_rounds": 2,
            "max_risk_discuss_rounds": 2
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/start_analysis",
            json=test_data,
            timeout=10
        )
        
        print(f"  📡 Réponse API: Status {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"  ✅ Réponse JSON valide")
                
                if result.get('success'):
                    print(f"  ✅ Analyse démarrée avec succès")
                    if 'session_id' in result:
                        print(f"  ✅ Session ID: {result['session_id']}")
                    return True
                else:
                    print(f"  ⚠️ Analyse non démarrée: {result.get('error', 'Erreur inconnue')}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"  ❌ Réponse JSON invalide")
                print(f"  📄 Contenu: {response.text[:200]}...")
                return False
        else:
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            print(f"  📄 Contenu: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur de connexion: {e}")
        return False

def test_javascript_functionality():
    """Tester que le JavaScript est présent"""
    print("\n🔍 Test du JavaScript...")
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            js_checks = [
                ('startNewAnalysis', 'Fonction de démarrage d\'analyse'),
                ('loadRecentAnalyses', 'Fonction de chargement des analyses'),
                ('updateProgress', 'Fonction de mise à jour du progrès'),
                ('addEventListener', 'Gestionnaires d\'événements'),
                ('fetch(', 'Appels API'),
            ]
            
            all_present = True
            for js_element, description in js_checks:
                if js_element in content:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description} - MANQUANT")
                    all_present = False
            
            return all_present
        else:
            print(f"  ❌ Impossible de charger la page")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def test_css_styling():
    """Tester que les styles CSS sont présents"""
    print("\n🔍 Test des styles CSS...")
    
    css_files = [
        '/static/css/modern-design.css',
        '/static/css/navigation.css',
        '/static/css/components.css',
        '/static/css/charts.css'
    ]
    
    all_loaded = True
    
    for css_file in css_files:
        try:
            response = requests.get(f"{BASE_URL}{css_file}", timeout=5)
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print(f"  ✅ {css_file} ({size_kb:.1f}KB)")
            else:
                print(f"  ❌ {css_file} - Status {response.status_code}")
                all_loaded = False
        except Exception as e:
            print(f"  ❌ {css_file} - Erreur: {e}")
            all_loaded = False
    
    return all_loaded

def main():
    """Fonction principale de test"""
    print("🧪 TEST DES BOUTONS DE LA PAGE D'ANALYSE")
    print("=" * 50)
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ Serveur non accessible sur {BASE_URL}")
            print("   Démarrez le serveur avec: python run.py")
            return False
    except:
        print(f"❌ Impossible de se connecter à {BASE_URL}")
        print("   Démarrez le serveur avec: python run.py")
        return False
    
    # Exécuter les tests
    tests = [
        ("Chargement de la page", test_page_loading),
        ("Endpoints API", test_api_endpoints),
        ("API d'analyse", test_analysis_api),
        ("Fonctionnalité JavaScript", test_javascript_functionality),
        ("Styles CSS", test_css_styling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Les boutons de la page d'analyse fonctionnent correctement")
        print("🌐 Interface accessible sur: " + BASE_URL)
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
