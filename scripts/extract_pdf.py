#!/usr/bin/env python3
"""
Script d'extraction de contenu depuis les fichiers PDF
Utilise pdfplumber et pymupdf pour extraire texte, structure et métadonnées
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("⚠️  pdfplumber non installé. Installation: pip install pdfplumber")

try:
    import fitz  # pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️  pymupdf non installé. Installation: pip install pymupdf")


class PDFExtractor:
    """Classe pour extraire le contenu des PDFs"""
    
    def __init__(self, prefer_pdfplumber: bool = True):
        """
        Args:
            prefer_pdfplumber: Utiliser pdfplumber en priorité (meilleur pour structure)
        """
        self.prefer_pdfplumber = prefer_pdfplumber and PDFPLUMBER_AVAILABLE
        self.use_pymupdf = PYMUPDF_AVAILABLE
    
    def extract_with_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """Extraire avec pdfplumber (meilleur pour structure)"""
        result = {
            "text": "",
            "pages": [],
            "tables": [],
            "metadata": {},
            "structure": []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Métadonnées
                result["metadata"] = {
                    "pages": len(pdf.pages),
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                    "creation_date": str(pdf.metadata.get("CreationDate", "")),
                    "modification_date": str(pdf.metadata.get("ModDate", ""))
                }
                
                # Extraire texte page par page
                full_text = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text.append(page_text)
                    
                    result["pages"].append({
                        "page_number": i + 1,
                        "text": page_text,
                        "text_length": len(page_text)
                    })
                    
                    # Extraire les tableaux
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            result["tables"].append({
                                "page": i + 1,
                                "table_index": table_idx,
                                "data": table
                            })
                
                result["text"] = "\n\n".join(full_text)
                
                # Détecter la structure (titres, sections)
                result["structure"] = self._detect_structure(result["text"])
        
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Erreur avec pdfplumber sur {pdf_path}: {e}")
        
        return result
    
    def extract_with_pymupdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extraire avec pymupdf (plus rapide, meilleur pour OCR)"""
        result = {
            "text": "",
            "pages": [],
            "metadata": {},
            "structure": []
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            # Métadonnées
            metadata = doc.metadata
            result["metadata"] = {
                "pages": doc.page_count,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }
            
            # Extraire texte page par page
            full_text = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                full_text.append(page_text)
                
                result["pages"].append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "text_length": len(page_text)
                })
            
            result["text"] = "\n\n".join(full_text)
            
            # Détecter la structure
            result["structure"] = self._detect_structure(result["text"])
            
            doc.close()
        
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Erreur avec pymupdf sur {pdf_path}: {e}")
        
        return result
    
    def _detect_structure(self, text: str) -> List[Dict[str, Any]]:
        """Détecter la structure du document (titres, sections)"""
        structure = []
        lines = text.split('\n')
        
        # Patterns pour détecter les titres
        title_patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # Titres en majuscules
            r'^\d+\.\s+[A-Z]',  # Numérotation avec titre
            r'^[A-Z][^.!?]*$',  # Ligne en majuscules sans ponctuation
            r'^Chapitre\s+\d+',  # Chapitres
            r'^Section\s+\d+',  # Sections
        ]
        
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Vérifier si c'est un titre
            is_title = False
            for pattern in title_patterns:
                if re.match(pattern, line):
                    is_title = True
                    break
            
            # Vérifier aussi la longueur et le format
            if not is_title and len(line) < 100 and line.isupper():
                is_title = True
            
            if is_title:
                # Sauvegarder la section précédente
                if current_section:
                    current_section["content"] = "\n".join(section_content)
                    structure.append(current_section)
                
                # Nouvelle section
                current_section = {
                    "title": line,
                    "line_number": i + 1,
                    "level": self._detect_title_level(line),
                    "content": ""
                }
                section_content = []
            else:
                section_content.append(line)
        
        # Ajouter la dernière section
        if current_section:
            current_section["content"] = "\n".join(section_content)
            structure.append(current_section)
        
        return structure
    
    def _detect_title_level(self, title: str) -> int:
        """Détecter le niveau d'un titre (1-3)"""
        # Titre principal (gros, centré souvent)
        if re.match(r'^[A-Z\s]{20,}$', title):
            return 1
        # Sous-titre avec numérotation
        if re.match(r'^\d+\.', title):
            return 2
        # Sous-sous-titre
        if re.match(r'^\d+\.\d+', title):
            return 3
        return 2  # Par défaut
    
    def extract(self, pdf_path: Path) -> Dict[str, Any]:
        """Extraire le contenu d'un PDF"""
        if not pdf_path.exists():
            return {"error": f"Fichier non trouvé: {pdf_path}"}
        
        # Choisir la méthode d'extraction
        if self.prefer_pdfplumber:
            result = self.extract_with_pdfplumber(pdf_path)
            # Si erreur, essayer pymupdf
            if "error" in result and self.use_pymupdf:
                print(f"⚠️  Fallback vers pymupdf pour {pdf_path}")
                result = self.extract_with_pymupdf(pdf_path)
        elif self.use_pymupdf:
            result = self.extract_with_pymupdf(pdf_path)
        else:
            return {"error": "Aucune bibliothèque PDF disponible"}
        
        # Ajouter le chemin du fichier
        result["file_path"] = str(pdf_path)
        result["file_name"] = pdf_path.name
        
        return result


def extract_pdf(pdf_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour extraire un PDF
    
    Args:
        pdf_path: Chemin vers le PDF
        output_path: Chemin optionnel pour sauvegarder le résultat JSON
    
    Returns:
        Dictionnaire avec le contenu extrait
    """
    extractor = PDFExtractor()
    result = extractor.extract(pdf_path)
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Résultat sauvegardé: {output_path}")
    
    return result


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_path> [output_json_path]")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"📄 Extraction de: {pdf_path}")
    result = extract_pdf(pdf_path, output_path)
    
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
    else:
        print(f"✅ Extraction réussie:")
        print(f"  - Pages: {result['metadata'].get('pages', 0)}")
        print(f"  - Texte: {len(result.get('text', ''))} caractères")
        print(f"  - Sections détectées: {len(result.get('structure', []))}")
        print(f"  - Tableaux: {len(result.get('tables', []))}")


if __name__ == "__main__":
    main()
