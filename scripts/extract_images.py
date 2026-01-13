#!/usr/bin/env python3
"""
Extraction et upload d'images depuis les PDFs
Utilise pdf-tools MCP, OpenAI Vision API, et Supabase Storage
"""

import os
import json
import base64
import httpx
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
PROCEDURE_IMAGES_BUCKET = "procedure-images"


class ImageExtractor:
    """
    Extracteur d'images depuis PDFs avec upload Supabase
    """
    
    def __init__(self, local_images_dir: Optional[Path] = None):
        """
        Args:
            local_images_dir: Répertoire local pour cache des images
        """
        if local_images_dir is None:
            local_images_dir = Path(__file__).parent / "local_db" / "images"
        
        self.local_images_dir = Path(local_images_dir)
        self.local_images_dir.mkdir(parents=True, exist_ok=True)
        
        self.openai_client = None
        if OPENAI_API_KEY:
            import openai
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_image_with_vision(self, image_base64: str, context: str = "") -> Dict[str, Any]:
        """
        Analyser une image avec OpenAI Vision API
        
        Args:
            image_base64: Image encodée en base64
            context: Contexte du document pour améliorer l'analyse
        
        Returns:
            Analyse de l'image (type, description, texte extrait)
        """
        if not self.openai_client:
            return {
                "type": "unknown",
                "description": "Vision API non disponible",
                "extracted_text": ""
            }
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Tu es un expert en analyse d'images techniques photovoltaïques.
Analyse l'image et fournis:
1. TYPE: 'diagram' (schéma), 'photo' (photo réelle), 'graph' (graphique/courbe), 'table' (tableau), 'icon' (icône/symbole), 'screenshot' (capture d'écran)
2. DESCRIPTION: Description détaillée du contenu
3. TEXTE: Tout texte visible dans l'image
4. PERTINENCE: Score 1-10 de pertinence pour une procédure technique
5. ELEMENTS: Liste des éléments importants identifiés

Réponds en JSON:
{
  "type": "diagram|photo|graph|table|icon|screenshot",
  "description": "...",
  "extracted_text": "...",
  "relevance_score": 8,
  "key_elements": ["element1", "element2"]
}"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Contexte du document: {context}\n\nAnalyse cette image:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens: 1000
            )
            
            result_text = response.choices[0].message.content
            # Parser le JSON de la réponse
            try:
                # Extraire le JSON s'il est dans un bloc de code
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]
                
                return json.loads(result_text.strip())
            except json.JSONDecodeError:
                return {
                    "type": "unknown",
                    "description": result_text,
                    "extracted_text": "",
                    "relevance_score": 5,
                    "key_elements": []
                }
                
        except Exception as e:
            print(f"❌ Erreur Vision API: {e}")
            return {
                "type": "error",
                "description": str(e),
                "extracted_text": "",
                "relevance_score": 0,
                "key_elements": []
            }
    
    def upload_to_supabase(self, image_data: bytes, file_name: str, content_type: str = "image/png") -> Optional[str]:
        """
        Upload une image vers Supabase Storage
        
        Args:
            image_data: Données binaires de l'image
            file_name: Nom du fichier
            content_type: Type MIME
        
        Returns:
            URL publique de l'image ou None si échec
        """
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("⚠️ Supabase non configuré - sauvegarde locale uniquement")
            return None
        
        try:
            file_path = f"images/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_name}"
            
            upload_url = f"{SUPABASE_URL}/storage/v1/object/{PROCEDURE_IMAGES_BUCKET}/{file_path}"
            
            headers = {
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            }
            
            with httpx.Client() as client:
                response = client.post(upload_url, content=image_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{PROCEDURE_IMAGES_BUCKET}/{file_path}"
                    print(f"✅ Image uploadée: {public_url}")
                    return public_url
                else:
                    print(f"❌ Erreur upload Supabase: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur upload: {e}")
            return None
    
    def save_locally(self, image_data: bytes, file_name: str) -> Path:
        """
        Sauvegarder une image localement
        
        Args:
            image_data: Données binaires
            file_name: Nom du fichier
        
        Returns:
            Chemin du fichier sauvegardé
        """
        file_path = self.local_images_dir / file_name
        file_path.write_bytes(image_data)
        return file_path
    
    def process_pdf_page_image(
        self,
        image_base64: str,
        document_id: int,
        page_number: int,
        document_context: str = ""
    ) -> Dict[str, Any]:
        """
        Traiter une image de page PDF: analyse, upload, et métadonnées
        
        Args:
            image_base64: Image encodée en base64
            document_id: ID du document dans la base
            page_number: Numéro de page
            document_context: Contexte du document (titre, marque, etc.)
        
        Returns:
            Métadonnées complètes de l'image
        """
        print(f"  📸 Traitement page {page_number}...")
        
        # 1. Analyser avec Vision API
        analysis = self.analyze_image_with_vision(image_base64, document_context)
        
        # 2. Décoder l'image
        image_data = base64.b64decode(image_base64)
        file_name = f"doc{document_id}_page{page_number}.png"
        
        # 3. Sauvegarder localement
        local_path = self.save_locally(image_data, file_name)
        
        # 4. Upload vers Supabase
        public_url = self.upload_to_supabase(image_data, file_name)
        
        return {
            "document_id": document_id,
            "page_number": page_number,
            "local_path": str(local_path),
            "public_url": public_url,
            "image_type": analysis.get("type", "unknown"),
            "description": analysis.get("description", ""),
            "extracted_text": analysis.get("extracted_text", ""),
            "relevance_score": analysis.get("relevance_score", 5),
            "key_elements": analysis.get("key_elements", []),
            "processed_at": datetime.now().isoformat()
        }


def extract_all_images_from_pdf(
    pdf_path: Path,
    document_id: int,
    document_context: str = "",
    pages_to_extract: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Extraire toutes les images d'un PDF
    
    Note: Cette fonction génère les instructions pour l'agent Cursor
    qui doit utiliser pdf-tools MCP pour l'extraction réelle.
    
    Args:
        pdf_path: Chemin vers le PDF
        document_id: ID du document
        document_context: Contexte pour l'analyse
        pages_to_extract: Pages spécifiques (None = toutes)
    
    Returns:
        Instructions pour l'agent Cursor
    """
    return {
        "action": "extract_images",
        "pdf_path": str(pdf_path),
        "document_id": document_id,
        "context": document_context,
        "pages": pages_to_extract or "all",
        "instructions": [
            {
                "step": 1,
                "mcp": "pdf-tools",
                "tool": "get_metadata",
                "args": {"file_name": str(pdf_path)},
                "purpose": "Obtenir le nombre de pages"
            },
            {
                "step": 2,
                "mcp": "pdf-tools",
                "tool": "display_page_as_image",
                "args": {"name": str(pdf_path), "page_number": "N"},
                "purpose": "Extraire chaque page comme image",
                "note": "Répéter pour chaque page, N = 1 à page_count"
            },
            {
                "step": 3,
                "action": "process_image",
                "script": "ImageExtractor.process_pdf_page_image()",
                "purpose": "Analyser via Vision API et uploader vers Supabase"
            },
            {
                "step": 4,
                "mcp": "sqlite",
                "tool": "create_record",
                "args": {"table": "document_images"},
                "purpose": "Stocker les métadonnées de l'image"
            }
        ]
    }


def main():
    """Test de l'extracteur d'images"""
    import sys
    
    print("🖼️  Extracteur d'images PDF avec Vision API et Supabase")
    print("=" * 60)
    
    # Vérifier la configuration
    print("\n📋 Configuration:")
    print(f"  - OpenAI API: {'✅ Configuré' if OPENAI_API_KEY else '❌ Non configuré'}")
    print(f"  - Supabase URL: {'✅ Configuré' if SUPABASE_URL else '❌ Non configuré'}")
    print(f"  - Supabase Key: {'✅ Configuré' if SUPABASE_SERVICE_KEY else '❌ Non configuré'}")
    
    if len(sys.argv) < 2:
        print("\n📖 Usage: python extract_images.py <pdf_path> [document_id]")
        print("\nCe script génère des instructions pour l'agent Cursor.")
        print("L'agent doit utiliser pdf-tools MCP pour extraire les images,")
        print("puis ce script pour les analyser et les uploader.")
        sys.exit(0)
    
    pdf_path = Path(sys.argv[1])
    document_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if not pdf_path.exists():
        print(f"\n❌ Fichier non trouvé: {pdf_path}")
        sys.exit(1)
    
    instructions = extract_all_images_from_pdf(pdf_path, document_id, f"Document: {pdf_path.name}")
    
    print(f"\n📋 Instructions d'extraction pour: {pdf_path.name}")
    print(json.dumps(instructions, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
