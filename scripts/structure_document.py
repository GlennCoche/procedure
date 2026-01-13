#!/usr/bin/env python3
"""
Script de structuration de documents extraits
Transforme le contenu brut en structure de procédures et steps
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Step:
    """Représente une étape d'une procédure"""
    order: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    validation_type: str = "manual"


@dataclass
class Procedure:
    """Représente une procédure"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = None
    steps: List[Step] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.steps is None:
            self.steps = []


class DocumentStructurer:
    """Classe pour structurer les documents en procédures"""
    
    def __init__(self):
        self.brand_keywords = {
            'ABB': ['ABB', 'TRIO', 'PVS'],
            'Delta': ['Delta', 'DSS', 'M88', 'M70', 'M50'],
            'Huawei': ['Huawei', 'EMMA', 'SUN2000'],
            'Goodwe': ['Goodwe', 'GW'],
            'Sungrow': ['Sungrow', 'SG'],
            'Webdynsun': ['Webdyn', 'Webdynsun']
        }
    
    def detect_brand(self, content: str, file_path: str) -> str:
        """Détecter la marque depuis le contenu ou le chemin"""
        content_upper = content.upper()
        path_upper = file_path.upper()
        
        for brand, keywords in self.brand_keywords.items():
            for keyword in keywords:
                if keyword in content_upper or keyword in path_upper:
                    return brand
        
        # Fallback: chercher dans le chemin
        path_lower = file_path.lower()
        for brand in self.brand_keywords.keys():
            if brand.lower() in path_lower:
                return brand
        
        return "Unknown"
    
    def detect_document_type(self, content: str, title: str = "") -> str:
        """Détecter le type de document"""
        content_lower = content.lower()
        title_lower = title.lower()
        combined = content_lower + " " + title_lower
        
        if any(word in combined for word in ['installation', 'install', 'mise en service']):
            return "Installation"
        elif any(word in combined for word in ['configuration', 'config', 'réglage', 'reglage']):
            return "Configuration"
        elif any(word in combined for word in ['alarme', 'alarm', 'erreur', 'error', 'fault']):
            return "Dépannage"
        elif any(word in combined for word in ['manuel', 'manual', 'guide', 'instruction']):
            return "Manuel"
        elif any(word in combined for word in ['maintenance', 'entretien']):
            return "Maintenance"
        else:
            return "Documentation"
    
    def extract_sections_from_pdf(self, pdf_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extraire les sections depuis les données PDF"""
        sections = []
        
        # Utiliser la structure détectée si disponible
        if "structure" in pdf_data and pdf_data["structure"]:
            for section in pdf_data["structure"]:
                sections.append({
                    "title": section.get("title", ""),
                    "content": section.get("content", ""),
                    "level": section.get("level", 2),
                    "line_number": section.get("line_number", 0)
                })
        else:
            # Fallback: découper par paragraphes
            text = pdf_data.get("text", "")
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            current_section = None
            for para in paragraphs:
                # Détecter si c'est un titre
                if self._is_title(para):
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        "title": para,
                        "content": "",
                        "level": self._detect_title_level(para),
                        "line_number": 0
                    }
                else:
                    if current_section:
                        current_section["content"] += "\n\n" + para
                    else:
                        # Créer une section par défaut
                        current_section = {
                            "title": "Introduction",
                            "content": para,
                            "level": 1,
                            "line_number": 0
                        }
            
            if current_section:
                sections.append(current_section)
        
        return sections
    
    def _is_title(self, text: str) -> bool:
        """Vérifier si un texte est un titre"""
        if len(text) > 200:
            return False
        
        # Titres en majuscules
        if text.isupper() and len(text) > 5:
            return True
        
        # Numérotation
        if re.match(r'^\d+[\.\)]\s+[A-Z]', text):
            return True
        
        # Format chapitre/section
        if re.match(r'^(Chapitre|Section|Partie)\s+\d+', text, re.IGNORECASE):
            return True
        
        return False
    
    def _detect_title_level(self, title: str) -> int:
        """Détecter le niveau d'un titre"""
        if re.match(r'^\d+\.\d+\.\d+', title):
            return 3
        elif re.match(r'^\d+\.\d+', title):
            return 2
        elif re.match(r'^\d+[\.\)]', title):
            return 2
        else:
            return 1
    
    def extract_steps_from_section(self, section_content: str) -> List[Step]:
        """Extraire les étapes depuis le contenu d'une section"""
        steps = []
        
        # Patterns pour détecter les étapes
        step_patterns = [
            r'^\d+[\.\)]\s+(.+?)(?=\n\d+[\.\)]|\n\n|$)',  # 1. Étape
            r'^Étape\s+\d+[\.:]?\s+(.+?)(?=\nÉtape|\n\n|$)',  # Étape 1:
            r'^Step\s+\d+[\.:]?\s+(.+?)(?=\nStep|\n\n|$)',  # Step 1:
        ]
        
        # Essayer chaque pattern
        for pattern in step_patterns:
            matches = re.finditer(pattern, section_content, re.MULTILINE | re.DOTALL)
            for match in matches:
                step_text = match.group(1).strip()
                if len(step_text) > 10:  # Ignorer les très courts
                    # Séparer titre et instructions
                    lines = step_text.split('\n', 1)
                    title = lines[0].strip()
                    instructions = lines[1].strip() if len(lines) > 1 else None
                    
                    steps.append(Step(
                        order=len(steps) + 1,
                        title=title[:255],  # Limiter la longueur
                        description=None,
                        instructions=instructions,
                        validation_type="manual"
                    ))
            
            if steps:
                break
        
        # Si aucun pattern ne fonctionne, découper par paragraphes numérotés
        if not steps:
            lines = section_content.split('\n')
            current_step = None
            step_num = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Détecter début d'étape
                if re.match(r'^\d+[\.\)]', line):
                    if current_step:
                        steps.append(current_step)
                    current_step = Step(
                        order=step_num,
                        title=line[:255],
                        instructions="",
                        validation_type="manual"
                    )
                    step_num += 1
                elif current_step:
                    if current_step.instructions:
                        current_step.instructions += "\n" + line
                    else:
                        current_step.instructions = line
            
            if current_step:
                steps.append(current_step)
        
        return steps
    
    def create_procedures_from_pdf(self, pdf_data: Dict[str, Any], file_path: str) -> List[Procedure]:
        """Créer des procédures depuis les données PDF"""
        procedures = []
        
        # Détecter la marque
        brand = self.detect_brand(pdf_data.get("text", ""), file_path)
        
        # Extraire les sections
        sections = self.extract_sections_from_pdf(pdf_data)
        
        if not sections:
            # Créer une procédure unique avec tout le contenu
            doc_type = self.detect_document_type(pdf_data.get("text", ""), pdf_data.get("file_name", ""))
            title = pdf_data.get("file_name", "Document").replace(".pdf", "")
            
            procedure = Procedure(
                title=title[:255],
                description=pdf_data.get("text", "")[:1000],  # Limiter
                category=f"{brand} - {doc_type}",
                tags=[brand, doc_type, "documentation"]
            )
            
            # Essayer d'extraire des étapes
            steps = self.extract_steps_from_section(pdf_data.get("text", ""))
            if steps:
                procedure.steps = steps
            else:
                # Créer une étape par défaut
                procedure.steps = [Step(
                    order=1,
                    title="Consulter le document",
                    instructions=pdf_data.get("text", "")[:2000],
                    validation_type="manual"
                )]
            
            procedures.append(procedure)
        else:
            # Une procédure par section
            doc_type = self.detect_document_type(pdf_data.get("text", ""), pdf_data.get("file_name", ""))
            
            for section in sections:
                section_title = section.get("title", "Section sans titre")
                section_content = section.get("content", "")
                
                if len(section_content) < 50:  # Ignorer les sections trop courtes
                    continue
                
                # Extraire les étapes
                steps = self.extract_steps_from_section(section_content)
                
                if not steps:
                    # Créer une étape unique avec le contenu
                    steps = [Step(
                        order=1,
                        title="Instructions",
                        instructions=section_content[:2000],
                        validation_type="manual"
                    )]
                
                procedure = Procedure(
                    title=section_title[:255],
                    description=section_content[:500],
                    category=f"{brand} - {doc_type}",
                    tags=[brand, doc_type, "section"],
                    steps=steps
                )
                
                procedures.append(procedure)
        
        return procedures
    
    def create_procedures_from_mms(self, mms_data: Dict[str, Any], file_path: str) -> List[Procedure]:
        """Créer des procédures depuis les données MMS"""
        procedures = []
        
        brand = "Delta"
        model = mms_data.get("detected_model", "Unknown")
        
        # Créer une procédure de configuration
        if "sections" in mms_data and mms_data["sections"]:
            for section in mms_data["sections"]:
                section_name = section.get("name", "Configuration")
                parameters = section.get("parameters", {})
                
                if not parameters:
                    continue
                
                # Créer les étapes pour chaque paramètre important
                steps = []
                step_num = 1
                
                for key, value in list(parameters.items())[:20]:  # Limiter à 20 paramètres
                    steps.append(Step(
                        order=step_num,
                        title=f"Configurer {key}",
                        instructions=f"Paramètre: {key}\nValeur: {value}",
                        validation_type="manual"
                    ))
                    step_num += 1
                
                if steps:
                    procedure = Procedure(
                        title=f"Configuration {model} - {section_name}",
                        description=f"Procédure de configuration pour le modèle {model}, section {section_name}",
                        category=f"Delta - Configuration",
                        tags=["Delta", "Configuration", model, "MMS"],
                        steps=steps
                    )
                    procedures.append(procedure)
        else:
            # Procédure générique
            procedure = Procedure(
                title=f"Configuration {model}",
                description=f"Fichier de configuration MMS pour modèle {model}",
                category="Delta - Configuration",
                tags=["Delta", "Configuration", model, "MMS"],
                steps=[Step(
                    order=1,
                    title="Importer la configuration",
                    instructions=f"Utiliser le fichier MMS: {mms_data.get('file_name', '')}",
                    validation_type="manual"
                )]
            )
            procedures.append(procedure)
        
        return procedures
    
    def create_tips_from_content(self, content: str, brand: str, doc_type: str) -> List[Dict[str, Any]]:
        """Créer des tips depuis le contenu"""
        tips = []
        
        # Chercher des conseils pratiques (phrases avec "conseil", "astuce", "attention", etc.)
        tip_keywords = ['conseil', 'astuce', 'attention', 'important', 'note', 'remarque', 'tip']
        
        sentences = re.split(r'[.!?]\s+', content)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in tip_keywords):
                if len(sentence) > 20 and len(sentence) < 500:
                    tips.append({
                        "title": sentence[:100],
                        "content": sentence,
                        "category": f"{brand} - {doc_type}",
                        "tags": [brand, doc_type, "conseil"]
                    })
        
        return tips


