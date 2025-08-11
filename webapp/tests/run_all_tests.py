#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Principal pour Exécuter Tous les Tests TradingAgents
Suite complète de tests pour l'interface moderne
"""

import os
import sys
import time
import subprocess
import requests
import signal
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
WEBAPP_DIR = Path(__file__).parent.parent
TEST_DIR = Path(__file__).parent

class TestRunner:
    """Gestionnaire d'exécution des tests"""
    
    def __init__(self):
        self.server_process = None
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Afficher l'en-tête des tests"""
        print("🧪" + "=" * 70)
        print("   SUITE DE TESTS TRADINGAGENTS INTERFACE MODERNE")
        print("=" * 72)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL de test: {BASE_URL}")
        print(f"📁 Répertoire: {WEBAPP_DIR}")
        print("=" * 72)
    
    def check_dependencies(self):
        """Vérifier les dépendances nécessaires"""
        print("\n🔍 Vérification des dépendances...")
        
        dependencies = {
            'pytest': 'pytest',
            'selenium': 'selenium',
            'requests': 'requests',
            'flask': 'flask'
        }
        
        missing = []
        
        for name, module in dependencies.items():
            try:
                __import__(module)
                print(f"✅ {name}")
            except ImportError:
                print(f"❌ {name} - MANQUANT")
                missing.append(name)
        
        if missing:
            print(f"\n⚠️ Dépendances manquantes: {', '.join(missing)}")
            print("Installez avec: pip install " + " ".join(missing))
            return False
        
        return True
    
    def start_server(self):
        """Démarrer le serveur Flask pour les tests"""
        print("\n🚀 Démarrage du serveur de test...")
        
        # Vérifier si le serveur est déjà en cours d'exécution
        try:
            response = requests.get(BASE_URL, timeout=2)
            if response.status_code == 200:
                print("✅ Serveur déjà en cours d'exécution")
                return True
        except:
            pass
        
        # Démarrer le serveur
        try:
            env = os.environ.copy()
            env['FLASK_ENV'] = 'testing'
            env['TESTING'] = 'true'
            
            self.server_process = subprocess.Popen(
                [sys.executable, 'run.py'],
                cwd=WEBAPP_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Attendre que le serveur démarre
            for i in range(30):  # 30 secondes maximum
                try:
                    response = requests.get(BASE_URL, timeout=1)
                    if response.status_code == 200:
                        print("✅ Serveur démarré avec succès")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Impossible de démarrer le serveur")
            return False
            
        except Exception as e:
            print(f"❌ Erreur démarrage serveur: {e}")
            return False
    
    def stop_server(self):
        """Arrêter le serveur Flask"""
        if self.server_process:
            print("\n🛑 Arrêt du serveur...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Serveur arrêté")
    
    def run_backend_tests(self):
        """Exécuter les tests backend"""
        print("\n🔧 Tests Backend API...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(TEST_DIR / 'test_backend_api.py'),
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=WEBAPP_DIR)
            
            success = result.returncode == 0
            self.test_results['backend'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                print("✅ Tests backend réussis")
            else:
                print("❌ Tests backend échoués")
                print(result.stderr[:500])  # Afficher les premières erreurs
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur tests backend: {e}")
            self.test_results['backend'] = {'success': False, 'error': str(e)}
            return False
    
    def run_frontend_tests(self):
        """Exécuter les tests frontend"""
        print("\n🎨 Tests Frontend JavaScript...")
        print("-" * 40)
        
        # Les tests frontend sont dans un fichier HTML
        # On vérifie juste que le fichier existe et que les pages se chargent
        try:
            frontend_test_file = TEST_DIR / 'test_frontend.html'
            if frontend_test_file.exists():
                print("✅ Fichier de tests frontend trouvé")
                
                # Vérifier que les pages principales se chargent
                pages = ['/', '/automation', '/backtesting', '/demo']
                all_pages_ok = True
                
                for page in pages:
                    try:
                        response = requests.get(f"{BASE_URL}{page}", timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Page {page}")
                        else:
                            print(f"❌ Page {page} - Status {response.status_code}")
                            all_pages_ok = False
                    except Exception as e:
                        print(f"❌ Page {page} - Erreur: {e}")
                        all_pages_ok = False
                
                self.test_results['frontend'] = {'success': all_pages_ok}
                return all_pages_ok
            else:
                print("❌ Fichier de tests frontend non trouvé")
                self.test_results['frontend'] = {'success': False}
                return False
                
        except Exception as e:
            print(f"❌ Erreur tests frontend: {e}")
            self.test_results['frontend'] = {'success': False, 'error': str(e)}
            return False
    
    def run_e2e_tests(self):
        """Exécuter les tests end-to-end"""
        print("\n🌐 Tests End-to-End (Selenium)...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                str(TEST_DIR / 'test_e2e_selenium.py'),
                '-v', '--tb=short', '-x'  # Arrêter au premier échec
            ], capture_output=True, text=True, cwd=WEBAPP_DIR)
            
            success = result.returncode == 0
            self.test_results['e2e'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                print("✅ Tests E2E réussis")
            else:
                print("❌ Tests E2E échoués")
                if "WebDriverException" in result.stderr:
                    print("⚠️ Selenium WebDriver non configuré (normal)")
                else:
                    print(result.stderr[:500])
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur tests E2E: {e}")
            self.test_results['e2e'] = {'success': False, 'error': str(e)}
            return False
    
    def run_performance_tests(self):
        """Exécuter les tests de performance"""
        print("\n⚡ Tests de Performance...")
        print("-" * 40)
        
        try:
            # Exécuter le script de performance directement
            result = subprocess.run([
                sys.executable, str(TEST_DIR / 'test_performance.py')
            ], capture_output=True, text=True, cwd=WEBAPP_DIR)
            
            success = result.returncode == 0
            self.test_results['performance'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                print("✅ Tests de performance réussis")
            else:
                print("❌ Tests de performance échoués")
                print(result.stderr[:500])
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur tests performance: {e}")
            self.test_results['performance'] = {'success': False, 'error': str(e)}
            return False
    
    def run_compatibility_tests(self):
        """Exécuter les tests de compatibilité"""
        print("\n🌍 Tests de Compatibilité Navigateur...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, str(TEST_DIR / 'test_browser_compatibility.py')
            ], capture_output=True, text=True, cwd=WEBAPP_DIR)
            
            success = result.returncode == 0
            self.test_results['compatibility'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                print("✅ Tests de compatibilité réussis")
            else:
                print("❌ Tests de compatibilité échoués")
                if "WebDriverException" in result.stderr:
                    print("⚠️ Navigateurs non configurés (normal)")
                else:
                    print(result.stderr[:500])
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur tests compatibilité: {e}")
            self.test_results['compatibility'] = {'success': False, 'error': str(e)}
            return False
    
    def generate_report(self):
        """Générer le rapport final"""
        print("\n📊 RAPPORT FINAL")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"📈 Résultats: {passed_tests}/{total_tests} suites de tests réussies")
        print(f"⏱️ Durée totale: {(self.end_time - self.start_time):.1f} secondes")
        print()
        
        # Détail par suite de tests
        for test_name, result in self.test_results.items():
            status = "✅ RÉUSSI" if result['success'] else "❌ ÉCHOUÉ"
            print(f"{status} - {test_name.capitalize()}")
        
        print()
        
        if passed_tests == total_tests:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("   L'interface TradingAgents est prête pour la production.")
        else:
            print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            print("   Vérifiez les erreurs ci-dessus.")
        
        # Sauvegarder le rapport
        self.save_report()
        
        return passed_tests == total_tests
    
    def save_report(self):
        """Sauvegarder le rapport dans un fichier"""
        try:
            report_file = TEST_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RAPPORT DE TESTS TRADINGAGENTS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Durée: {(self.end_time - self.start_time):.1f}s\n\n")
                
                for test_name, result in self.test_results.items():
                    f.write(f"\n{test_name.upper()}\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Statut: {'RÉUSSI' if result['success'] else 'ÉCHOUÉ'}\n")
                    
                    if 'output' in result:
                        f.write(f"Sortie:\n{result['output']}\n")
                    if 'errors' in result:
                        f.write(f"Erreurs:\n{result['errors']}\n")
                    if 'error' in result:
                        f.write(f"Erreur: {result['error']}\n")
            
            print(f"📄 Rapport sauvegardé: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder le rapport: {e}")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        self.start_time = time.time()
        
        try:
            self.print_header()
            
            # Vérifier les dépendances
            if not self.check_dependencies():
                return False
            
            # Démarrer le serveur
            if not self.start_server():
                return False
            
            # Exécuter les tests
            test_functions = [
                self.run_backend_tests,
                self.run_frontend_tests,
                self.run_performance_tests,
                self.run_e2e_tests,
                self.run_compatibility_tests
            ]
            
            for test_func in test_functions:
                try:
                    test_func()
                except KeyboardInterrupt:
                    print("\n⚠️ Tests interrompus par l'utilisateur")
                    break
                except Exception as e:
                    print(f"❌ Erreur inattendue: {e}")
            
            self.end_time = time.time()
            
            # Générer le rapport
            return self.generate_report()
            
        finally:
            self.stop_server()


def main():
    """Fonction principale"""
    runner = TestRunner()
    
    # Gérer l'interruption clavier
    def signal_handler(sig, frame):
        print("\n⚠️ Interruption détectée...")
        runner.stop_server()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Exécuter les tests
    success = runner.run_all_tests()
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
