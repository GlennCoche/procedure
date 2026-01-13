#!/usr/bin/env python3
"""
Script pour traiter tous les documents par marque avec le pipeline intelligent
Utilise tous les MCPs pour chaque document
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from scripts.intelligent_import import IntelligentImportOrchestrator
from scripts.local_db.db_manager import LocalDBManager


def get_documents_by_brand(docs_dir: Path) -> Dict[str, List[Path]]:
    """
    Organiser les documents par marque
    
    Args:
        docs_dir: Répertoire contenant les documents
    
    Returns:
        Dictionnaire {brand: [list of pdfs]}
    """
    documents_by_brand = {}
    
    if not docs_dir.exists():
        return documents_by_brand
    
    # Parcourir les sous-répertoires (marques)
    for brand_dir in docs_dir.iterdir():
        if brand_dir.is_dir():
            brand = brand_dir.name
            pdfs = list(brand_dir.glob("*.pdf"))
            if pdfs:
                documents_by_brand[brand] = pdfs
    
    return documents_by_brand


def process_all_documents(docs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Traiter tous les documents par marque
    
    L'agent Cursor doit utiliser le pipeline intelligent pour chaque document
    
    Args:
        docs_dir: Répertoire contenant les documents (par défaut: docs/)
    
    Returns:
        Plan de traitement avec instructions MCP
    """
    if docs_dir is None:
        docs_dir = Path(__file__).parent.parent / "docs"
    
    documents_by_brand = get_documents_by_brand(docs_dir)
    
    total_documents = sum(len(pdfs) for pdfs in documents_by_brand.values())
    
    return {
        "total_documents": total_documents,
        "documents_by_brand": {
            brand: len(pdfs) for brand, pdfs in documents_by_brand.items()
        },
        "processing_plan": {
            "order": list(documents_by_brand.keys()),
            "workflow_per_document": "Utiliser intelligent_import.process_document()",
            "mcp_tools_used": [
                "pdf-tools (extraction)",
                "content-core (analyse, structuration, enrichissement)",
                "sqlite (stockage, validation)",
                "openai_vision (analyse images)",
                "faiss (embeddings, étape import)"
            ]
        },
        "instructions": {
            "for_each_brand": [
                "1. Traiter tous les PDFs de la marque",
                "2. Utiliser le pipeline intelligent pour chaque document",
                "3. Vérifier le statut dans document_processing",
                "4. Passer à la marque suivante"
            ],
            "for_each_document": [
                "1. Extraction (pdf-tools + content-core)",
                "2. Analyse IA (content-core)",
                "3. Analyse Vision (pdf-tools + OpenAI Vision)",
                "4. Structuration (content-core + sqlite)",
                "5. Enrichissement (content-core + sqlite)",
                "6. Validation (sqlite)"
            ]
        },
        "expected_results": {
            "per_document": {
                "status": "validated",
                "procedures_created": ">= 1",
                "tips_created": ">= 1",
                "quality_score": ">= 0.7"
            },
            "total": {
                "documents_processed": total_documents,
                "success_rate": "> 95%"
            }
        }
    }


def main():
    """Fonction principale"""
    print("📚 Traitement de tous les documents")
    print("=" * 60)
    
    plan = process_all_documents()
    
    print(f"📊 Total de documents: {plan['total_documents']}")
    print(f"\n📦 Documents par marque:")
    for brand, count in plan["documents_by_brand"].items():
        print(f"   - {brand}: {count} documents")
    
    print(f"\n📋 Plan de traitement:")
    print(json.dumps(plan["processing_plan"], indent=2, ensure_ascii=False))
    
    print(f"\n✅ Plan généré")
    print(f"   L'agent Cursor traitera chaque document avec le pipeline intelligent")


if __name__ == "__main__":
    main()
