#!/usr/bin/env python3
"""
Association intelligente des images aux étapes des procédures
Utilise la similarité sémantique pour matcher images et steps
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@dataclass
class ImageInfo:
    """Information sur une image extraite"""
    id: int
    document_id: int
    page_number: int
    image_url: str
    image_type: str
    description: str
    extracted_text: str
    key_elements: List[str]
    relevance_score: int


@dataclass
class StepInfo:
    """Information sur une étape de procédure"""
    id: int
    procedure_id: int
    order: int
    title: str
    description: str
    instructions: str


class ImageStepAssociator:
    """
    Associe les images extraites aux étapes des procédures
    """
    
    def __init__(self):
        """Initialiser l'associateur"""
        self.openai_client = None
        if OPENAI_API_KEY:
            import openai
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def compute_similarity(self, image: ImageInfo, step: StepInfo) -> float:
        """
        Calculer le score de similarité entre une image et une étape
        
        Args:
            image: Information sur l'image
            step: Information sur l'étape
        
        Returns:
            Score de similarité (0-1)
        """
        score = 0.0
        
        # 1. Correspondance de mots-clés
        step_text = f"{step.title} {step.description or ''} {step.instructions or ''}".lower()
        
        # Vérifier les éléments clés de l'image
        for element in image.key_elements:
            if element.lower() in step_text:
                score += 0.15
        
        # Vérifier le texte extrait de l'image
        if image.extracted_text:
            extracted_words = image.extracted_text.lower().split()
            for word in extracted_words:
                if len(word) > 3 and word in step_text:
                    score += 0.05
        
        # 2. Correspondance de type d'image avec catégorie d'étape
        type_matches = {
            'diagram': ['installation', 'montage', 'connexion', 'branchement', 'câblage'],
            'photo': ['vérification', 'contrôle', 'inspection', 'visuel'],
            'graph': ['mesure', 'test', 'courbe', 'paramètre'],
            'table': ['configuration', 'paramètre', 'réglage', 'valeur'],
            'icon': ['indicateur', 'icône', 'led', 'affichage', 'écran']
        }
        
        if image.image_type in type_matches:
            for keyword in type_matches[image.image_type]:
                if keyword in step_text:
                    score += 0.1
        
        # 3. Correspondance description image / étape
        if image.description:
            desc_words = [w.lower() for w in image.description.split() if len(w) > 4]
            for word in desc_words:
                if word in step_text:
                    score += 0.03
        
        # Normaliser le score entre 0 et 1
        return min(1.0, score)
    
    def associate_with_ai(self, image: ImageInfo, steps: List[StepInfo]) -> Optional[int]:
        """
        Utiliser l'IA pour associer une image à la meilleure étape
        
        Args:
            image: Information sur l'image
            steps: Liste des étapes candidates
        
        Returns:
            ID de l'étape la plus pertinente ou None
        """
        if not self.openai_client or not steps:
            return None
        
        try:
            steps_text = "\n".join([
                f"Étape {s.order} (ID:{s.id}): {s.title}\n   {s.description or ''}\n   {s.instructions or ''}"
                for s in steps
            ])
            
            prompt = f"""Tu es un expert en documentation technique photovoltaïque.

IMAGE À ASSOCIER:
- Type: {image.image_type}
- Description: {image.description}
- Texte extrait: {image.extracted_text}
- Éléments clés: {', '.join(image.key_elements)}

ÉTAPES DISPONIBLES:
{steps_text}

Quelle étape correspond le mieux à cette image ?
Réponds UNIQUEMENT avec l'ID de l'étape (un nombre) ou "NONE" si aucune ne correspond.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu associes des images techniques à des étapes de procédures. Réponds uniquement avec un ID numérique ou NONE."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if result.upper() == "NONE":
                return None
            
            return int(result)
            
        except Exception as e:
            print(f"❌ Erreur association IA: {e}")
            return None
    
    def associate_images_to_steps(
        self,
        images: List[ImageInfo],
        steps: List[StepInfo],
        use_ai: bool = True,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Associer une liste d'images aux étapes les plus pertinentes
        
        Args:
            images: Liste des images
            steps: Liste des étapes
            use_ai: Utiliser l'IA pour les associations ambiguës
            min_similarity: Score minimum pour une association
        
        Returns:
            Liste des associations (image_id, step_id, score, method)
        """
        associations = []
        
        for image in images:
            print(f"\n📸 Association image page {image.page_number}...")
            
            # Calculer la similarité avec chaque étape
            scores = []
            for step in steps:
                score = self.compute_similarity(image, step)
                if score > 0:
                    scores.append((step, score))
            
            # Trier par score décroissant
            scores.sort(key=lambda x: x[1], reverse=True)
            
            if scores and scores[0][1] >= min_similarity:
                # Association par similarité
                best_step, best_score = scores[0]
                associations.append({
                    "image_id": image.id,
                    "step_id": best_step.id,
                    "score": best_score,
                    "method": "similarity",
                    "image_url": image.image_url,
                    "image_type": image.image_type,
                    "description": image.description
                })
                print(f"  ✅ Associée à étape {best_step.order}: {best_step.title} (score: {best_score:.2f})")
            
            elif use_ai and self.openai_client:
                # Essayer avec l'IA
                ai_step_id = self.associate_with_ai(image, steps)
                if ai_step_id:
                    ai_step = next((s for s in steps if s.id == ai_step_id), None)
                    if ai_step:
                        associations.append({
                            "image_id": image.id,
                            "step_id": ai_step_id,
                            "score": 0.5,  # Score par défaut pour IA
                            "method": "ai",
                            "image_url": image.image_url,
                            "image_type": image.image_type,
                            "description": image.description
                        })
                        print(f"  ✅ Associée (IA) à étape {ai_step.order}: {ai_step.title}")
                    else:
                        print(f"  ⚠️ Pas d'association trouvée")
                else:
                    print(f"  ⚠️ Pas d'association trouvée")
            else:
                print(f"  ⚠️ Pas d'association trouvée (score max: {scores[0][1]:.2f} < {min_similarity})")
        
        return associations
    
    def generate_step_photos_json(self, associations: List[Dict[str, Any]]) -> Dict[int, str]:
        """
        Générer le JSON photos pour chaque step
        
        Args:
            associations: Liste des associations
        
        Returns:
            Dict step_id -> JSON photos
        """
        step_photos = {}
        
        # Grouper par step_id
        for assoc in associations:
            step_id = assoc["step_id"]
            if step_id not in step_photos:
                step_photos[step_id] = []
            
            step_photos[step_id].append({
                "url": assoc["image_url"],
                "type": assoc["image_type"],
                "description": assoc["description"],
                "order": len(step_photos[step_id])
            })
        
        # Convertir en JSON string
        return {
            step_id: json.dumps(photos, ensure_ascii=False)
            for step_id, photos in step_photos.items()
        }


def main():
    """Fonction principale de test"""
    print("🔗 Associateur Images-Steps")
    print("=" * 50)
    print("\nCe script associe les images extraites aux étapes des procédures.")
    print("\nUtilisation via l'orchestrateur intelligent_import.py:")
    print("  1. Extraire les images avec extract_images.py")
    print("  2. Stocker les métadonnées dans document_images (SQLite)")
    print("  3. Exécuter ce script pour associer aux steps")
    print("  4. Mettre à jour le champ 'photos' des steps")
    print("\nMéthodes d'association:")
    print("  - Similarité textuelle (mots-clés, éléments, description)")
    print("  - IA (GPT-4o-mini pour les cas ambigus)")


if __name__ == "__main__":
    main()
