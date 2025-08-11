#!/usr/bin/env python3
"""
Tests de Performance pour TradingAgents Interface Moderne
Tests de charge, stress et performance des API et interface
"""

import pytest
import time
import asyncio
import aiohttp
import requests
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys
import json

# Configuration
BASE_URL = "http://localhost:5000"
MAX_RESPONSE_TIME = 2.0  # Temps de réponse maximum acceptable (secondes)
CONCURRENT_USERS = 10    # Nombre d'utilisateurs simultanés pour les tests de charge

class TestAPIPerformance:
    """Tests de performance des API"""
    
    def test_api_response_times(self):
        """Test des temps de réponse des API principales"""
        endpoints = [
            "/api/status",
            "/api/list_results",
            "/api/automation/status",
            "/api/brokerage/status",
            "/api/monitoring/positions",
            "/api/monitoring/alerts"
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            times = []
            
            # Faire 5 requêtes pour chaque endpoint
            for _ in range(5):
                start_time = time.time()
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                    else:
                        print(f"⚠️ {endpoint} returned {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Error testing {endpoint}: {e}")
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                response_times[endpoint] = {
                    'average': avg_time,
                    'maximum': max_time,
                    'samples': len(times)
                }
                
                # Vérifier que le temps de réponse est acceptable
                assert avg_time < MAX_RESPONSE_TIME, f"{endpoint} trop lent: {avg_time:.3f}s"
                
                print(f"✅ {endpoint}: {avg_time:.3f}s avg, {max_time:.3f}s max")
        
        return response_times
    
    def test_concurrent_requests(self):
        """Test de requêtes simultanées"""
        endpoint = "/api/status"
        num_requests = 20
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'status_code': 0,
                    'response_time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Lancer les requêtes en parallèle
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyser les résultats
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        success_rate = len(successful_requests) / len(results) * 100
        
        if successful_requests:
            avg_response_time = statistics.mean([r['response_time'] for r in successful_requests])
            max_response_time = max([r['response_time'] for r in successful_requests])
            
            print(f"✅ Concurrent requests: {success_rate:.1f}% success rate")
            print(f"   Average response time: {avg_response_time:.3f}s")
            print(f"   Maximum response time: {max_response_time:.3f}s")
            
            # Vérifier que le taux de succès est acceptable
            assert success_rate >= 95, f"Taux de succès trop bas: {success_rate:.1f}%"
            assert avg_response_time < MAX_RESPONSE_TIME * 2, f"Temps de réponse trop élevé sous charge: {avg_response_time:.3f}s"
        
        if failed_requests:
            print(f"⚠️ {len(failed_requests)} requêtes échouées")
            for req in failed_requests[:3]:  # Afficher les 3 premières erreurs
                print(f"   Error: {req.get('error', 'Unknown')}")
    
    def test_memory_usage_simulation(self):
        """Test de simulation d'utilisation mémoire"""
        # Simuler plusieurs analyses simultanées (sans les lancer vraiment)
        endpoint = "/api/list_results"
        
        # Faire plusieurs requêtes pour simuler l'utilisation
        for i in range(50):
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                if response.status_code != 200:
                    print(f"⚠️ Request {i+1} failed with status {response.status_code}")
                    
                # Petite pause pour éviter de surcharger
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request {i+1} failed: {e}")
                break
        
        print("✅ Memory usage simulation completed")


class TestPageLoadPerformance:
    """Tests de performance de chargement des pages"""
    
    def test_static_assets_loading(self):
        """Test du chargement des assets statiques"""
        static_files = [
            "/static/css/modern-design.css",
            "/static/css/navigation.css",
            "/static/css/charts.css",
            "/static/js/modern-ui.js",
            "/static/js/charts.js",
            "/static/js/advanced-ux.js"
        ]
        
        for asset in static_files:
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}{asset}", timeout=10)
                end_time = time.time()
                
                load_time = end_time - start_time
                
                assert response.status_code == 200, f"Asset {asset} not found"
                assert load_time < 1.0, f"Asset {asset} trop lent: {load_time:.3f}s"
                
                print(f"✅ {asset}: {load_time:.3f}s")
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Failed to load {asset}: {e}")
    
    def test_page_sizes(self):
        """Test de la taille des pages"""
        pages = [
            "/",
            "/automation",
            "/backtesting",
            "/demo",
            "/config"
        ]
        
        max_page_size = 500 * 1024  # 500KB maximum par page
        
        for page in pages:
            try:
                response = requests.get(f"{BASE_URL}{page}", timeout=10)
                
                if response.status_code == 200:
                    page_size = len(response.content)
                    page_size_kb = page_size / 1024
                    
                    print(f"✅ {page}: {page_size_kb:.1f}KB")
                    
                    # Vérifier que la page n'est pas trop lourde
                    assert page_size < max_page_size, f"Page {page} trop lourde: {page_size_kb:.1f}KB"
                else:
                    print(f"⚠️ {page} returned status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error loading {page}: {e}")


