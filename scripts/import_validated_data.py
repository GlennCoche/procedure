#!/usr/bin/env python3
"""
Import des données validées dans Supabase
Utilise sqlite MCP pour lire les données et faiss MCP pour générer les embeddings
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from scripts.local_db.db_manager import LocalDBManager
from scripts.migrate_to_production import MigrationToProduction
from scripts.generate_embeddings import EmbeddingGenerator


class ImportValidatedData:
    """
    Gestionnaire d'import vers Supabase
    Utilise sqlite MCP + faiss MCP
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Args:
            db_path: Chemin vers la base SQLite locale
        """
        self.db = LocalDBManager(db_path)
        self.migrator = MigrationToProduction(db_path)
        self.embedding_gen = EmbeddingGenerator(db_path)
    
    def import_to_supabase(self) -> Dict[str, Any]:
        """
        Importer les données validées dans Supabase
        
        L'agent Cursor doit utiliser: sqlite.read_records + faiss MCP
        
        Returns:
            Instructions pour utiliser les MCPs
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "read_procedures": {
                        "tool": "sqlite.read_records",
                        "table": "local_procedures",
                        "conditions": {"needs_review": 0},
                        "description": "Lire toutes les procédures validées"
                    },
                    "read_tips": {
                        "tool": "sqlite.read_records",
                        "table": "local_tips",
                        "conditions": {"needs_review": 0},
                        "description": "Lire tous les tips validés"
                    },
                    "get_documents": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT id, file_name, brand
                            FROM document_processing
                            WHERE status = 'validated'
                        """,
                        "description": "Obtenir les documents validés"
                    }
                },
                "faiss": {
                    "generate_embeddings": {
                        "tool": "faiss.ingest_document",
                        "description": "Créer les embeddings pour chaque procédure/tip",
                        "for_each": {
                            "procedure": "Ingérer title + description + steps",
                            "tip": "Ingérer title + content"
                        }
                    },
                    "verify_embeddings": {
                        "tool": "faiss.query_rag_store",
                        "description": "Vérifier que les embeddings fonctionnent"
                    }
                }
            },
            "import_workflow": [
                "1. Lire procédures validées via sqlite.read_records",
                "2. Lire tips validés via sqlite.read_records",
                "3. Générer embeddings via faiss.ingest_document pour chaque procédure",
                "4. Générer embeddings via faiss.ingest_document pour chaque tip",
                "5. Préparer les données pour Supabase (format Prisma)",
                "6. Importer dans Supabase via API Prisma",
                "7. Associer les embeddings aux enregistrements Supabase"
            ],
            "supabase_import": {
                "method": "API Prisma (via backend)",
                "endpoints": [
                    "/api/procedures (POST)",
                    "/api/tips (POST)"
                ],
                "data_format": {
                    "procedure": {
                        "title": "string",
                        "description": "string",
                        "category": "string",
                        "tags": "array",
                        "steps": "array",
                        "embedding": "vector (depuis faiss)"
                    },
                    "tip": {
                        "title": "string",
                        "content": "string",
                        "category": "string",
                        "tags": "array",
                        "embedding": "vector (depuis faiss)"
                    }
                }
            },
            "post_import_verification": [
                "Vérifier que les procédures sont dans Supabase",
                "Vérifier que les tips sont dans Supabase",
                "Vérifier que les embeddings sont associés",
                "Tester la recherche sémantique"
            ]
        }
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """
        Obtenir les statistiques d'import
        
        Returns:
            Instructions pour utiliser sqlite MCP
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "get_stats": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT 
                                COUNT(DISTINCT dp.id) as documents,
                                COUNT(DISTINCT p.id) as procedures,
                                COUNT(DISTINCT t.id) as tips,
                                AVG(p.quality_score) as avg_proc_score,
                                AVG(t.quality_score) as avg_tip_score
                            FROM document_processing dp
                            LEFT JOIN local_procedures p ON p.document_id = dp.id AND p.needs_review = 0
                            LEFT JOIN local_tips t ON t.document_id = dp.id AND t.needs_review = 0
                            WHERE dp.status = 'validated'
                        """,
                        "description": "Obtenir les statistiques d'import"
                    }
                }
            }
        }


def import_validated_data() -> Dict[str, Any]:
    """Fonction utilitaire pour importer les données"""
    importer = ImportValidatedData()
    return importer.import_to_supabase()


def main():
    """Fonction principale pour tests"""
    print("📥 Import vers Supabase avec embeddings")
    print("=" * 60)
    
    plan = import_validated_data()
    
    print("📋 Instructions pour utiliser sqlite MCP + faiss MCP:\n")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Plan d'import généré")
    print(f"   L'agent utilisera sqlite pour lire et faiss pour les embeddings")


if __name__ == "__main__":
    main()
