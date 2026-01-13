#!/usr/bin/env python3
"""
Script de migration des données document_processing de SQLite vers Supabase
Ce script génère un fichier SQL avec les INSERT statements pour Supabase
"""

import os
import sys
import json
from datetime import datetime

# Note: Ce script doit être exécuté avec accès à la base SQLite via MCP
# Pour l'instant, il génère un template SQL

def escape_sql_string(value):
    """Échappe les chaînes pour SQL"""
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return "'" + value.replace("'", "''").replace("\\", "\\\\") + "'"
    return str(value)

def generate_migration_sql():
    """Génère le script SQL de migration"""
    
    sql_content = """-- Migration SQL pour Supabase
-- Import des données document_processing depuis SQLite
-- Date de génération: {date}

-- Note: Les données doivent être insérées via l'API ou un script Python
-- car nous n'avons pas accès direct à la base SQLite depuis ici.

-- Structure de la table (déjà créée par la migration 3_migrate_document_processing)
-- Les données seront insérées via l'API /api/admin/import-documents ou similaire

-- Pour insérer les données, utilisez le script Python:
-- python scripts/import_documents_from_sqlite.py

""".format(date=datetime.now().isoformat())
    
    return sql_content

if __name__ == "__main__":
    output_file = "frontend/prisma/migrations/3_migrate_document_processing/data_insert.sql"
    
    # Créer le répertoire si nécessaire
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    sql_content = generate_migration_sql()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✅ Script SQL généré: {output_file}")
    print("⚠️  Note: Les données doivent être insérées via l'API ou un script Python")
    print("   car nous n'avons pas accès direct à la base SQLite MCP depuis Python")
