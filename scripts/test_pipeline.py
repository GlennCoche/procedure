#!/usr/bin/env python3
"""
Script de test du pipeline complet sur un document ABB
Utilise tous les MCPs pour valider le workflow
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from scripts.intelligent_import import IntelligentImportOrchestrator
from scripts.local_db.db_manager import LocalDBManager


def test_pipeline_on_abb_document() -> Dict[str, Any]:
    """
    Tester le pipeline complet sur un document ABB
    
    L'agent Cursor doit utiliser tous les MCPs selon le workflow défini
    
    Returns:
        Instructions pour tester avec tous les MCPs
    """
    # Trouver un document ABB de test
    docs_dir = Path(__file__).parent.parent / "docs" / "ABB"
    
    abb_pdfs = list(docs_dir.glob("*.pdf")) if docs_dir.exists() else []
    
    if not abb_pdfs:
        return {
            "error": "Aucun document ABB trouvé",
            "expected_path": str(docs_dir),
            "note": "Créer un document de test ou utiliser un document existant"
        }
    
    test_document = abb_pdfs[0]
    
    return {
        "test_document": str(test_document),
        "workflow_to_test": {
            "step_1_extraction": {
                "mcp_tools": ["pdf-tools.get_metadata", "pdf-tools.get_text_json", "pdf-tools.display_page_as_image"],
                "expected_result": "extraction_data dans document_processing"
            },
            "step_2_analysis": {
                "mcp_tools": ["content-core.extract_content"],
                "expected_result": "analysis_data dans document_processing"
            },
            "step_3_vision": {
                "mcp_tools": ["pdf-tools.display_page_as_image", "openai_vision_api"],
                "expected_result": "document_images avec descriptions"
            },
            "step_4_structuring": {
                "mcp_tools": ["content-core.extract_content", "sqlite.create_record"],
                "expected_result": "local_procedures et local_tips créés"
            },
            "step_5_enrichment": {
                "mcp_tools": ["content-core.extract_content", "sqlite.update_records"],
                "expected_result": "Données enrichies"
            },
            "step_6_validation": {
                "mcp_tools": ["sqlite.read_records", "sqlite.execute_sql", "sqlite.update_records"],
                "expected_result": "Scores de qualité, status='validated'"
            }
        },
        "validation_checks": [
            "Vérifier que document_processing.status = 'validated'",
            "Vérifier que local_procedures contient au moins une procédure",
            "Vérifier que local_tips contient au moins un tip",
            "Vérifier que quality_score > 0.7 pour chaque procédure",
            "Vérifier que document_images contient des images analysées"
        ],
        "mcp_verification": {
            "pdf-tools": "Vérifier que get_metadata, get_text_json fonctionnent",
            "sqlite": "Vérifier que create_record, read_records, update_records fonctionnent",
            "content-core": "Vérifier que extract_content fonctionne",
            "faiss": "Vérifier que les embeddings peuvent être créés (étape import)"
        }
    }


def run_test() -> bool:
    """
    Exécuter le test du pipeline
    
    Returns:
        True si le test réussit
    """
    print("🧪 Test du pipeline complet")
    print("=" * 60)
    
    test_plan = test_pipeline_on_abb_document()
    
    if "error" in test_plan:
        print(f"⚠️  {test_plan['error']}")
        return False
    
    print(f"📄 Document de test: {test_plan['test_document']}")
    print(f"\n📋 Workflow à tester:\n")
    
    for step_name, step_info in test_plan["workflow_to_test"].items():
        print(f"{step_name}:")
        print(f"  MCPs: {', '.join(step_info['mcp_tools'])}")
        print(f"  Résultat attendu: {step_info['expected_result']}")
        print()
    
    print("✅ Plan de test généré")
    print("\n⚠️  Note: L'agent Cursor exécutera le workflow en utilisant les MCPs")
    
    return True


if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
