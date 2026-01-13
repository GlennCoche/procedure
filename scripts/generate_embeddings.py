#!/usr/bin/env python3
"""
Génération d'embeddings utilisant faiss MCP
Crée les embeddings vectoriels pour la recherche sémantique
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from scripts.local_db.db_manager import LocalDBManager


class EmbeddingGenerator:
    """
    Générateur d'embeddings utilisant faiss MCP
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Args:
            db_path: Chemin vers la base SQLite locale
        """
        self.db = LocalDBManager(db_path)
    
    def generate_embeddings_for_procedures(self, procedures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Générer des embeddings pour les procédures
        
        L'agent Cursor doit utiliser: faiss MCP
        
        Args:
            procedures: Liste de procédures
        
        Returns:
            Instructions pour utiliser faiss MCP
        """
        return {
            "mcp_instructions": {
                "faiss": {
                    "ingest_documents": {
                        "tool": "faiss.ingest_document",
                        "description": "Ingérer chaque procédure dans le store vectoriel",
                        "for_each_procedure": {
                            "document": "title + description + steps (texte combiné)",
                            "source": "procedure_{id}"
                        }
                    },
                    "query_store": {
                        "tool": "faiss.query_rag_store",
                        "description": "Tester la recherche sémantique",
                        "example_query": "Comment installer un onduleur photovoltaïque?"
                    }
                },
                "sqlite": {
                    "read_procedures": {
                        "tool": "sqlite.read_records",
                        "table": "local_procedures",
                        "conditions": {"needs_review": 0},
                        "description": "Lire toutes les procédures validées"
                    }
                }
            },
            "workflow": [
                "1. Lire toutes les procédures validées via sqlite.read_records",
                "2. Pour chaque procédure, combiner title + description + steps en texte",
                "3. Utiliser faiss.ingest_document pour chaque procédure",
                "4. Répéter pour les tips",
                "5. Tester la recherche avec faiss.query_rag_store"
            ],
            "embedding_text_format": {
                "procedure": "{title}\n\n{description}\n\nSteps:\n{steps_text}",
                "tip": "{title}\n\n{content}"
            }
        }
    
    def generate_embeddings_for_tips(self, tips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Générer des embeddings pour les tips
        
        Args:
            tips: Liste de tips
        
        Returns:
            Instructions pour utiliser faiss MCP
        """
        return {
            "mcp_instructions": {
                "faiss": {
                    "ingest_documents": {
                        "tool": "faiss.ingest_document",
                        "description": "Ingérer chaque tip dans le store vectoriel",
                        "for_each_tip": {
                            "document": "title + content",
                            "source": "tip_{id}"
                        }
                    }
                }
            }
        }
    
    def generate_all_embeddings(self) -> Dict[str, Any]:
        """
        Générer les embeddings pour toutes les données validées
        
        Returns:
            Instructions complètes pour utiliser faiss MCP
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "read_all_validated": {
                        "tool": "sqlite.read_records",
                        "description": "Lire procédures et tips validés"
                    }
                },
                "faiss": {
                    "ingest_all": {
                        "tool": "faiss.ingest_document",
                        "description": "Ingérer toutes les données dans le store vectoriel"
                    },
                    "verify": {
                        "tool": "faiss.query_rag_store",
                        "description": "Vérifier que les embeddings fonctionnent"
                    }
                }
            },
            "workflow": [
                "1. Lire procédures validées via sqlite.read_records",
                "2. Lire tips validés via sqlite.read_records",
                "3. Pour chaque procédure: faiss.ingest_document",
                "4. Pour chaque tip: faiss.ingest_document",
                "5. Tester la recherche sémantique avec faiss.query_rag_store"
            ],
            "expected_result": "Store vectoriel FAISS avec tous les embeddings créés"
        }


def generate_embeddings() -> Dict[str, Any]:
    """Fonction utilitaire pour générer les embeddings"""
    generator = EmbeddingGenerator()
    return generator.generate_all_embeddings()


def main():
    """Fonction principale pour tests"""
    print("🔢 Génération d'embeddings avec faiss MCP")
    print("=" * 60)
    
    plan = generate_embeddings()
    
    print("📋 Instructions pour utiliser faiss MCP:\n")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Plan de génération d'embeddings généré")
    print(f"   L'agent utilisera faiss MCP pour créer les embeddings vectoriels")


if __name__ == "__main__":
    main()
