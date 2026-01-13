#!/usr/bin/env python3
"""
Crée le fichier JSON complet avec toutes les données depuis SQLite
À exécuter depuis Cursor avec les données récupérées via MCP
"""

import json
import sys

# Les données complètes doivent être passées ici ou lues depuis un fichier
# Pour l'instant, ce script sert de template

def create_json_export(documents_data):
    """Crée le fichier JSON d'export"""
    output_file = "documents_export_complete.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(documents_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Fichier JSON créé: {output_file}")
    print(f"   - {len(documents_data)} documents exportés")
    return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("Export documents SQLite -> JSON")
    print("=" * 60)
    print()
    print("💡 Pour utiliser ce script:")
    print("   1. Récupérez les données via MCP sqlite:")
    print("      SELECT * FROM document_processing WHERE status='extracted'")
    print("   2. Copiez les résultats JSON")
    print("   3. Collez-les dans ce script ou passez-les en argument")
    print()
    print("Ou utilisez directement le script d'import Python qui peut")
    print("se connecter à Supabase si DATABASE_URL est configuré.")
