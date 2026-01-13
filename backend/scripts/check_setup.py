#!/usr/bin/env python3
"""
Script pour vérifier que l'installation est correcte
"""

import sys
import os

def check_imports():
    """Vérifier que tous les modules sont installés"""
    print("Vérification des imports...")
    try:
        import fastapi
        import sqlalchemy
        import openai
        import pydantic
        print("✅ Tous les modules sont installés")
        return True
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
        print("Exécutez: pip install -r requirements.txt")
        return False

def check_env():
    """Vérifier les variables d'environnement"""
    print("\nVérification des variables d'environnement...")
    from app.core.config import settings
    
    issues = []
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
        issues.append("OPENAI_API_KEY n'est pas défini")
    if not settings.SECRET_KEY or settings.SECRET_KEY == "change-me-in-production":
        issues.append("SECRET_KEY doit être changé en production")
    
    if issues:
        print("⚠️  Problèmes détectés:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Variables d'environnement OK")
        return True

def check_database():
    """Vérifier la base de données"""
    print("\nVérification de la base de données...")
    try:
        from app.core.database import engine, Base
        from app.models import User
        
        # Tester la connexion
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Vérifier que les tables existent
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de base de données: {e}")
        print("Exécutez: python scripts/init_db.py")
        return False

def main():
    print("=" * 50)
    print("Vérification de l'installation")
    print("=" * 50)
    
    all_ok = True
    all_ok &= check_imports()
    all_ok &= check_env()
    all_ok &= check_database()
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ Installation complète et fonctionnelle!")
    else:
        print("❌ Des problèmes ont été détectés")
        sys.exit(1)

if __name__ == "__main__":
    main()
