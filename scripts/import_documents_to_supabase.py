#!/usr/bin/env python3
"""
Script pour importer les documents depuis SQLite (via données JSON) vers Supabase
Utilise psycopg2 pour se connecter directement à PostgreSQL/Supabase
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any

# Configuration - À MODIFIER avec vos credentials Supabase
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres"
)

def connect_to_supabase():
    """Établit la connexion à Supabase PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à Supabase: {e}")
        print()
        print("💡 Vérifiez votre DATABASE_URL dans .env ou modifiez le script")
        sys.exit(1)

def import_documents_from_json(json_file: str):
    """Importe les documents depuis un fichier JSON vers Supabase"""
    
    # Lire les données JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {json_file}")
        print("💡 Exportez d'abord les données depuis SQLite via MCP")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        sys.exit(1)
    
    print(f"📦 {len(documents)} documents à importer")
    
    # Connexion à Supabase
    conn = connect_to_supabase()
    cur = conn.cursor()
    
    try:
        imported = 0
        errors = 0
        
        for doc in documents:
            try:
                # Préparer les données
                values = (
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
                    doc.get('created_at'),
                    doc.get('updated_at')
                )
                
                # INSERT avec ON CONFLICT
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
                """, values)
                
                imported += 1
                if imported % 10 == 0:
                    print(f"  ✓ {imported}/{len(documents)} documents importés...")
                
            except Exception as e:
                errors += 1
                print(f"  ❌ Erreur pour {doc.get('file_name')}: {e}")
                continue
        
        # Commit
        conn.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Migration terminée!")
        print(f"   - Documents importés: {imported}")
        print(f"   - Erreurs: {errors}")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'import: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("Import documents SQLite -> Supabase")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python import_documents_to_supabase.py <fichier_json>")
        print()
        print("Exemple:")
        print("  python import_documents_to_supabase.py documents_export.json")
        print()
        print("💡 Pour exporter les données depuis SQLite:")
        print("   1. Utilisez MCP sqlite dans Cursor")
        print("   2. Exécutez: SELECT * FROM document_processing WHERE status='extracted'")
        print("   3. Sauvegardez les résultats en JSON")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"❌ Fichier non trouvé: {json_file}")
        sys.exit(1)
    
    # Vérifier DATABASE_URL
    if "YOUR-PASSWORD" in DATABASE_URL or "YOUR-PROJECT" in DATABASE_URL:
        print("⚠️  ATTENTION: DATABASE_URL n'est pas configuré!")
        print()
        print("Configurez DATABASE_URL dans .env ou modifiez le script:")
        print("  DATABASE_URL=postgresql://postgres:password@project.supabase.co:5432/postgres")
        print()
        response = input("Continuer quand même? (o/N): ")
        if response.lower() != 'o':
            sys.exit(1)
    
    import_documents_from_json(json_file)

if __name__ == "__main__":
    main()
