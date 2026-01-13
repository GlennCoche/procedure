#!/usr/bin/env python3
"""
Structurateur intelligent utilisant content-core MCP pour transformer l'analyse IA en procédures/steps/tips
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from scripts.prompts.expert_prompts import get_structuring_prompt


class IntelligentStructurer:
    """
    Structurateur intelligent utilisant content-core MCP
    Transforme l'analyse IA en structures applicatives (procédures, steps, tips)
    """
    
    def __init__(self):
        """Initialiser le structurateur"""
        pass
    
    def structure_analysis(self, analysis_data: Dict[str, Any], document_id: int) -> Dict[str, Any]:
        """
        Structurer l'analyse IA en procédures et tips
        
        L'agent Cursor doit utiliser: content-core.extract_content avec le prompt de structuration
        
        Args:
            analysis_data: Données d'analyse IA (de create_ai_analyzer)
            document_id: ID du document dans document_processing
        
        Returns:
            Instructions pour utiliser content-core MCP + sqlite MCP
        """
        structuring_prompt = get_structuring_prompt(analysis_data)
        
        return {
            "mcp_instructions": {
                "content_core": {
                    "tool": "content-core.extract_content",
                    "description": "Structuration intelligente du contenu analysé",
                    "note": "Utiliser le prompt de structuration pour guider l'extraction"
                },
                "sqlite": {
                    "create_procedures": {
                        "tool": "sqlite.create_record",
                        "table": "local_procedures",
                        "description": "Créer les procédures structurées"
                    },
                    "create_tips": {
                        "tool": "sqlite.create_record",
                        "table": "local_tips",
                        "description": "Créer les tips structurés"
                    },
                    "update_status": {
                        "tool": "sqlite.update_records",
                        "table": "document_processing",
                        "description": "Mettre à jour le statut à 'structured'"
                    }
                }
            },
            "structuring_prompt": structuring_prompt,
            "workflow": [
                {
                    "step": 1,
                    "action": "Utiliser content-core.extract_content avec le prompt de structuration",
                    "description": "Content-core structure l'analyse en procédures et tips",
                    "input": "analysis_data (JSON)",
                    "output": "structured_data (JSON avec procedures et tips)"
                },
                {
                    "step": 2,
                    "action": "Parser le résultat JSON de content-core",
                    "description": "Extraire les arrays procedures et tips"
                },
                {
                    "step": 3,
                    "action": "Pour chaque procédure, utiliser sqlite.create_record",
                    "description": "Créer l'enregistrement dans local_procedures",
                    "data_structure": {
                        "document_id": "document_id",
                        "title": "string",
                        "description": "string",
                        "category": "string",
                        "tags": "JSON array (string)",
                        "steps": "JSON array",
                        "quality_score": 0.0
                    }
                },
                {
                    "step": 4,
                    "action": "Pour chaque tip, utiliser sqlite.create_record",
                    "description": "Créer l'enregistrement dans local_tips",
                    "data_structure": {
                        "document_id": "document_id",
                        "title": "string",
                        "content": "string",
                        "category": "string",
                        "tags": "JSON array (string)",
                        "source_section": "string",
                        "quality_score": 0.0
                    }
                },
                {
                    "step": 5,
                    "action": "Mettre à jour document_processing",
                    "description": "Mettre à jour structured_data et status='structured'",
                    "tool": "sqlite.update_records"
                }
            ],
            "expected_output": {
                "procedures_created": "number",
                "tips_created": "number",
                "structured_data": "JSON string"
            }
        }
    
    def extract_procedures(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraire les procédures depuis l'analyse
        
        Args:
            analysis_data: Données d'analyse
        
        Returns:
            Liste de procédures structurées
        """
        procedures = analysis_data.get("procedures_detected", [])
        
        structured_procedures = []
        for proc in procedures:
            structured_procedures.append({
                "title": proc.get("title", ""),
                "description": proc.get("description", ""),
                "category": proc.get("category", "maintenance"),
                "tags": json.dumps(proc.get("tags", [])),
                "steps": json.dumps(proc.get("steps", []))
            })
        
        return structured_procedures
    
    def extract_tips(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extraire les tips depuis l'analyse
        
        Args:
            analysis_data: Données d'analyse
        
        Returns:
            Liste de tips structurés
        """
        tips = analysis_data.get("tips_detected", [])
        
        structured_tips = []
        for tip in tips:
            structured_tips.append({
                "title": tip.get("title", ""),
                "content": tip.get("content", ""),
                "category": tip.get("category", "general"),
                "tags": json.dumps(tip.get("tags", [])),
                "source_section": tip.get("source_section", "")
            })
        
        return structured_tips


def structure_analysis_data(analysis_data: Dict[str, Any], document_id: int) -> Dict[str, Any]:
    """
    Fonction utilitaire pour structurer l'analyse
    
    Args:
        analysis_data: Données d'analyse IA
        document_id: ID du document
    
    Returns:
        Instructions pour utiliser les MCPs
    """
    structurer = IntelligentStructurer()
    return structurer.structure_analysis(analysis_data, document_id)


def main():
    """Fonction principale pour tests"""
    import sys
    
    # Exemple d'analyse_data
    example_analysis = {
        "document_type": "manuel_maintenance",
        "equipment_brand": "ABB",
        "procedures_detected": [
            {
                "title": "Installation onduleur",
                "description": "Procédure d'installation",
                "steps": [
                    {"step_number": 1, "title": "Préparer le site", "instructions": "..."}
                ]
            }
        ],
        "tips_detected": [
            {
                "title": "Vérifier la tension",
                "content": "Toujours vérifier la tension avant connexion",
                "source_section": "Sécurité"
            }
        ]
    }
    
    print("🔧 Structuration intelligente de l'analyse")
    print(f"\n📋 Instructions pour utiliser content-core MCP + sqlite MCP:\n")
    
    result = structure_analysis_data(example_analysis, document_id=1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Instructions générées")
    print(f"   L'agent utilisera content-core pour structurer")
    print(f"   Puis sqlite pour stocker les procédures et tips")


if __name__ == "__main__":
    main()
