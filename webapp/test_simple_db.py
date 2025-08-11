#!/usr/bin/env python3
"""
Test simple de connexion à la base de données Neon PostgreSQL
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

def test_simple_connection():
    """Test simple avec psycopg2"""
    try:
        import psycopg2
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL non définie")
            return False
        
        print("🗄️ Test de connexion simple à Neon PostgreSQL")
        print("=" * 50)
        print(f"🔗 URL: {db_url[:50]}...")
        
        # Test de connexion directe
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test simple
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion réussie!")
        print(f"📊 Version PostgreSQL: {version[0][:50]}...")
        
        # Test de création de table simple
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Test d'insertion
        cursor.execute("""
            INSERT INTO test_table (name) VALUES (%s) RETURNING id;
        """, ("test_connection",))
        
        test_id = cursor.fetchone()[0]
        print(f"✅ Test d'écriture réussi! ID: {test_id}")
        
        # Test de lecture
        cursor.execute("SELECT COUNT(*) FROM test_table;")
        count = cursor.fetchone()[0]
        print(f"✅ Test de lecture réussi! Nombre d'enregistrements: {count}")
        
        # Nettoyer
        cursor.execute("DELETE FROM test_table WHERE name = %s;", ("test_connection",))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Tous les tests sont passés!")
        return True
        
    except ImportError:
        print("❌ psycopg2 non installé. Installez avec: pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_sqlalchemy_connection():
    """Test avec SQLAlchemy"""
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL non définie")
            return False
        
        print("\n🗄️ Test de connexion SQLAlchemy")
        print("=" * 50)
        
        # Créer le moteur
        engine = create_engine(db_url, echo=False)
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ SQLAlchemy connexion réussie! Test: {test_value}")
            
        print("🎉 SQLAlchemy fonctionne!")
        return True
        
    except ImportError:
        print("❌ SQLAlchemy non installé. Installez avec: pip install SQLAlchemy")
        return False
        
    except Exception as e:
        print(f"❌ Erreur SQLAlchemy: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Tests de connexion à la base de données Neon")
    print("=" * 60)
    
    # Test 1: Connexion simple
    simple_ok = test_simple_connection()
    
    # Test 2: SQLAlchemy
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    if simple_ok and sqlalchemy_ok:
        print("🎉 Tous les tests sont passés!")
        print("✅ La base de données Neon est prête")
        print("Vous pouvez maintenant démarrer l'application:")
        print("   python run.py")
    elif simple_ok:
        print("⚠️ Connexion de base OK, mais problème avec SQLAlchemy")
        print("Vérifiez la version de SQLAlchemy:")
        print("   pip install --upgrade SQLAlchemy")
    else:
        print("❌ Problème de connexion à la base de données")
        print("Vérifiez votre URL de connexion dans le fichier .env")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
