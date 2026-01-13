from openai import OpenAI
from app.core.config import settings
from typing import Dict, Any
import base64

class VisionService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Supporte aussi la vision
    
    async def recognize_equipment(self, image_data: bytes) -> Dict[str, Any]:
        """Reconnaître un équipement via photo"""
        # Encoder l'image en base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        prompt = """Analyse cette photo d'équipement de centrale photovoltaïque et identifie:
1. Le type d'équipement (onduleur, panneau solaire, compteur, coffret électrique, etc.)
2. Le modèle/marque si visible
3. L'état apparent (normal, endommagé, nécessite maintenance)
4. Des suggestions de procédures de maintenance appropriées

Réponds en JSON avec les clés: equipment_type, brand_model, condition, maintenance_suggestions (liste)"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o pour la vision
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
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content or "{}"
            
            # Parser le JSON de la réponse
            try:
                import json
                result = json.loads(result_text)
            except:
                # Si ce n'est pas du JSON valide, créer une structure par défaut
                result = {
                    "equipment_type": "Équipement non identifié",
                    "brand_model": "Non déterminé",
                    "condition": "À vérifier",
                    "maintenance_suggestions": ["Inspection visuelle recommandée"],
                    "raw_response": result_text
                }
            
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "equipment_type": "Erreur d'analyse",
                    "brand_model": "Non déterminé",
                    "condition": "Erreur",
                    "maintenance_suggestions": []
                }
            }
