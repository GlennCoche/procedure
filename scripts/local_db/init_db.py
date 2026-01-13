#!/usr/bin/env python3
"""
Script d'initialisation de la base de données SQLite locale
Utilise le MCP sqlite pour créer les tables
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def init_database():
    """Initialiser la base de données SQLite locale"""
    db_path = Path(__file__).parent / "documents.db"
    schema_path = Path(__file__).parent / "schema.sql"
    
    print(f"📦 Initialisation de la base de données locale...")
    print(f"   Chemin DB: {db_path}")
    print(f"   Schéma: {schema_path}")
    
    # Vérifier que le schéma existe
    if not schema_path.exists():
        print(f"❌ Erreur: Le fichier schema.sql n'existe pas: {schema_path}")
        return False
    
    # Lire le schéma SQL
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print(f"\n✅ Schéma SQL chargé ({len(schema_sql)} caractères)")
    print(f"\n⚠️  Note: Ce script prépare le schéma SQL.")
    print(f"   Pour créer les tables, utilisez le MCP sqlite avec:")
    print(f"   - execute_sql: Exécuter le contenu de schema.sql")
    print(f"   - list_tables: Vérifier que les tables sont créées")
    print(f"   - get_table_schema: Valider la structure de chaque table")
    
    print(f"\n📋 Tables à créer:")
    print(f"   - document_processing")
    print(f"   - document_images")
    print(f"   - local_procedures")
    print(f"   - local_tips")
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
