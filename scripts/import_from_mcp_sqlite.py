#!/usr/bin/env python3
"""
Script pour importer directement depuis SQLite (via données JSON récupérées via MCP)
vers Supabase PostgreSQL.

UTILISATION:
1. Dans Cursor, utilisez MCP sqlite pour récupérer les données:
   mcp_sqlite_query: SELECT * FROM document_processing WHERE status='extracted'
   
2. Copiez les résultats JSON et collez-les dans un fichier documents_export_complete.json

3. Configurez DATABASE_URL:
   export DATABASE_URL="postgresql://postgres:password@project.supabase.co:5432/postgres"

4. Exécutez:
   python scripts/import_from_mcp_sqlite.py documents_export_complete.json
"""

import os
import sys
import json
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def escape_for_sql(value):
    """Échappe une valeur pour PostgreSQL"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)

def import_documents(json_file):
    """Importe les documents depuis JSON vers Supabase"""
    
    # Lire JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL non configuré!")
        print("Configurez: export DATABASE_URL='postgresql://...'")
        sys.exit(1)
    
    print(f"📦 {len(documents)} documents à importer")
    print(f"🔗 Connexion à Supabase...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        imported = 0
        errors = 0
        
        for doc in documents:
            try:
                # Convertir les timestamps
                created_at = doc.get('created_at')
                updated_at = doc.get('updated_at')
                
                if created_at:
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at = None
                
                if updated_at:
                    try:
                        updated_at = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                    except:
                        updated_at = None
                
                cur.execute("""
                    INSERT INTO document_processing 
                    (file_path, file_name, brand, file_type, file_size, status, 
                     extraction_data, analysis_data, structured_data, enriched_data, 
                     validation_notes, error_message, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (file_path) DO UPDATE SET
                        file_name = EXCLUDED.file_name,
                        brand = EXCLUDED.brand,
                        file_type = EXCLUDED.file_type,
                        file_size = EXCLUDED.file_size,
                        status = EXCLUDED.status,
                        extraction_data = EXCLUDED.extraction_data,
                        analysis_data = EXCLUDED.analysis_data,
                        structured_data = EXCLUDED.structured_data,
                        enriched_data = EXCLUDED.enriched_data,
                        validation_notes = EXCLUDED.validation_notes,
                        error_message = EXCLUDED.error_message,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    doc.get('file_path'),
                    doc.get('file_name'),
                    doc.get('brand'),
                    doc.get('file_type'),
                    doc.get('file_size'),
                    doc.get('status', 'extracted'),
                    doc.get('extraction_data'),
                    doc.get('analysis_data'),
                    doc.get('structured_data'),
                    doc.get('enriched_data'),
                    doc.get('validation_notes'),
                    doc.get('error_message'),
                    created_at,
                    updated_at
                ))
                
                imported += 1
                if imported % 10 == 0:
                    print(f"  ✓ {imported}/{len(documents)}...")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Erreur {doc.get('file_name')}: {e}")
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print()
        print("=" * 60)
        print(f"✅ Migration terminée!")
        print(f"   Importés: {imported} | Erreurs: {errors}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_from_mcp_sqlite.py <fichier_json>")
        sys.exit(1)
    
    import_documents(sys.argv[1])
