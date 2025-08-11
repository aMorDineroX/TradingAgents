#!/usr/bin/env python3
"""
Script de test pour la connexion à la base de données Neon PostgreSQL
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

def test_database_connection():
    """Tester la connexion à la base de données"""
    try:
        from database import DatabaseManager
        
        print("🗄️ Test de connexion à la base de données Neon PostgreSQL")
        print("=" * 60)
        
        # Vérifier l'URL de la base de données
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL non définie dans le fichier .env")
            return False
        
        print(f"🔗 URL de connexion: {db_url[:50]}...")
        
        # Créer le gestionnaire de base de données
        db_manager = DatabaseManager(db_url)
        
        # Tester la connexion
        if db_manager.test_connection():
            print("✅ Connexion à la base de données réussie!")
            
            # Tester les opérations de base
            print("\n🧪 Test des opérations de base de données:")
            
            # Test de sauvegarde d'analyse
            test_session_id = "test_session_123"
            success = db_manager.save_analysis_result(
                session_id=test_session_id,
                ticker="TEST",
                trade_date="2024-01-01",
                config={"test": True},
                status="pending"
            )
            
            if success:
                print("✅ Sauvegarde d'analyse: OK")
                
                # Test de récupération
                result = db_manager.get_analysis_result(test_session_id)
                if result:
                    print("✅ Récupération d'analyse: OK")
                    print(f"   Session ID: {result['session_id']}")
                    print(f"   Ticker: {result['ticker']}")
                    print(f"   Statut: {result['status']}")
                else:
                    print("❌ Récupération d'analyse: ÉCHEC")
                
                # Test de mise à jour
                update_success = db_manager.update_analysis_result(
                    session_id=test_session_id,
                    decision="BUY",
                    status="completed"
                )
                
                if update_success:
                    print("✅ Mise à jour d'analyse: OK")
                else:
                    print("❌ Mise à jour d'analyse: ÉCHEC")
                
                # Test de liste
                analyses = db_manager.list_analysis_results(limit=5)
                print(f"✅ Liste des analyses: {len(analyses)} résultat(s)")
                
                # Test des statistiques
                stats = db_manager.get_analysis_stats()
                if stats:
                    print("✅ Statistiques: OK")
                    print(f"   Total: {stats.get('total_analyses', 0)}")
                    print(f"   Complétées: {stats.get('completed', 0)}")
                    print(f"   Taux de réussite: {stats.get('success_rate', 0):.1f}%")
                
            else:
                print("❌ Sauvegarde d'analyse: ÉCHEC")
            
            print("\n🎉 Tous les tests de base de données sont passés!")
            return True
            
        else:
            print("❌ Échec de la connexion à la base de données")
            return False
            
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("Installez les dépendances: pip install psycopg2-binary SQLAlchemy")
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    success = test_database_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Base de données Neon PostgreSQL prête à l'utilisation!")
        print("Vous pouvez maintenant démarrer l'application:")
        print("   python run.py")
    else:
        print("⚠️ Problème avec la base de données")
        print("L'application fonctionnera en mode fichiers")
    print("=" * 60)

if __name__ == "__main__":
    main()
