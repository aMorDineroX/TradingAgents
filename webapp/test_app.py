#!/usr/bin/env python3
"""
Script de test pour TradingAgents Web Interface
Teste les fonctionnalités principales de l'application
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Ajouter le répertoire parent au path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

class TradingAgentsWebTester:
    """Testeur pour l'application web TradingAgents"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Enregistrer le résultat d'un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_server_connection(self):
        """Tester la connexion au serveur"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Connexion serveur", True, "Serveur accessible")
                return True
            else:
                self.log_test("Connexion serveur", False, f"Code de statut: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Connexion serveur", False, f"Erreur: {str(e)}")
            return False
    
    def test_pages_loading(self):
        """Tester le chargement des pages principales"""
        pages = [
            ("/", "Page d'accueil"),
            ("/dashboard", "Tableau de bord"),
            ("/config", "Configuration")
        ]
        
        all_success = True
        for url, name in pages:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(f"Chargement {name}", True, "Page chargée correctement")
                else:
                    self.log_test(f"Chargement {name}", False, f"Code: {response.status_code}")
                    all_success = False
            except Exception as e:
                self.log_test(f"Chargement {name}", False, f"Erreur: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_api_endpoints(self):
        """Tester les endpoints API"""
        endpoints = [
            ("/api/list_results", "GET", "Liste des résultats"),
            ("/api/agents_status", "GET", "Statut des agents"),
            ("/api/config", "GET", "Configuration actuelle"),
            ("/api/presets", "GET", "Préréglages"),
        ]
        
        all_success = True
        for url, method, name in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{url}")
                else:
                    response = self.session.post(f"{self.base_url}{url}")
                
                if response.status_code == 200:
                    # Vérifier que la réponse est du JSON valide
                    try:
                        response.json()
                        self.log_test(f"API {name}", True, "Réponse JSON valide")
                    except:
                        self.log_test(f"API {name}", False, "Réponse JSON invalide")
                        all_success = False
                else:
                    self.log_test(f"API {name}", False, f"Code: {response.status_code}")
                    all_success = False
            except Exception as e:
                self.log_test(f"API {name}", False, f"Erreur: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_config_management(self):
        """Tester la gestion de la configuration"""
        try:
            # Test de récupération de la configuration
            response = self.session.get(f"{self.base_url}/api/config")
            if response.status_code != 200:
                self.log_test("Gestion config", False, "Impossible de récupérer la config")
                return False
            
            config = response.json()
            
            # Test de mise à jour de la configuration
            test_update = {"temperature": 0.5}
            response = self.session.post(
                f"{self.base_url}/api/config/update",
                json=test_update,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.log_test("Gestion config", True, "Mise à jour réussie")
                return True
            else:
                self.log_test("Gestion config", False, f"Erreur mise à jour: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Gestion config", False, f"Erreur: {str(e)}")
            return False
    
    def test_preset_management(self):
        """Tester la gestion des préréglages"""
        try:
            # Test de récupération des préréglages
            response = self.session.get(f"{self.base_url}/api/presets")
            if response.status_code != 200:
                self.log_test("Gestion préréglages", False, "Impossible de récupérer les préréglages")
                return False
            
            presets = response.json()
            
            # Vérifier que les préréglages par défaut existent
            expected_presets = ["fast", "balanced", "deep"]
            for preset in expected_presets:
                if preset not in presets:
                    self.log_test("Gestion préréglages", False, f"Préréglage manquant: {preset}")
                    return False
            
            self.log_test("Gestion préréglages", True, "Préréglages disponibles")
            return True
            
        except Exception as e:
            self.log_test("Gestion préréglages", False, f"Erreur: {str(e)}")
            return False
    
    def test_analysis_validation(self):
        """Tester la validation des données d'analyse"""
        try:
            # Test avec des données invalides
            invalid_data = {
                "ticker": "",  # Ticker vide
                "trade_date": "2025-01-01",  # Date future
                "config": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/start_analysis",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Devrait retourner une erreur
            if response.status_code == 400:
                self.log_test("Validation analyse", True, "Validation des données correcte")
                return True
            else:
                self.log_test("Validation analyse", False, "Validation insuffisante")
                return False
                
        except Exception as e:
            self.log_test("Validation analyse", False, f"Erreur: {str(e)}")
            return False
    
    def test_file_structure(self):
        """Tester la structure des fichiers"""
        required_files = [
            "app.py",
            "config_manager.py",
            "run.py",
            "requirements.txt",
            "README.md",
            "templates/base.html",
            "templates/index.html",
            "templates/dashboard.html",
            "templates/config.html",
            "static/css/custom.css",
            "static/js/app.js"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = current_dir / file_path
            if full_path.exists():
                self.log_test(f"Fichier {file_path}", True, "Existe")
            else:
                self.log_test(f"Fichier {file_path}", False, "Manquant")
                all_exist = False
        
        return all_exist
    
    def test_config_manager(self):
        """Tester le gestionnaire de configuration"""
        try:
            from config_manager import ConfigManager
            
            # Créer une instance temporaire
            config_manager = ConfigManager("webapp/test_configs")
            
            # Test de chargement de configuration
            config = config_manager.load_config()
            if not config:
                self.log_test("ConfigManager", False, "Impossible de charger la config")
                return False
            
            # Test de validation
            test_config = {"temperature": 1.5, "max_tokens": 3000}
            validated = config_manager.validate_config(test_config)
            
            if validated["temperature"] == 1.5 and validated["max_tokens"] == 3000:
                self.log_test("ConfigManager", True, "Validation fonctionnelle")
                return True
            else:
                self.log_test("ConfigManager", False, "Problème de validation")
                return False
                
        except Exception as e:
            self.log_test("ConfigManager", False, f"Erreur: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Démarrage des tests TradingAgents Web Interface\n")
        
        # Tests de structure
        print("📁 Tests de structure des fichiers:")
        self.test_file_structure()
        
        # Tests du gestionnaire de configuration
        print("\n⚙️ Tests du gestionnaire de configuration:")
        self.test_config_manager()
        
        # Tests du serveur (si accessible)
        print("\n🌐 Tests du serveur web:")
        if self.test_server_connection():
            self.test_pages_loading()
            self.test_api_endpoints()
            self.test_config_management()
            self.test_preset_management()
            self.test_analysis_validation()
        else:
            print("⚠️ Serveur non accessible - tests web ignorés")
            print("💡 Démarrez le serveur avec: python run.py")
        
        # Résumé des résultats
        self.print_summary()
    
    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total des tests: {total_tests}")
        print(f"✅ Réussis: {passed_tests}")
        print(f"❌ Échoués: {failed_tests}")
        print(f"📈 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Tests échoués:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*50)
        
        if failed_tests == 0:
            print("🎉 Tous les tests sont passés avec succès!")
        else:
            print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

def main():
    """Fonction principale"""
    tester = TradingAgentsWebTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
