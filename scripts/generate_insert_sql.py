#!/usr/bin/env python3
"""
Génère le script SQL INSERT pour migrer les documents vers Supabase
"""

import json
import sys

def escape_sql(value):
    """Échappe une valeur pour SQL PostgreSQL"""
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Échapper les apostrophes et backslashes
        escaped = value.replace("'", "''").replace("\\", "\\\\")
        return f"'{escaped}'"
    return f"'{json.dumps(value).replace("'", "''")}'"

# Les données récupérées depuis SQLite (65 documents, car id 1 manque)
documents = [
    # ... (toutes les données seront ici)
]

# Pour l'instant, créons un template
print("""-- Script SQL pour insérer les documents dans Supabase
-- Généré automatiquement depuis SQLite

-- IMPORTANT: 
-- 1. Exécutez d'abord: frontend/prisma/migrations/3_migrate_document_processing/migration.sql
-- 2. Ensuite, utilisez le script Python: python scripts/import_documents_to_supabase.py documents_export.json

-- Les données sont dans: documents_export.json
-- Utilisez le script Python pour l'import automatique (recommandé)
""")
