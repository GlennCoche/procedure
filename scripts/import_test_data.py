#!/usr/bin/env python3
"""
Script d'import de données de test à partir de documents techniques
Supporte les documents d'alarmes, manuels de maintenance, etc.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
        USE_PDFPLUMBER = True
    except ImportError:
        PDF_AVAILABLE = False
        USE_PDFPLUMBER = False


@dataclass
class AlarmData:
    """Structure pour une alarme extraite d'un document"""
    alarm_id: str
    alarm_name: str
    severity: str  # Critical, Major, Minor, Warning
    possible_causes: List[Dict[str, str]]  # [{cause_id: str, description: str}]
    suggestions: List[str]
    brand: str
    model: str = ""


@dataclass
class ProcedureData:
    """Structure pour une procédure à créer"""
    title: str
    description: str
    category: str
    tags: List[str]
    steps: List[Dict[str, Any]]


class DocumentParser:
    """Parser pour extraire les données des documents techniques"""
    
    def __init__(self, brand: str = "Huawei"):
        self.brand = brand
    
    def parse_pdf(self, pdf_path: str) -> List[AlarmData]:
        """Parser un PDF de référence d'alarmes"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 ou pdfplumber requis. Installez avec: pip install PyPDF2 pdfplumber")
        
        alarms = []
        
        try:
            if USE_PDFPLUMBER:
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            else:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            
            # Parser le texte pour extraire les alarmes
            alarms = self._parse_alarm_text(text)
            
        except Exception as e:
            print(f"Erreur lors du parsing du PDF: {e}")
            raise
        
        return alarms
    
    def _parse_alarm_text(self, text: str) -> List[AlarmData]:
        """Parser le texte pour extraire les alarmes (format Huawei EMMA)"""
        alarms = []
        
        # Pattern pour détecter les sections d'alarmes
        # Format attendu: "Alarm ID | Alarm Name | Alarm Severity"
        lines = text.split('\n')
        current_alarm = None
        current_section = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Détecter le début d'une alarme (format: "2 4000 Inverter Communication Error")
            if line and line[0].isdigit() and ' ' in line:
                parts = line.split(None, 2)
                if len(parts) >= 2 and parts[1].isdigit() and len(parts[1]) == 4:
                    # Nouvelle alarme détectée
                    if current_alarm:
                        alarms.append(current_alarm)
                    
                    alarm_id = parts[1]
                    alarm_name = parts[2] if len(parts) > 2 else ""
                    
                    # Chercher la sévérité dans les lignes suivantes
                    severity = "Major"
                    for j in range(i+1, min(i+10, len(lines))):
                        if "Critical" in lines[j]:
                            severity = "Critical"
                            break
                        elif "Major" in lines[j]:
                            severity = "Major"
                            break
                        elif "Minor" in lines[j]:
                            severity = "Minor"
                            break
                        elif "Warning" in lines[j]:
                            severity = "Warning"
                            break
                    
                    current_alarm = AlarmData(
                        alarm_id=alarm_id,
                        alarm_name=alarm_name,
                        severity=severity,
                        possible_causes=[],
                        suggestions=[],
                        brand=self.brand
                    )
                    current_section = None
            
            # Détecter les sections
            elif current_alarm:
                if "Possible Cause" in line:
                    current_section = "causes"
                elif "Suggestion" in line or "Cause ID" in line:
                    current_section = "suggestions"
                elif current_section == "causes" and line and not line.startswith("|"):
                    # Extraire les causes
                    if "Cause ID" not in line and line.strip():
                        current_alarm.possible_causes.append({
                            "cause_id": str(len(current_alarm.possible_causes) + 1),
                            "description": line
                        })
                elif current_section == "suggestions" and line and not line.startswith("|"):
                    # Extraire les suggestions
                    if line.strip() and not line.startswith("Cause ID"):
                        current_alarm.suggestions.append(line)
            
            i += 1
        
        # Ajouter la dernière alarme
        if current_alarm:
            alarms.append(current_alarm)
        
        return alarms
    
    def alarm_to_procedure(self, alarm: AlarmData) -> ProcedureData:
        """Convertir une alarme en procédure de maintenance"""
        steps = []
        order = 1
        
        # Étape 1: Identifier l'alarme
        steps.append({
            "title": f"Identifier l'alarme {alarm.alarm_id}",
            "description": f"Vérifier que l'alarme {alarm.alarm_id} ({alarm.alarm_name}) est bien présente sur l'équipement {alarm.brand}",
            "instructions": f"Accéder au menu de monitoring de l'application et localiser l'équipement présentant l'alarme {alarm.alarm_id}.",
            "order": order,
            "validation_type": "manual"
        })
        order += 1
        
        # Étapes pour chaque cause possible
        for idx, cause in enumerate(alarm.possible_causes, 1):
            steps.append({
                "title": f"Vérifier la cause {idx}: {cause.get('description', 'Cause inconnue')[:50]}",
                "description": cause.get('description', ''),
                "instructions": self._generate_instructions_for_cause(cause, alarm),
                "order": order,
                "validation_type": "manual"
            })
            order += 1
        
        # Étapes pour les suggestions
        for idx, suggestion in enumerate(alarm.suggestions, 1):
            if suggestion.strip():
                steps.append({
                    "title": f"Action {idx}: {suggestion[:50]}",
                    "description": suggestion,
                    "instructions": self._format_suggestion_as_instructions(suggestion),
                    "order": order,
                    "validation_type": "manual"
                })
                order += 1
        
        # Créer la procédure
        return ProcedureData(
            title=f"Résolution alarme {alarm.alarm_id}: {alarm.alarm_name} ({alarm.brand})",
            description=f"Procédure de résolution pour l'alarme {alarm.alarm_id} ({alarm.alarm_name}) sur équipement {alarm.brand}. Sévérité: {alarm.severity}",
            category=f"Alarmes {alarm.brand}",
            tags=[alarm.brand, f"Alarme-{alarm.alarm_id}", alarm.severity.lower(), "maintenance"],
            steps=steps
        )
    
    def _generate_instructions_for_cause(self, cause: Dict[str, str], alarm: AlarmData) -> str:
        """Générer des instructions détaillées pour une cause"""
        description = cause.get('description', '')
        
        instructions = f"Vérifier: {description}\n\n"
        
        # Instructions spécifiques selon le type de cause
        if "cable" in description.lower() or "connection" in description.lower():
            instructions += "1. Vérifier visuellement les connexions\n"
            instructions += "2. Tester la continuité des câbles si nécessaire\n"
            instructions += "3. Vérifier que les connecteurs sont bien serrés\n"
        elif "certificate" in description.lower():
            instructions += "1. Vérifier la date système de l'équipement\n"
            instructions += "2. Contacter le support technique pour un nouveau certificat\n"
        elif "power" in description.lower():
            instructions += "1. Vérifier l'alimentation électrique\n"
            instructions += "2. Contrôler les fusibles et disjoncteurs\n"
        
        return instructions
    
    def _format_suggestion_as_instructions(self, suggestion: str) -> str:
        """Formater une suggestion comme instructions étape par étape"""
        # Si la suggestion contient des numéros, les garder
        if suggestion.strip()[0].isdigit() or suggestion.startswith("•"):
            return suggestion
        else:
            # Ajouter une structure si nécessaire
            return f"1. {suggestion}"


class DataImporter:
    """Classe pour importer les données via l'API"""
    
    def __init__(self, api_url: str = "http://localhost:8000", admin_token: str = None):
        self.api_url = api_url.rstrip('/')
        self.admin_token = admin_token
        self.session = requests.Session()
        if admin_token:
            self.session.headers.update({"Authorization": f"Bearer {admin_token}"})
    
    def login(self, email: str, password: str) -> bool:
        """Se connecter et obtenir un token"""
        try:
            response = self.session.post(
                f"{self.api_url}/api/auth/login",
                data={"username": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    return True
        except Exception as e:
            print(f"Erreur de connexion: {e}")
        return False
    
    def create_procedure(self, procedure_data: ProcedureData) -> Optional[Dict]:
        """Créer une procédure via l'API"""
        payload = {
            "title": procedure_data.title,
            "description": procedure_data.description,
            "category": procedure_data.category,
            "tags": procedure_data.tags,
            "steps": procedure_data.steps
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/api/procedures",
                json=payload
            )
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Erreur création procédure: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erreur lors de la création de la procédure: {e}")
        
        return None
    
    def create_tip(self, title: str, content: str, category: str = None, tags: List[str] = None) -> Optional[Dict]:
        """Créer un tip via l'API"""
        payload = {
            "title": title,
            "content": content,
            "category": category or "Général",
            "tags": tags or []
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/api/tips",
                json=payload
            )
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Erreur création tip: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erreur lors de la création du tip: {e}")
        
        return None


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Importer des données de test depuis des documents techniques")
    parser.add_argument("--pdf", type=str, help="Chemin vers le PDF à parser")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="URL de l'API")
    parser.add_argument("--email", type=str, default="admin@procedures.local", help="Email admin")
    parser.add_argument("--password", type=str, default="admin123", help="Mot de passe admin")
    parser.add_argument("--brand", type=str, default="Huawei", help="Marque de l'équipement")
    parser.add_argument("--dry-run", action="store_true", help="Mode test sans insertion")
    
    args = parser.parse_args()
    
    # Initialiser l'importeur
    importer = DataImporter(api_url=args.api_url)
    
    if not args.dry_run:
        # Se connecter
        print(f"Connexion à l'API avec {args.email}...")
        if not importer.login(args.email, args.password):
            print("❌ Échec de la connexion. Vérifiez les identifiants.")
            return
        print("✅ Connexion réussie")
    
    # Parser le document
    if args.pdf:
        if not os.path.exists(args.pdf):
            print(f"❌ Fichier PDF non trouvé: {args.pdf}")
            return
        
        print(f"📄 Parsing du document: {args.pdf}")
        parser = DocumentParser(brand=args.brand)
        
        try:
            alarms = parser.parse_pdf(args.pdf)
            print(f"✅ {len(alarms)} alarmes extraites")
            
            # Convertir en procédures
            procedures_created = 0
            tips_created = 0
            
            for alarm in alarms:
                print(f"\n📋 Traitement de l'alarme {alarm.alarm_id}: {alarm.alarm_name}")
                
                # Créer la procédure
                procedure_data = parser.alarm_to_procedure(alarm)
                
                if args.dry_run:
                    print(f"  [DRY-RUN] Procédure: {procedure_data.title}")
                    print(f"  [DRY-RUN] {len(procedure_data.steps)} étapes")
                else:
                    result = importer.create_procedure(procedure_data)
                    if result:
                        procedures_created += 1
                        print(f"  ✅ Procédure créée (ID: {result.get('id')})")
                    
                    # Créer un tip avec les informations de l'alarme
                    tip_content = f"**Alarme {alarm.alarm_id}: {alarm.alarm_name}**\n\n"
                    tip_content += f"**Sévérité:** {alarm.severity}\n\n"
                    tip_content += f"**Causes possibles:**\n"
                    for cause in alarm.possible_causes:
                        tip_content += f"- {cause.get('description', '')}\n"
                    tip_content += f"\n**Suggestions:**\n"
                    for suggestion in alarm.suggestions:
                        tip_content += f"- {suggestion}\n"
                    
                    tip_result = importer.create_tip(
                        title=f"Référence: Alarme {alarm.alarm_id} - {alarm.alarm_name}",
                        content=tip_content,
                        category=f"Alarmes {args.brand}",
                        tags=[args.brand, f"Alarme-{alarm.alarm_id}", alarm.severity.lower()]
                    )
                    if tip_result:
                        tips_created += 1
                        print(f"  ✅ Tip créé (ID: {tip_result.get('id')})")
            
            print(f"\n✨ Import terminé:")
            print(f"  - {procedures_created} procédures créées")
            print(f"  - {tips_created} tips créés")
            
        except Exception as e:
            print(f"❌ Erreur lors du parsing: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Aucun fichier PDF spécifié. Utilisez --pdf pour spécifier un fichier.")


if __name__ == "__main__":
    main()