class TestStressTest:
    """Tests de stress et de charge"""
    
    def test_rapid_requests(self):
        """Test de requêtes rapides successives"""
        endpoint = "/api/status"
        num_requests = 100
        max_time = 30  # 30 secondes maximum pour 100 requêtes
        
        start_time = time.time()
        successful_requests = 0
        
        for i in range(num_requests):
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                if response.status_code == 200:
                    successful_requests += 1
            except:
                pass  # Ignorer les erreurs pour ce test de stress
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success_rate = successful_requests / num_requests * 100
        requests_per_second = successful_requests / total_time
        
        print(f"✅ Stress test: {successful_requests}/{num_requests} requests in {total_time:.2f}s")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Requests per second: {requests_per_second:.1f}")
        
        # Vérifications
        assert total_time < max_time, f"Test trop lent: {total_time:.2f}s"
        assert success_rate >= 80, f"Taux de succès trop bas sous stress: {success_rate:.1f}%"
    
    def test_sustained_load(self):
        """Test de charge soutenue"""
        endpoint = "/api/status"
        duration = 10  # 10 secondes de test
        concurrent_users = 5
        
        results = []
        stop_time = time.time() + duration
        
        def worker():
            worker_results = []
            while time.time() < stop_time:
                start = time.time()
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                    end = time.time()
                    worker_results.append({
                        'success': response.status_code == 200,
                        'response_time': end - start
                    })
                except:
                    worker_results.append({
                        'success': False,
                        'response_time': 0
                    })
                time.sleep(0.1)  # Petite pause entre les requêtes
            return worker_results
        
        # Lancer les workers
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            for future in as_completed(futures):
                results.extend(future.result())
        
        # Analyser les résultats
        if results:
            successful = [r for r in results if r['success']]
            success_rate = len(successful) / len(results) * 100
            
            if successful:
                avg_response_time = statistics.mean([r['response_time'] for r in successful])
                max_response_time = max([r['response_time'] for r in successful])
                
                print(f"✅ Sustained load test: {len(results)} total requests")
                print(f"   Success rate: {success_rate:.1f}%")
                print(f"   Average response time: {avg_response_time:.3f}s")
                print(f"   Maximum response time: {max_response_time:.3f}s")
                
                # Vérifications
                assert success_rate >= 90, f"Taux de succès insuffisant: {success_rate:.1f}%"
                assert avg_response_time < MAX_RESPONSE_TIME * 1.5, f"Temps de réponse dégradé: {avg_response_time:.3f}s"


class TestResourceUsage:
    """Tests d'utilisation des ressources"""
    
    def test_css_optimization(self):
        """Test de l'optimisation CSS"""
        css_files = [
            "/static/css/modern-design.css",
            "/static/css/navigation.css",
            "/static/css/charts.css"
        ]
        
        total_css_size = 0
        
        for css_file in css_files:
            try:
                response = requests.get(f"{BASE_URL}{css_file}", timeout=10)
                if response.status_code == 200:
                    size = len(response.content)
                    total_css_size += size
                    print(f"✅ {css_file}: {size/1024:.1f}KB")
            except:
                pass
        
        total_css_kb = total_css_size / 1024
        print(f"📊 Total CSS size: {total_css_kb:.1f}KB")
        
        # Vérifier que le CSS total n'est pas trop lourd
        assert total_css_kb < 200, f"CSS trop lourd: {total_css_kb:.1f}KB"
    
    def test_js_optimization(self):
        """Test de l'optimisation JavaScript"""
        js_files = [
            "/static/js/modern-ui.js",
            "/static/js/charts.js",
            "/static/js/advanced-ux.js"
        ]
        
        total_js_size = 0
        
        for js_file in js_files:
            try:
                response = requests.get(f"{BASE_URL}{js_file}", timeout=10)
                if response.status_code == 200:
                    size = len(response.content)
                    total_js_size += size
                    print(f"✅ {js_file}: {size/1024:.1f}KB")
            except:
                pass
        
        total_js_kb = total_js_size / 1024
        print(f"📊 Total JS size: {total_js_kb:.1f}KB")
        
        # Vérifier que le JavaScript total n'est pas trop lourd
        assert total_js_kb < 300, f"JavaScript trop lourd: {total_js_kb:.1f}KB"


def run_performance_benchmark():
    """Exécuter un benchmark complet"""
    print("🚀 Démarrage du benchmark de performance TradingAgents")
    print("=" * 60)
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ Serveur non accessible sur {BASE_URL}")
            return False
    except:
        print(f"❌ Impossible de se connecter à {BASE_URL}")
        return False
    
    # Exécuter les tests
    test_classes = [
        TestAPIPerformance(),
        TestPageLoadPerformance(),
        TestStressTest(),
        TestResourceUsage()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 {class_name}")
        print("-" * 40)
        
        # Exécuter tous les tests de la classe
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(test_class, method_name)
                    method()
                    passed_tests += 1
                    print(f"✅ {method_name}")
                except Exception as e:
                    print(f"❌ {method_name}: {e}")
    
    # Résumé
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {passed_tests}/{total_tests} tests passés")
    
    if passed_tests == total_tests:
        print("🎉 Tous les tests de performance sont passés!")
        return True
    else:
        print(f"⚠️ {total_tests - passed_tests} tests ont échoué")
        return False


if __name__ == '__main__':
    success = run_performance_benchmark()
    sys.exit(0 if success else 1)
