#!/usr/bin/env python3
"""
Script principal d'orchestration utilisant tous les MCPs
Gère le workflow complet document par document
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Imports des modules
from scripts.local_db.db_manager import LocalDBManager
from scripts.extract_pdf_enhanced import extract_pdf_enhanced
from scripts.ai_analyzer import analyze_document_with_ai
from scripts.vision_analyzer import analyze_images_from_pdf
from scripts.intelligent_structurer import structure_analysis_data
from scripts.ai_enricher import enrich_procedure
from scripts.validator import validate_document
from scripts.mcp_helpers import MCPHelper


class IntelligentImportOrchestrator:
    """
    Orchestrateur principal utilisant tous les MCPs
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Args:
            db_path: Chemin vers la base SQLite locale
        """
        self.db = LocalDBManager(db_path)
        self.mcp_helper = MCPHelper()
    
    def process_document(self, pdf_path: Path, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Traiter un document complet en utilisant tous les MCPs
        
        Cette fonction documente le workflow. L'agent Cursor utilisera
        directement les outils MCP à chaque étape.
        
        Args:
            pdf_path: Chemin vers le PDF
            brand: Marque de l'équipement
        
        Returns:
            Résultat du traitement avec instructions MCP
        """
        result = {
            "file_path": str(pdf_path),
            "file_name": pdf_path.name,
            "brand": brand,
            "workflow": []
        }
        
        # Étape 1: Extraction (MCP: pdf-tools + content-core)
        result["workflow"].append({
            "step": 1,
            "name": "Extraction",
            "mcp_tools": {
                "pdf_tools": [
                    "get_metadata",
                    "get_text_json",
                    "get_text_blocks",
                    "display_page_as_image (pour chaque page)"
                ],
                "content_core": [
                    "extract_content (optionnel, si extraction pdf-tools insuffisante)"
                ]
            },
            "store_in": "document_processing (status='extracted')",
            "mcp_instruction": "Utiliser sqlite.create_record pour stocker"
        })
        
        # Étape 2: Analyse IA (MCP: content-core)
        result["workflow"].append({
            "step": 2,
            "name": "Analyse IA",
            "mcp_tools": {
                "content_core": [
                    "extract_content avec prompt expert photovoltaïque"
                ]
            },
            "store_in": "document_processing.analysis_data (status='analyzed')",
            "mcp_instruction": "Utiliser sqlite.update_records pour mettre à jour"
        })
        
        # Étape 3: Analyse Vision (MCP: pdf-tools + OpenAI Vision)
        result["workflow"].append({
            "step": 3,
            "name": "Analyse Vision",
            "mcp_tools": {
                "pdf_tools": [
                    "display_page_as_image (pour chaque page avec schémas/graphiques)"
                ],
                "openai_vision": "Appel direct à OpenAI Vision API (GPT-4o) dans le code Python"
            },
            "store_in": "document_images",
            "mcp_instruction": "Utiliser sqlite.create_record pour chaque image analysée"
        })
        
        # Étape 4: Structuration (MCP: content-core + sqlite)
        result["workflow"].append({
            "step": 4,
            "name": "Structuration",
            "mcp_tools": {
                "content_core": [
                    "extract_content avec prompt de structuration"
                ],
                "sqlite": [
                    "create_record dans local_procedures",
                    "create_record dans local_tips",
                    "update_records dans document_processing (status='structured')"
                ]
            }
        })
        
        # Étape 5: Enrichissement (MCP: content-core + sqlite)
        result["workflow"].append({
            "step": 5,
            "name": "Enrichissement",
            "mcp_tools": {
                "content_core": [
                    "extract_content avec prompt d'enrichissement (pour chaque procédure/tip)"
                ],
                "sqlite": [
                    "update_records dans local_procedures",
                    "update_records dans local_tips",
                    "update_records dans document_processing (status='enriched')"
                ]
            }
        })
        
        # Étape 6: Validation (MCP: sqlite)
        result["workflow"].append({
            "step": 6,
            "name": "Validation",
            "mcp_tools": {
                "sqlite": [
                    "read_records (lire procédures et tips)",
                    "execute_sql (vérifier complétude, détecter doublons)",
                    "update_records (mettre à jour quality_score)",
                    "update_records dans document_processing (status='validated')"
                ]
            }
        })
        
        return result
    
    def process_all_documents(self, docs_dir: Path, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Traiter tous les documents d'un répertoire
        
        Args:
            docs_dir: Répertoire contenant les documents
            brand: Marque de l'équipement
        
        Returns:
            Résultat du traitement
        """
        pdf_files = list(docs_dir.glob("*.pdf"))
        
        return {
            "total_documents": len(pdf_files),
            "workflow_per_document": self.process_document(pdf_files[0] if pdf_files else Path("example.pdf"), brand),
            "note": "Répéter le workflow pour chaque document"
        }
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé du workflow avec MCPs"""
        return {
            "workflow_steps": [
                {
                    "step": 1,
                    "name": "Extraction",
                    "mcps": ["pdf-tools", "content-core"],
                    "output": "extraction_data dans document_processing"
                },
                {
                    "step": 2,
                    "name": "Analyse IA",
                    "mcps": ["content-core"],
                    "output": "analysis_data dans document_processing"
                },
                {
                    "step": 3,
                    "name": "Analyse Vision",
                    "mcps": ["pdf-tools", "openai_vision"],
                    "output": "document_images"
                },
                {
                    "step": 4,
                    "name": "Structuration",
                    "mcps": ["content-core", "sqlite"],
                    "output": "local_procedures, local_tips"
                },
                {
                    "step": 5,
                    "name": "Enrichissement",
                    "mcps": ["content-core", "sqlite"],
                    "output": "Données enrichies dans local_procedures, local_tips"
                },
                {
                    "step": 6,
                    "name": "Validation",
                    "mcps": ["sqlite"],
                    "output": "Scores de qualité, status='validated'"
                }
            ],
            "mcp_usage": {
                "pdf-tools": "Extraction PDF (texte, images, métadonnées)",
                "sqlite": "Gestion base de données (CRUD, requêtes)",
                "content-core": "Analyse IA, structuration, enrichissement",
                "faiss": "Génération embeddings (étape import)"
            }
        }


def process_single_document(pdf_path: Path, brand: Optional[str] = None) -> Dict[str, Any]:
    """Fonction utilitaire pour traiter un document"""
    orchestrator = IntelligentImportOrchestrator()
    return orchestrator.process_document(pdf_path, brand)


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: intelligent_import.py <pdf_path> [brand]")
        print("\nExemple:")
        print("  python intelligent_import.py docs/ABB/manual.pdf ABB")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    brand = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not pdf_path.exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        sys.exit(1)
    
    print(f"🚀 Orchestration du traitement: {pdf_path.name}")
    print(f"\n📋 Workflow avec MCPs:\n")
    
    orchestrator = IntelligentImportOrchestrator()
    result = orchestrator.process_document(pdf_path, brand)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Workflow défini")
    print(f"   L'agent Cursor utilisera les MCPs à chaque étape")


if __name__ == "__main__":
    main()