def structure_document(extracted_data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
    """
    Structurer un document extrait
    
    Args:
        extracted_data: Données extraites (PDF ou MMS)
        file_path: Chemin du fichier source
    
    Returns:
        Dictionnaire avec procédures et tips
    """
    structurer = DocumentStructurer()
    
    result = {
        "file_path": file_path,
        "procedures": [],
        "tips": []
    }
    
    # Déterminer le type de document
    if "pages" in extracted_data:  # PDF
        procedures = structurer.create_procedures_from_pdf(extracted_data, file_path)
        brand = structurer.detect_brand(extracted_data.get("text", ""), file_path)
        doc_type = structurer.detect_document_type(extracted_data.get("text", ""))
        
        # Créer des tips
        tips = structurer.create_tips_from_content(
            extracted_data.get("text", ""),
            brand,
            doc_type
        )
        
        result["procedures"] = [asdict(p) for p in procedures]
        result["tips"] = tips
    
    elif "detected_type" in extracted_data:  # MMS
        procedures = structurer.create_procedures_from_mms(extracted_data, file_path)
        result["procedures"] = [asdict(p) for p in procedures]
    
    return result


def main():
    """Fonction principale pour tests"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python structure_document.py <extracted_json_path> [output_json_path]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"📄 Structuration de: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    result = structure_document(extracted_data, str(input_path))
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ Résultat sauvegardé: {output_path}")
    
    print(f"✅ Structuration réussie:")
    print(f"  - Procédures: {len(result['procedures'])}")
    print(f"  - Tips: {len(result['tips'])}")


if __name__ == "__main__":
    main()
