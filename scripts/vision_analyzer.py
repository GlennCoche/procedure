#!/usr/bin/env python3
"""
Analyseur d'images utilisant pdf-tools MCP pour extraction et OpenAI Vision API pour analyse
"""

import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
import os


class VisionAnalyzer:
    """
    Analyseur d'images utilisant pdf-tools MCP + OpenAI Vision API
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Args:
            openai_api_key: Clé API OpenAI (ou depuis env)
        """
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY requis pour l'analyse Vision")
        
        self.client = OpenAI(api_key=openai_api_key)
    
    def extract_images_from_pdf(self, pdf_path: Path, page_numbers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Instructions pour extraire les images via pdf-tools MCP
        
        L'agent Cursor doit utiliser: pdf-tools.display_page_as_image
        
        Args:
            pdf_path: Chemin vers le PDF
            page_numbers: Pages à extraire (None = toutes)
        
        Returns:
            Instructions pour utiliser pdf-tools MCP
        """
        instructions = []
        
        # D'abord obtenir le nombre de pages
        instructions.append({
            "step": 1,
            "mcp_tool": "pdf-tools.get_metadata",
            "args": {"name": pdf_path.name},
            "description": "Obtenir le nombre de pages"
        })
        
        # Ensuite extraire chaque page comme image
        if page_numbers:
            for page_num in page_numbers:
                instructions.append({
                    "step": 2,
                    "mcp_tool": "pdf-tools.display_page_as_image",
                    "args": {"name": pdf_path.name, "page_number": page_num},
                    "description": f"Extraire la page {page_num} comme image"
                })
        else:
            instructions.append({
                "step": 2,
                "mcp_tool": "pdf-tools.display_page_as_image",
                "args": {"name": pdf_path.name, "page_number": 1},
                "description": "Extraire chaque page comme image (répéter pour toutes les pages)",
                "note": "Utiliser le résultat de get_metadata pour connaître le nombre de pages"
            })
        
        return instructions
    
    def analyze_image_with_vision(self, image_data: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyser une image avec OpenAI Vision API
        
        Args:
            image_data: Données image (base64 ou chemin fichier)
            context: Contexte du document pour améliorer l'analyse
        
        Returns:
            Analyse de l'image
        """
        # Préparer le prompt
        prompt = """
Analyse cette image d'un document technique photovoltaïque.

Identifie :
1. Le type d'image (schéma électrique, diagramme de connexion, photo d'équipement, graphique, tableau)
2. Le contenu principal et les éléments visibles
3. Les informations techniques importantes
4. Les connexions, labels, valeurs numériques
5. Les éléments de sécurité ou d'avertissement

Génère une description détaillée et structurée en JSON.
"""
        
        if context:
            prompt += f"\n\nContexte du document : {context}"
        
        # Préparer l'image
        if Path(image_data).exists():
            # Lire le fichier et convertir en base64
            with open(image_data, 'rb') as f:
                image_bytes = f.read()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
        else:
            # Déjà en base64
            base64_image = image_data
        
        # Appel à OpenAI Vision API
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parser le JSON si possible
            try:
                analysis = json.loads(analysis_text)
            except:
                analysis = {"description": analysis_text}
            
            return {
                "success": True,
                "analysis": analysis,
                "image_type": self._classify_image_type(analysis),
                "raw_response": analysis_text
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def _classify_image_type(self, analysis: Dict[str, Any]) -> str:
        """Classifier le type d'image depuis l'analyse"""
        description = str(analysis.get("description", "")).lower()
        
        if any(word in description for word in ["schéma", "diagram", "wiring", "connexion"]):
            return "diagram"
        elif any(word in description for word in ["photo", "image", "picture"]):
            return "photo"
        elif any(word in description for word in ["graph", "chart", "courbe"]):
            return "graph"
        elif any(word in description for word in ["table", "tableau", "grid"]):
            return "table"
        else:
            return "unknown"
    
    def analyze_all_pages(self, pdf_path: Path, extraction_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Analyser toutes les pages d'un PDF
        
        Args:
            pdf_path: Chemin vers le PDF
            extraction_data: Données d'extraction précédentes (pour contexte)
        
        Returns:
            Liste d'analyses d'images
        """
        # Instructions pour l'agent Cursor
        return {
            "mcp_instructions": self.extract_images_from_pdf(pdf_path),
            "vision_analysis": {
                "description": "Pour chaque image extraite via pdf-tools, utiliser analyze_image_with_vision",
                "context": extraction_data.get("text", "")[:500] if extraction_data else None
            },
            "workflow": [
                "1. Extraire toutes les pages comme images via pdf-tools.display_page_as_image",
                "2. Pour chaque image, utiliser OpenAI Vision API (GPT-4o) pour analyser",
                "3. Classifier le type d'image (diagram, photo, graph, table)",
                "4. Stocker les résultats dans document_images via sqlite.create_record"
            ]
        }


def analyze_images_from_pdf(pdf_path: Path, openai_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour analyser les images d'un PDF
    
    Args:
        pdf_path: Chemin vers le PDF
        openai_api_key: Clé API OpenAI
    
    Returns:
        Instructions pour utiliser pdf-tools MCP + Vision API
    """
    analyzer = VisionAnalyzer(openai_api_key)
    return analyzer.analyze_all_pages(pdf_path)


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: vision_analyzer.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        sys.exit(1)
    
    print(f"👁️  Analyse Vision du document: {pdf_path.name}")
    print(f"\n📋 Instructions pour utiliser pdf-tools MCP + Vision API:\n")
    
    result = analyze_images_from_pdf(pdf_path)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Instructions générées")
    print(f"   L'agent utilisera pdf-tools pour extraire les images")
    print(f"   Puis OpenAI Vision API pour analyser chaque image")


if __name__ == "__main__":
    main()
