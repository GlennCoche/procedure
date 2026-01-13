#!/usr/bin/env python3
"""
Enrichisseur IA utilisant content-core MCP pour améliorer et compléter les données générées
"""

import json
from typing import Dict, List, Any, Optional
from scripts.prompts.expert_prompts import get_enrichment_prompt


class AIEnricher:
    """
    Enrichisseur IA utilisant content-core MCP
    """
    
    def __init__(self):
        """Initialiser l'enrichisseur"""
        pass
    
    def enrich_procedure(self, procedure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichir une procédure en utilisant content-core MCP
        
        L'agent Cursor doit utiliser: content-core.extract_content
        
        Args:
            procedure_data: Données de la procédure à enrichir
        
        Returns:
            Instructions pour utiliser content-core MCP + sqlite MCP
        """
        enrichment_prompt = get_enrichment_prompt(procedure_data)
        
        return {
            "mcp_instructions": {
                "content_core": {
                    "tool": "content-core.extract_content",
                    "description": "Enrichissement IA de la procédure",
                    "input": "procedure_data (JSON)",
                    "prompt": enrichment_prompt
                },
                "sqlite": {
                    "update_procedure": {
                        "tool": "sqlite.update_records",
                        "table": "local_procedures",
                        "description": "Mettre à jour la procédure enrichie"
                    }
                }
            },
            "enrichment_prompt": enrichment_prompt,
            "workflow": [
                {
                    "step": 1,
                    "action": "Utiliser content-core.extract_content avec le prompt d'enrichissement",
                    "description": "Content-core enrichit la procédure avec OpenAI",
                    "input": "procedure_data (JSON)",
                    "output": "enriched_procedure_data (JSON)"
                },
                {
                    "step": 2,
                    "action": "Parser le résultat JSON enrichi",
                    "description": "Extraire les améliorations"
                },
                {
                    "step": 3,
                    "action": "Mettre à jour via sqlite.update_records",
                    "description": "Mettre à jour la procédure dans local_procedures",
                    "conditions": {"id": "procedure_id"},
                    "data": "enriched_procedure_data"
                }
            ],
            "enrichments_applied": [
                "Amélioration des descriptions",
                "Optimisation des instructions",
                "Ajout de conseils pratiques",
                "Identification de points d'attention",
                "Optimisation des tags et catégories",
                "Vérification de cohérence technique"
            ]
        }
    
    def enrich_tip(self, tip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichir un tip en utilisant content-core MCP
        
        Args:
            tip_data: Données du tip à enrichir
        
        Returns:
            Instructions pour utiliser content-core MCP
        """
        enrichment_prompt = get_enrichment_prompt(tip_data)
        
        return {
            "mcp_instructions": {
                "content_core": {
                    "tool": "content-core.extract_content",
                    "description": "Enrichissement IA du tip",
                    "prompt": enrichment_prompt
                },
                "sqlite": {
                    "update_tip": {
                        "tool": "sqlite.update_records",
                        "table": "local_tips",
                        "description": "Mettre à jour le tip enrichi"
                    }
                }
            }
        }
    
    def enrich_batch(self, procedures: List[Dict[str, Any]], 
                    tips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrichir un lot de procédures et tips
        
        Args:
            procedures: Liste de procédures
            tips: Liste de tips
        
        Returns:
            Instructions pour enrichir le lot
        """
        return {
            "mcp_instructions": {
                "content_core": {
                    "tool": "content-core.extract_content",
                    "description": "Enrichissement en lot",
                    "batch_mode": True
                },
                "sqlite": {
                    "update_batch": {
                        "tool": "sqlite.update_records",
                        "description": "Mise à jour en lot"
                    }
                }
            },
            "workflow": [
                "1. Pour chaque procédure, utiliser content-core.extract_content",
                "2. Pour chaque tip, utiliser content-core.extract_content",
                "3. Mettre à jour toutes les données enrichies via sqlite.update_records"
            ],
            "total_items": len(procedures) + len(tips)
        }


def enrich_procedure(procedure_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction utilitaire pour enrichir une procédure"""
    enricher = AIEnricher()
    return enricher.enrich_procedure(procedure_data)


def main():
    """Fonction principale pour tests"""
    example_procedure = {
        "id": 1,
        "title": "Installation onduleur",
        "description": "Installer l'onduleur",
        "steps": [
            {"step_number": 1, "title": "Préparer", "instructions": "Vérifier le site"}
        ]
    }
    
    print("✨ Enrichissement IA de la procédure")
    print(f"\n📋 Instructions pour utiliser content-core MCP:\n")
    
    result = enrich_procedure(example_procedure)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Instructions générées")
    print(f"   L'agent utilisera content-core pour enrichir")
    print(f"   Puis sqlite pour mettre à jour")


if __name__ == "__main__":
    main()
