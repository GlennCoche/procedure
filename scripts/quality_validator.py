#!/usr/bin/env python3
"""
Validateur de qualité utilisant sqlite MCP pour vérifier cohérence, détecter doublons et calculer scores
"""

import json
from typing import Dict, List, Any, Optional


class QualityValidator:
    """
    Validateur de qualité utilisant sqlite MCP
    """
    
    def __init__(self):
        """Initialiser le validateur"""
        pass
    
    def validate_procedure(self, procedure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valider une procédure
        
        Args:
            procedure_data: Données de la procédure
        
        Returns:
            Score de qualité et notes de validation
        """
        score = 0.0
        notes = []
        
        # Critères de validation
        if procedure_data.get("title") and len(procedure_data["title"]) > 10:
            score += 0.2
        else:
            notes.append("Titre trop court ou manquant")
        
        if procedure_data.get("description") and len(procedure_data["description"]) > 50:
            score += 0.2
        else:
            notes.append("Description trop courte")
        
        steps = procedure_data.get("steps", [])
        if isinstance(steps, str):
            try:
                steps = json.loads(steps)
            except:
                steps = []
        
        if len(steps) >= 2:
            score += 0.3
        else:
            notes.append("Moins de 2 steps")
        
        # Vérifier que chaque step a un titre et des instructions
        valid_steps = 0
        for step in steps:
            if step.get("title") and step.get("instructions"):
                valid_steps += 1
        
        if valid_steps == len(steps) and len(steps) > 0:
            score += 0.2
        else:
            notes.append(f"{len(steps) - valid_steps} steps incomplets")
        
        if procedure_data.get("category"):
            score += 0.1
        else:
            notes.append("Catégorie manquante")
        
        return {
            "quality_score": min(score, 1.0),
            "validation_notes": notes,
            "passed": score >= 0.7
        }
    
    def validate_tip(self, tip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valider un tip
        
        Args:
            tip_data: Données du tip
        
        Returns:
            Score de qualité et notes
        """
        score = 0.0
        notes = []
        
        if tip_data.get("title") and len(tip_data["title"]) > 5:
            score += 0.3
        else:
            notes.append("Titre trop court")
        
        if tip_data.get("content") and len(tip_data["content"]) > 20:
            score += 0.5
        else:
            notes.append("Contenu trop court")
        
        if tip_data.get("category"):
            score += 0.2
        else:
            notes.append("Catégorie manquante")
        
        return {
            "quality_score": min(score, 1.0),
            "validation_notes": notes,
            "passed": score >= 0.7
        }
    
    def detect_duplicates(self, table: str, field: str, value: str) -> Dict[str, Any]:
        """
        Instructions pour détecter les doublons via sqlite MCP
        
        L'agent Cursor doit utiliser: sqlite.execute_sql
        
        Args:
            table: Table à vérifier
            field: Champ à vérifier
            value: Valeur à rechercher
        
        Returns:
            Instructions pour utiliser sqlite MCP
        """
        return {
            "mcp_instructions": {
                "sqlite": {
                    "detect_duplicates": {
                        "tool": "sqlite.execute_sql",
                        "sql": f"""
                            SELECT id, {field}, COUNT(*) as count
                            FROM {table}
                            WHERE {field} = ?
                            GROUP BY {field}
                            HAVING COUNT(*) > 1
                        """,
                        "params": [value],
                        "description": "Détecter les doublons dans la table"
                    }
                }
            }
        }
    
    def validate_all(self, document_id: int) -> Dict[str, Any]:
        """
        Valider toutes les procédures et tips d'un document
        
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
                        "description": "Lire toutes les procédures du document"
                    },
                    "read_tips": {
                        "tool": "sqlite.read_records",
                        "table": "local_tips",
                        "conditions": {"document_id": document_id},
                        "description": "Lire tous les tips du document"
                    },
                    "check_duplicates": {
                        "tool": "sqlite.execute_sql",
                        "sql": """
                            SELECT title, COUNT(*) as count
                            FROM local_procedures
                            WHERE document_id = ?
                            GROUP BY title
                            HAVING COUNT(*) > 1
                        """,
                        "description": "Détecter les procédures en double"
                    },
                    "update_scores": {
                        "tool": "sqlite.update_records",
                        "table": "local_procedures",
                        "description": "Mettre à jour les scores de qualité"
                    }
                }
            },
            "workflow": [
                "1. Lire toutes les procédures via sqlite.read_records",
                "2. Lire tous les tips via sqlite.read_records",
                "3. Valider chaque procédure (calculer quality_score)",
                "4. Valider chaque tip (calculer quality_score)",
                "5. Détecter les doublons via sqlite.execute_sql",
                "6. Mettre à jour les scores via sqlite.update_records",
                "7. Mettre à jour document_processing.status='validated'"
            ]
        }


def validate_procedure(procedure_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction utilitaire pour valider une procédure"""
    validator = QualityValidator()
    return validator.validate_procedure(procedure_data)


def main():
    """Fonction principale pour tests"""
    example_procedure = {
        "title": "Installation onduleur photovoltaïque",
        "description": "Procédure complète pour installer un onduleur photovoltaïque sur site",
        "steps": [
            {"step_number": 1, "title": "Préparer le site", "instructions": "Vérifier..."},
            {"step_number": 2, "title": "Installer", "instructions": "Fixer..."}
        ],
        "category": "installation"
    }
    
    print("✅ Validation de qualité")
    result = validate_procedure(example_procedure)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
