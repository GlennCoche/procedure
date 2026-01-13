#!/usr/bin/env python3
"""
Script de migration depuis SQLite local vers Supabase production
Utilise sqlite MCP pour lire les données validées
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from scripts.local_db.db_manager import LocalDBManager


class MigrationToProduction:
    """
    Gestionnaire de migration vers Supabase
    Utilise sqlite MCP pour exporter les données
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Args:
            db_path: Chemin vers la base SQLite locale
        """
        self.db = LocalDBManager(db_path)
    
    def export_validated_data(self) -> Dict[str, Any]:
        """
        Exporter les données validées depuis SQLite
        
        L'agent Cursor doit utiliser: sqlite.read_records, execute_sql
        
        Returns:
            Instructions pour utiliser sqlite MCP pour exporter
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "read_validated_procedures": {
                        "tool": "sqlite.read_records",
                        "table": "local_procedures",
                        "conditions": {"needs_review": 0},
                        "description": "Lire toutes les procédures validées (needs_review = 0)"
                    },
                    "read_validated_tips": {
                        "tool": "sqlite.read_records",
                        "table": "local_tips",
                        "conditions": {"needs_review": 0},
                        "description": "Lire tous les tips validés"
                    },
                    "get_documents": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT DISTINCT dp.id, dp.file_name, dp.brand
                            FROM document_processing dp
                            INNER JOIN local_procedures p ON p.document_id = dp.id
                            WHERE dp.status = 'validated'
                        """,
                        "description": "Obtenir la liste des documents validés"
                    },
                    "export_statistics": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT 
                                COUNT(DISTINCT dp.id) as documents_count,
                                COUNT(DISTINCT p.id) as procedures_count,
                                COUNT(DISTINCT t.id) as tips_count,
                                AVG(p.quality_score) as avg_procedure_score,
                                AVG(t.quality_score) as avg_tip_score
                            FROM document_processing dp
                            LEFT JOIN local_procedures p ON p.document_id = dp.id
                            LEFT JOIN local_tips t ON t.document_id = dp.id
                            WHERE dp.status = 'validated'
                        """,
                        "description": "Obtenir les statistiques d'export"
                    }
                }
            },
            "export_workflow": [
                "1. Lire toutes les procédures validées via sqlite.read_records",
                "2. Lire tous les tips validés via sqlite.read_records",
                "3. Obtenir les statistiques via sqlite.execute_sql",
                "4. Préparer les données pour Supabase (format Prisma)",
                "5. Exporter en JSON ou directement migrer vers Supabase"
            ],
            "data_structure": {
                "procedures": [
                    {
                        "title": "string",
                        "description": "string",
                        "category": "string",
                        "tags": "JSON array",
                        "steps": "JSON array",
                        "quality_score": "number"
                    }
                ],
                "tips": [
                    {
                        "title": "string",
                        "content": "string",
                        "category": "string",
                        "tags": "JSON array",
                        "source_section": "string"
                    }
                ]
            }
        }
    
    def prepare_for_supabase(self, procedures: List[Dict[str, Any]], 
                            tips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Préparer les données pour l'import Supabase
        
        Args:
            procedures: Liste de procédures
            tips: Liste de tips
        
        Returns:
            Données formatées pour Supabase
        """
        return {
            "procedures": [
                {
                    "title": proc.get("title"),
                    "description": proc.get("description"),
                    "category": proc.get("category"),
                    "tags": json.loads(proc.get("tags", "[]")) if isinstance(proc.get("tags"), str) else proc.get("tags", []),
                    "steps": json.loads(proc.get("steps", "[]")) if isinstance(proc.get("steps"), str) else proc.get("steps", []),
                    "qualityScore": proc.get("quality_score", 0.0)
                }
                for proc in procedures
            ],
            "tips": [
                {
                    "title": tip.get("title"),
                    "content": tip.get("content"),
                    "category": tip.get("category"),
                    "tags": json.loads(tip.get("tags", "[]")) if isinstance(tip.get("tags"), str) else tip.get("tags", []),
                    "sourceSection": tip.get("source_section", "")
                }
                for tip in tips
            ]
        }


def export_validated_data() -> Dict[str, Any]:
    """Fonction utilitaire pour exporter les données validées"""
    migrator = MigrationToProduction()
    return migrator.export_validated_data()


def main():
    """Fonction principale pour tests"""
    print("📤 Migration vers Supabase")
    print("=" * 60)
    
    plan = export_validated_data()
    
    print("📋 Instructions pour utiliser sqlite MCP:\n")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Plan d'export généré")
    print(f"   L'agent utilisera sqlite MCP pour lire les données validées")


if __name__ == "__main__":
    main()
