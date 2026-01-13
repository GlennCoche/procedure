#!/usr/bin/env python3
"""
Analyseur IA contextuel utilisant content-core MCP
Analyse les documents comme un expert photovoltaïque
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


# Prompt système expert photovoltaïque
EXPERT_ANALYSIS_PROMPT = """
Tu es un expert senior en maintenance photovoltaïque avec 20 ans d'expérience sur le terrain.

Document à analyser : {document_title}
Marque : {brand}
Type : {file_type}

Tâches :
1. Identifie le type de document (manuel installation, guide maintenance, référence alarmes, configuration, etc.)
2. Extrais la structure logique (sections principales, procédures, étapes)
3. Identifie les procédures techniques détaillées avec leurs étapes
4. Extrais les conseils pratiques, astuces, et informations critiques
5. Analyse les images/schémas fournis et génère des descriptions pertinentes
6. Identifie les informations de sécurité importantes
7. Extrais les paramètres techniques, valeurs de référence, contacts

Format de réponse JSON structuré :
{{
  "document_type": "...",
  "equipment_brand": "...",
  "equipment_model": "...",
  "main_sections": [...],
  "procedures_detected": [...],
  "tips_detected": [...],
  "critical_info": {{...}},
  "images_analysis": [...]
}}
"""


class AIAnalyzer:
    """
    Analyseur IA utilisant content-core MCP pour l'analyse contextuelle
    """
    
    def __init__(self):
        """Initialiser l'analyseur"""
        pass
    
    def analyze_document(self, pdf_path: Path, extraction_data: Dict[str, Any], 
                        brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyser un document en utilisant content-core MCP
        
        L'agent Cursor doit utiliser: content-core.extract_content
        
        Args:
            pdf_path: Chemin vers le PDF
            extraction_data: Données d'extraction précédentes (de pdf-tools)
            brand: Marque de l'équipement (si connue)
        
        Returns:
            Instructions pour utiliser content-core MCP + prompt expert
        """
        file_name = pdf_path.name
        file_type = pdf_path.suffix.lower()
        
        # Détecter la marque depuis le chemin si non fournie
        if not brand:
            path_parts = pdf_path.parts
            if 'docs' in path_parts:
                docs_index = path_parts.index('docs')
                if docs_index + 1 < len(path_parts):
                    brand = path_parts[docs_index + 1]
        
        return {
            "mcp_instructions": {
                "content_core": {
                    "tool": "content-core.extract_content",
                    "args": {
                        "file_path": str(pdf_path)
                    },
                    "description": "Extraction intelligente avec analyse IA du contenu"
                }
            },
            "expert_prompt": EXPERT_ANALYSIS_PROMPT.format(
                document_title=file_name,
                brand=brand or "Inconnue",
                file_type=file_type
            ),
            "analysis_steps": [
                {
                    "step": 1,
                    "action": "Utiliser content-core.extract_content avec file_path",
                    "description": "Content-core extrait et analyse le contenu avec OpenAI"
                },
                {
                    "step": 2,
                    "action": "Combiner avec extraction_data de pdf-tools",
                    "description": "Fusionner les résultats de pdf-tools et content-core"
                },
                {
                    "step": 3,
                    "action": "Analyser avec le prompt expert",
                    "description": "Utiliser le prompt expert pour structurer l'analyse",
                    "prompt": EXPERT_ANALYSIS_PROMPT
                },
                {
                    "step": 4,
                    "action": "Générer JSON structuré",
                    "description": "Créer la structure JSON avec document_type, procedures_detected, etc."
                }
            ],
            "expected_output": {
                "document_type": "string",
                "equipment_brand": "string",
                "equipment_model": "string",
                "main_sections": ["array of sections"],
                "procedures_detected": ["array of procedures"],
                "tips_detected": ["array of tips"],
                "critical_info": {"object with critical information"},
                "images_analysis": ["array of image analyses"]
            }
        }
    
    def get_expert_prompt(self, document_title: str, brand: str, file_type: str) -> str:
        """Obtenir le prompt expert formaté"""
        return EXPERT_ANALYSIS_PROMPT.format(
            document_title=document_title,
            brand=brand,
            file_type=file_type
        )


def analyze_document_with_ai(pdf_path: Path, extraction_data: Dict[str, Any], 
                            brand: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour analyser un document avec IA
    
    Args:
        pdf_path: Chemin vers le PDF
        extraction_data: Données d'extraction précédentes
        brand: Marque de l'équipement
    
    Returns:
        Instructions pour utiliser content-core MCP
    """
    analyzer = AIAnalyzer()
    return analyzer.analyze_document(pdf_path, extraction_data, brand)


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ai_analyzer.py <pdf_path> [brand]")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    brand = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not pdf_path.exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        sys.exit(1)
    
    print(f"🤖 Analyse IA du document: {pdf_path.name}")
    print(f"\n📋 Instructions pour utiliser content-core MCP:\n")
    
    # Simuler extraction_data
    extraction_data = {
        "text": "Contenu extrait...",
        "metadata": {}
    }
    
    result = analyze_document_with_ai(pdf_path, extraction_data, brand)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Instructions générées")
    print(f"   L'agent Cursor utilisera content-core.extract_content pour l'analyse IA")


if __name__ == "__main__":
    main()
