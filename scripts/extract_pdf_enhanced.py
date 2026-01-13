#!/usr/bin/env python3
"""
Script d'extraction PDF améliorée utilisant les MCPs pdf-tools et content-core
Remplace l'extraction manuelle par l'utilisation des outils MCP
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64


class PDFExtractorEnhanced:
    """
    Extracteur PDF amélioré utilisant les MCPs
    Note: Ce script prépare les appels aux MCPs. L'agent Cursor utilisera
    directement les outils MCP (pdf-tools et content-core) pour l'extraction.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Args:
            output_dir: Répertoire pour stocker les images extraites
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "local_db" / "images"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_with_mcp_tools(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extraire le contenu d'un PDF en utilisant les MCPs
        
        Cette fonction documente comment utiliser les MCPs pour l'extraction.
        L'agent Cursor utilisera directement les outils MCP.
        
        Args:
            pdf_path: Chemin vers le PDF
        
        Returns:
            Dictionnaire avec instructions pour utiliser les MCPs
        """
        result = {
            "file_path": str(pdf_path),
            "file_name": pdf_path.name,
            "mcp_instructions": {
                "pdf_tools": {
                    "get_metadata": {
                        "description": "Extraire les métadonnées du PDF",
                        "tool": "pdf-tools.get_metadata",
                        "args": {"name": pdf_path.name}
                    },
                    "get_text_json": {
                        "description": "Extraire le texte structuré avec positions",
                        "tool": "pdf-tools.get_text_json",
                        "args": {"name": pdf_path.name}
                    },
                    "get_text_blocks": {
                        "description": "Extraire les blocs de texte",
                        "tool": "pdf-tools.get_text_blocks",
                        "args": {"name": pdf_path.name}
                    },
                    "display_page_as_image": {
                        "description": "Extraire chaque page comme image pour analyse",
                        "tool": "pdf-tools.display_page_as_image",
                        "args": {"name": pdf_path.name, "page_number": 1}  # Répéter pour chaque page
                    }
                },
                "content_core": {
                    "extract_content": {
                        "description": "Extraction intelligente complémentaire avec IA",
                        "tool": "content-core.extract_content",
                        "args": {"file_path": str(pdf_path)}
                    }
                }
            }
        }
        
        return result
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Instructions pour extraire les métadonnées via pdf-tools MCP
        
        L'agent Cursor doit utiliser: pdf-tools.get_metadata
        """
        return {
            "mcp_tool": "pdf-tools.get_metadata",
            "args": {"name": pdf_path.name},
            "description": "Extrait les métadonnées du PDF (titre, auteur, nombre de pages, etc.)"
        }
    
    def extract_text(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Instructions pour extraire le texte via pdf-tools MCP
        
        L'agent Cursor doit utiliser: pdf-tools.get_text_json ou pdf-tools.get_text_blocks
        """
        return {
            "mcp_tool": "pdf-tools.get_text_json",
            "args": {"name": pdf_path.name},
            "alternative": "pdf-tools.get_text_blocks",
            "description": "Extrait le texte structuré du PDF avec positions et formatage"
        }
    
    def extract_images(self, pdf_path: Path, page_numbers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Instructions pour extraire les images via pdf-tools MCP
        
        L'agent Cursor doit utiliser: pdf-tools.display_page_as_image pour chaque page
        """
        instructions = []
        
        # Si page_numbers n'est pas fourni, extraire toutes les pages
        # L'agent devra d'abord obtenir le nombre de pages via get_metadata
        
        if page_numbers:
            for page_num in page_numbers:
                instructions.append({
                    "mcp_tool": "pdf-tools.display_page_as_image",
                    "args": {"name": pdf_path.name, "page_number": page_num},
                    "description": f"Extrait la page {page_num} comme image pour analyse"
                })
        else:
            instructions.append({
                "mcp_tool": "pdf-tools.display_page_as_image",
                "args": {"name": pdf_path.name, "page_number": 1},  # Commencer par la page 1
                "description": "Extrait chaque page comme image (répéter pour toutes les pages)",
                "note": "Obtenir d'abord le nombre de pages via get_metadata"
            })
        
        return instructions
    
    def extract_with_content_core(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Instructions pour extraction intelligente via content-core MCP
        
        L'agent Cursor doit utiliser: content-core.extract_content
        """
        return {
            "mcp_tool": "content-core.extract_content",
            "args": {"file_path": str(pdf_path)},
            "description": "Extraction intelligente avec analyse IA du contenu",
            "note": "Content-core utilise OpenAI pour analyser le contenu intelligemment"
        }


def extract_pdf_enhanced(pdf_path: Path, use_mcps: bool = True) -> Dict[str, Any]:
    """
    Fonction principale d'extraction PDF améliorée
    
    Args:
        pdf_path: Chemin vers le PDF
        use_mcps: Si True, retourne les instructions pour utiliser les MCPs
    
    Returns:
        Dictionnaire avec le contenu extrait ou instructions MCP
    """
    if not pdf_path.exists():
        return {"error": f"Fichier non trouvé: {pdf_path}"}
    
    extractor = PDFExtractorEnhanced()
    
    if use_mcps:
        # Retourner les instructions pour utiliser les MCPs
        return extractor.extract_with_mcp_tools(pdf_path)
    else:
        # Fallback vers extraction manuelle si nécessaire
        # (pour compatibilité)
        from scripts.extract_pdf import PDFExtractor
        fallback_extractor = PDFExtractor()
        return fallback_extractor.extract(pdf_path)


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: extract_pdf_enhanced.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        sys.exit(1)
    
    print(f"📄 Extraction PDF améliorée: {pdf_path.name}")
    print(f"\n📋 Instructions pour utiliser les MCPs:\n")
    
    result = extract_pdf_enhanced(pdf_path, use_mcps=True)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Instructions générées")
    print(f"   L'agent Cursor utilisera directement les outils MCP pour l'extraction")


if __name__ == "__main__":
    main()
