#!/usr/bin/env python3
"""
Validateur complet utilisant sqlite MCP pour vérifier cohérence, détecter doublons et calculer scores
"""

import json
from typing import Dict, List, Any
from scripts.quality_validator import QualityValidator


class Validator:
    """
    Validateur complet utilisant sqlite MCP
    """
    
    def __init__(self):
        """Initialiser le validateur"""
        self.quality_validator = QualityValidator()
    
    def validate_document(self, document_id: int) -> Dict[str, Any]:
        """
        Valider toutes les données d'un document
        
        L'agent Cursor doit utiliser: sqlite.read_records, execute_sql, update_records
        
        Args:
            document_id: ID du document
        
        Returns:
            Instructions pour utiliser sqlite MCP
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "read_procedures": {
                        "tool": "sqlite.read_records",
                        "table": "local_procedures",
                        "conditions": {"document_id": document_id},
                        "description": "Lire toutes les procédures"
                    },
                    "read_tips": {
                        "tool": "sqlite.read_records",
                        "table": "local_tips",
                        "conditions": {"document_id": document_id},
                        "description": "Lire tous les tips"
                    },
                    "check_completeness": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT 
                                COUNT(DISTINCT p.id) as procedures_count,
                                COUNT(DISTINCT t.id) as tips_count,
                                AVG(p.quality_score) as avg_procedure_score,
                                AVG(t.quality_score) as avg_tip_score
                            FROM document_processing dp
                            LEFT JOIN local_procedures p ON p.document_id = dp.id
                            LEFT JOIN local_tips t ON t.document_id = dp.id
                            WHERE dp.id = ?
                        """,
                        "description": "Vérifier la complétude"
                    },
                    "detect_duplicates": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT title, COUNT(*) as count
                            FROM local_procedures
                            WHERE document_id = ?
                            GROUP BY title
                            HAVING COUNT(*) > 1
                            UNION ALL
                            SELECT title, COUNT(*) as count
                            FROM local_tips
                            WHERE document_id = ?
                            GROUP BY title
                            HAVING COUNT(*) > 1
                        """,
                        "description": "Détecter les doublons"
                    },
                    "update_scores": {
                        "tool": "sqlite.update_records",
                        "table": "local_procedures",
                        "description": "Mettre à jour les scores de qualité"
                    },
                    "update_status": {
                        "tool": "sqlite.update_records",
                        "table": "document_processing",
                        "conditions": {"id": document_id},
                        "data": {"status": "validated"},
                        "description": "Mettre à jour le statut à 'validated'"
                    }
                }
            },
            "validation_criteria": {
                "procedures": {
                    "min_steps": 2,
                    "min_title_length": 10,
                    "min_description_length": 50,
                    "min_quality_score": 0.7
                },
                "tips": {
                    "min_title_length": 5,
                    "min_content_length": 20,
                    "min_quality_score": 0.7
                }
            },
            "workflow": [
                "1. Lire procédures et tips via sqlite.read_records",
                "2. Valider chaque procédure (calculer quality_score)",
                "3. Valider chaque tip (calculer quality_score)",
                "4. Vérifier complétude via sqlite.execute_sql",
                "5. Détecter doublons via sqlite.execute_sql",
                "6. Mettre à jour scores via sqlite.update_records",
                "7. Si validation OK, mettre status='validated'"
            ]
        }
    
    def calculate_quality_scores(self, procedures: List[Dict[str, Any]], 
                                tips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculer les scores de qualité pour toutes les données
        
        Args:
            procedures: Liste de procédures
            tips: Liste de tips
        
        Returns:
            Scores calculés
        """
        procedure_scores = []
        tip_scores = []
        
        for proc in procedures:
            score = self.quality_validator.validate_procedure(proc)
            procedure_scores.append(score["quality_score"])
        
        for tip in tips:
            score = self.quality_validator.validate_tip(tip)
            tip_scores.append(score["quality_score"])
        
        return {
            "procedures": {
                "count": len(procedures),
                "scores": procedure_scores,
                "average": sum(procedure_scores) / len(procedure_scores) if procedure_scores else 0.0,
                "min": min(procedure_scores) if procedure_scores else 0.0,
                "max": max(procedure_scores) if procedure_scores else 0.0
            },
            "tips": {
                "count": len(tips),
                "scores": tip_scores,
                "average": sum(tip_scores) / len(tip_scores) if tip_scores else 0.0,
                "min": min(tip_scores) if tip_scores else 0.0,
                "max": max(tip_scores) if tip_scores else 0.0
            }
        }


def validate_document(document_id: int) -> Dict[str, Any]:
    """Fonction utilitaire pour valider un document"""
    validator = Validator()
    return validator.validate_document(document_id)


def main():
    """Fonction principale pour tests"""
    print("✅ Validation complète")
    result = validate_document(document_id=1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
