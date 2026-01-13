#!/usr/bin/env python3
"""
Génère le script SQL INSERT complet pour migrer les documents vers Supabase
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
        # Limiter la longueur si trop long (pour les très gros contenus)
        if len(escaped) > 100000:
            escaped = escaped[:100000] + "... [truncated]"
        return f"'{escaped}'"
    return f"'{json.dumps(value).replace("'", "''")}'"

# Les 65 documents (id 1 manque, donc 65 au lieu de 66)
# Note: Les données complètes doivent être passées en argument ou lues depuis un fichier

if __name__ == "__main__":
    print("Ce script génère le SQL INSERT depuis les données JSON")
    print("Utilisez plutôt: python scripts/import_documents_to_supabase.py documents_export.json")
