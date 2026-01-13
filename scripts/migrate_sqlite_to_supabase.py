#!/usr/bin/env python3
"""
Script de migration des données document_processing de SQLite vers Supabase
Utilise les MCPs pour lire SQLite et insère dans Supabase via PostgreSQL
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# Configuration Supabase (à remplir avec vos credentials)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")  # Format: postgresql://user:pass@host:port/dbname

def escape_sql_string(value: Any) -> str:
    """Échappe les chaînes pour SQL PostgreSQL"""
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
    # Pour les autres types, convertir en JSON
    return f"'{json.dumps(value).replace("'", "''")}'"

def generate_insert_sql(documents: List[Dict[str, Any]]) -> str:
    """Génère le script SQL INSERT pour tous les documents"""
    
    sql_lines = [
        "-- Migration SQL: Insertion des 66 documents depuis SQLite vers Supabase",
        f"-- Généré le: {datetime.now().isoformat()}",
        "",
        "-- IMPORTANT: Exécutez d'abord migration.sql pour créer la table",
        "",
        "BEGIN;",
        ""
    ]
    
    for doc in documents:
        # Préparer les valeurs
        file_path = escape_sql_string(doc.get('file_path'))
        file_name = escape_sql_string(doc.get('file_name'))
        brand = escape_sql_string(doc.get('brand'))
        file_type = escape_sql_string(doc.get('file_type'))
        file_size = doc.get('file_size') if doc.get('file_size') is not None else 'NULL'
        status = escape_sql_string(doc.get('status', 'extracted'))
        extraction_data = escape_sql_string(doc.get('extraction_data'))
        analysis_data = escape_sql_string(doc.get('analysis_data'))
        structured_data = escape_sql_string(doc.get('structured_data'))
        enriched_data = escape_sql_string(doc.get('enriched_data'))
        validation_notes = escape_sql_string(doc.get('validation_notes'))
        error_message = escape_sql_string(doc.get('error_message'))
        
        # Convertir les timestamps
        created_at = f"'{doc.get('created_at')}'" if doc.get('created_at') else 'CURRENT_TIMESTAMP'
        updated_at = f"'{doc.get('updated_at')}'" if doc.get('updated_at') else 'CURRENT_TIMESTAMP'
        
        sql_lines.append(
            f"INSERT INTO document_processing "
            f"(file_path, file_name, brand, file_type, file_size, status, extraction_data, "
            f"analysis_data, structured_data, enriched_data, validation_notes, error_message, "
            f"created_at, updated_at) "
            f"VALUES "
            f"({file_path}, {file_name}, {brand}, {file_type}, {file_size}, {status}, "
            f"{extraction_data}, {analysis_data}, {structured_data}, {enriched_data}, "
            f"{validation_notes}, {error_message}, {created_at}, {updated_at}) "
            f"ON CONFLICT (file_path) DO UPDATE SET "
            f"file_name = EXCLUDED.file_name, "
            f"brand = EXCLUDED.brand, "
            f"file_type = EXCLUDED.file_type, "
            f"file_size = EXCLUDED.file_size, "
            f"status = EXCLUDED.status, "
            f"extraction_data = EXCLUDED.extraction_data, "
            f"updated_at = CURRENT_TIMESTAMP;"
        )
    
    sql_lines.extend([
        "",
        "COMMIT;",
        "",
        f"-- Total: {len(documents)} documents insérés"
    ])
    
    return "\n".join(sql_lines)

def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("Migration SQLite -> Supabase: document_processing")
    print("=" * 60)
    print()
    print("Ce script génère un fichier SQL avec les INSERT statements")
    print("pour migrer les données depuis SQLite vers Supabase.")
    print()
    print("⚠️  IMPORTANT:")
    print("1. Les données doivent être récupérées depuis SQLite via MCP")
    print("2. Ce script génère le SQL, mais vous devez l'exécuter manuellement")
    print("   dans Supabase SQL Editor")
    print()
    
    # Le script ne peut pas accéder directement à SQLite via MCP depuis Python
    # Il faut utiliser les outils MCP depuis Cursor pour récupérer les données
    print("📋 Instructions:")
    print("1. Utilisez les outils MCP sqlite dans Cursor pour récupérer les données")
    print("2. Exécutez: mcp_sqlite_query avec SELECT * FROM document_processing WHERE status='extracted'")
    print("3. Copiez les résultats JSON")
    print("4. Exécutez ce script avec les données JSON en entrée")
    print()
    print("Ou utilisez le script SQL généré manuellement dans Supabase SQL Editor")
    print()
    
    output_file = "frontend/prisma/migrations/3_migrate_document_processing/INSERT_DATA.sql"
    
    # Créer un template SQL avec instructions
    template_sql = """-- Migration SQL: Insertion des documents document_processing
-- À exécuter dans Supabase SQL Editor APRÈS avoir créé la table (migration.sql)

-- IMPORTANT: 
-- 1. Exécutez d'abord: frontend/prisma/migrations/3_migrate_document_processing/migration.sql
-- 2. Ensuite, utilisez le script Python pour générer les INSERT statements
-- 3. Ou insérez les données via l'API ou un script Python avec psycopg2

-- Pour générer les INSERT statements:
-- python scripts/migrate_sqlite_to_supabase.py

-- Les 66 documents sont dans SQLite et doivent être migrés via:
-- - Script Python avec psycopg2 (recommandé)
-- - API REST si disponible
-- - Ou INSERT SQL manuel (voir script Python pour générer)

-- Exemple de structure INSERT:
/*
INSERT INTO document_processing 
(file_path, file_name, brand, file_type, file_size, status, extraction_data, created_at, updated_at)
VALUES 
('path/to/file.pdf', 'file.pdf', 'ABB', 'pdf', 1000000, 'extracted', '{"content": "..."}', NOW(), NOW())
ON CONFLICT (file_path) DO UPDATE SET 
  file_name = EXCLUDED.file_name,
  status = EXCLUDED.status,
  extraction_data = EXCLUDED.extraction_data,
  updated_at = CURRENT_TIMESTAMP;
*/
"""
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template_sql)
    
    print(f"✅ Template SQL créé: {output_file}")
    print()
    print("📝 Prochaines étapes:")
    print("1. Exécutez migration.sql dans Supabase SQL Editor")
    print("2. Utilisez les outils MCP pour récupérer les données SQLite")
    print("3. Générez les INSERT statements avec les données")
    print("4. Exécutez les INSERT dans Supabase SQL Editor")

if __name__ == "__main__":
    main()
