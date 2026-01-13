#!/usr/bin/env python3
"""
Extraction des réglages spécifiques France depuis les PDFs
Identifie et structure les paramètres techniques pour la France métropolitaine
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@dataclass
class FranceSetting:
    """Paramètre technique spécifique France"""
    brand: str
    equipment_type: str
    model: Optional[str]
    category: str  # tension, frequence, puissance, reseau, communication, protection, injection
    name: str
    value: str
    unit: Optional[str]
    country: str = "FR"
    source_doc: Optional[str] = None
    page_number: Optional[int] = None
    notes: Optional[str] = None
    importance: str = "standard"  # critical, standard, optional


class SettingsExtractor:
    """
    Extracteur de paramètres techniques France depuis documentation PV
    """
    
    # Patterns de détection automatique
    VOLTAGE_PATTERNS = [
        r"(?:tension|voltage|V)\s*(?:nominale?|réseau|AC|DC)?\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*V",
        r"(\d{2,3})\s*V\s*(?:AC|DC|nominal)",
        r"Vmin\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*V",
        r"Vmax\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*V",
        r"Vstart\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*V",
    ]
    
    FREQUENCY_PATTERNS = [
        r"(?:fréquence|frequency|freq)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*Hz",
        r"(\d{2}(?:[.,]\d+)?)\s*Hz",
        r"(?:47|48|49|50|51|52)[.,]?\d*\s*Hz",
    ]
    
    COUNTRY_CODE_PATTERNS = [
        r"(?:code\s*pays|country\s*code)\s*[:=]?\s*([A-Z0-9]{1,4})",
        r"France\s*[:=]?\s*([A-Z0-9]{1,4})",
        r"FR\s*[:=]?\s*(\d[A-F0-9])",
        r"Standard\s*[:=]?\s*(\d[A-F0-9])",
    ]
    
    def __init__(self):
        """Initialiser l'extracteur"""
        self.openai_client = None
        if OPENAI_API_KEY:
            import openai
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def extract_with_patterns(self, text: str, brand: str, equipment_type: str) -> List[FranceSetting]:
        """
        Extraction automatique avec patterns regex
        
        Args:
            text: Texte du document
            brand: Marque de l'équipement
            equipment_type: Type d'équipement
        
        Returns:
            Liste des paramètres détectés
        """
        settings = []
        
        # Recherche de tensions
        for pattern in self.VOLTAGE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).replace(",", ".")
                context = text[max(0, match.start()-50):match.end()+50]
                
                # Déterminer le type de tension
                name = "Tension"
                if "min" in context.lower():
                    name = "Tension minimum"
                elif "max" in context.lower():
                    name = "Tension maximum"
                elif "start" in context.lower():
                    name = "Tension de démarrage"
                elif "nominal" in context.lower():
                    name = "Tension nominale"
                
                settings.append(FranceSetting(
                    brand=brand,
                    equipment_type=equipment_type,
                    model=None,
                    category="TENSION",
                    name=name,
                    value=value,
                    unit="V",
                    notes=f"Détecté automatiquement: ...{context}..."
                ))
        
        # Recherche de fréquences
        for pattern in self.FREQUENCY_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                value = value.replace(",", ".").replace("Hz", "").strip()
                
                settings.append(FranceSetting(
                    brand=brand,
                    equipment_type=equipment_type,
                    model=None,
                    category="FREQUENCE",
                    name="Fréquence réseau",
                    value=value,
                    unit="Hz"
                ))
        
        # Recherche de codes pays
        for pattern in self.COUNTRY_CODE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                code = match.group(1)
                settings.append(FranceSetting(
                    brand=brand,
                    equipment_type=equipment_type,
                    model=None,
                    category="RESEAU",
                    name="Code pays France",
                    value=code,
                    unit=None,
                    importance="critical"
                ))
        
        return settings
    
    def extract_with_ai(
        self,
        text: str,
        brand: str,
        equipment_type: str,
        model: Optional[str] = None
    ) -> List[FranceSetting]:
        """
        Extraction intelligente avec IA
        
        Args:
            text: Texte du document
            brand: Marque
            equipment_type: Type d'équipement
            model: Modèle si connu
        
        Returns:
            Liste des paramètres extraits
        """
        if not self.openai_client:
            print("⚠️ OpenAI non configuré - extraction IA indisponible")
            return []
        
        try:
            from scripts.prompts.expert_prompts import get_settings_extraction_prompt
            prompt = get_settings_extraction_prompt(text, brand, equipment_type)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu extrais les paramètres techniques France depuis des documentations photovoltaïques. Réponds uniquement en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content
            
            # Parser le JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            settings_data = json.loads(result_text.strip())
            
            # Convertir en FranceSetting
            settings = []
            for item in settings_data:
                settings.append(FranceSetting(
                    brand=item.get("brand", brand),
                    equipment_type=item.get("equipment_type", equipment_type),
                    model=item.get("model", model),
                    category=item.get("category", "AUTRE"),
                    name=item.get("name", "Paramètre inconnu"),
                    value=str(item.get("value", "")),
                    unit=item.get("unit"),
                    source_doc=item.get("source_section"),
                    page_number=item.get("page_number"),
                    notes=item.get("notes"),
                    importance=item.get("importance", "standard")
                ))
            
            return settings
            
        except Exception as e:
            print(f"❌ Erreur extraction IA: {e}")
            return []
    
    def extract_settings(
        self,
        text: str,
        brand: str,
        equipment_type: str,
        model: Optional[str] = None,
        source_doc: Optional[str] = None,
        use_ai: bool = True
    ) -> List[FranceSetting]:
        """
        Extraction complète des paramètres France
        
        Args:
            text: Texte du document
            brand: Marque
            equipment_type: Type d'équipement
            model: Modèle
            source_doc: Document source
            use_ai: Utiliser l'IA
        
        Returns:
            Liste des paramètres France
        """
        all_settings = []
        
        # 1. Extraction automatique avec patterns
        print("  🔍 Extraction automatique (patterns)...")
        pattern_settings = self.extract_with_patterns(text, brand, equipment_type)
        all_settings.extend(pattern_settings)
        print(f"     → {len(pattern_settings)} paramètres détectés")
        
        # 2. Extraction IA
        if use_ai:
            print("  🤖 Extraction intelligente (IA)...")
            ai_settings = self.extract_with_ai(text, brand, equipment_type, model)
            all_settings.extend(ai_settings)
            print(f"     → {len(ai_settings)} paramètres extraits")
        
        # 3. Déduplication
        unique_settings = self._deduplicate_settings(all_settings)
        
        # 4. Ajouter source
        for setting in unique_settings:
            if source_doc:
                setting.source_doc = source_doc
        
        return unique_settings
    
    def _deduplicate_settings(self, settings: List[FranceSetting]) -> List[FranceSetting]:
        """Supprimer les doublons"""
        seen = set()
        unique = []
        
        for s in settings:
            key = (s.category, s.name, s.value)
            if key not in seen:
                seen.add(key)
                unique.append(s)
        
        return unique
    
    def format_for_database(self, settings: List[FranceSetting]) -> List[Dict[str, Any]]:
        """
        Formater les paramètres pour insertion en base de données
        
        Args:
            settings: Liste des paramètres
        
        Returns:
            Liste de dictionnaires prêts pour l'insertion
        """
        return [asdict(s) for s in settings]
    
    def generate_sql_inserts(self, settings: List[FranceSetting]) -> str:
        """
        Générer les requêtes SQL d'insertion
        
        Args:
            settings: Liste des paramètres
        
        Returns:
            Requêtes SQL
        """
        sql_lines = []
        
        for s in settings:
            values = [
                f"'{s.brand}'",
                f"'{s.equipment_type}'",
                f"'{s.model}'" if s.model else "NULL",
                f"'{s.category}'",
                f"'{s.name}'",
                f"'{s.value}'",
                f"'{s.unit}'" if s.unit else "NULL",
                f"'{s.country}'",
                f"'{s.source_doc}'" if s.source_doc else "NULL",
                str(s.page_number) if s.page_number else "NULL",
                f"'{s.notes}'" if s.notes else "NULL"
            ]
            
            sql_lines.append(
                f"INSERT INTO settings (brand, equipment_type, model, category, name, value, unit, country, source_doc, page_number, notes) VALUES ({', '.join(values)});"
            )
        
        return "\n".join(sql_lines)


def extract_france_settings(
    document_text: str,
    brand: str,
    equipment_type: str = "onduleur",
    model: Optional[str] = None,
    source_doc: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour extraire les paramètres France
    
    Args:
        document_text: Texte du document
        brand: Marque de l'équipement
        equipment_type: Type d'équipement
        model: Modèle
        source_doc: Document source
    
    Returns:
        Liste des paramètres au format dictionnaire
    """
    extractor = SettingsExtractor()
    settings = extractor.extract_settings(
        document_text,
        brand,
        equipment_type,
        model,
        source_doc
    )
    return extractor.format_for_database(settings)


def main():
    """Test de l'extracteur de réglages France"""
    import sys
    
    print("🇫🇷 Extracteur de Réglages France")
    print("=" * 50)
    
    # Vérifier la configuration
    print("\n📋 Configuration:")
    print(f"  - OpenAI API: {'✅ Configuré' if OPENAI_API_KEY else '❌ Non configuré'}")
    
    if len(sys.argv) < 2:
        print("\n📖 Usage: python extract_settings.py <text_file_or_content>")
        print("\nExemple de texte à analyser:")
        
        # Exemple avec texte ABB TRIO
        example_text = """
        Configuration standard France:
        - Tension réseau: 400V triphasé
        - Fréquence: 50Hz
        - Code pays: 0D (interrupteur 1=0, interrupteur 2=D)
        - Plage de tension: 340V - 460V
        - Plage de fréquence: 47.5Hz - 51.5Hz
        - Temps de reconnexion: 20s minimum
        - Protection différentielle: Type AC 300mA (intégrée 300mA/300ms)
        """
        
        print("\n🔍 Test avec exemple ABB...")
        extractor = SettingsExtractor()
        settings = extractor.extract_settings(
            example_text,
            brand="ABB",
            equipment_type="onduleur",
            model="TRIO-20.0/27.6-TL",
            source_doc="Manuel installateur"
        )
        
        print(f"\n✅ {len(settings)} paramètres extraits:")
        for s in settings:
            print(f"  - [{s.category}] {s.name}: {s.value} {s.unit or ''}")
        
        sys.exit(0)
    
    # Lire le fichier ou utiliser comme texte direct
    input_arg = sys.argv[1]
    
    if Path(input_arg).exists():
        text = Path(input_arg).read_text()
        source = input_arg
    else:
        text = input_arg
        source = "CLI input"
    
    brand = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
    
    extractor = SettingsExtractor()
    settings = extractor.extract_settings(text, brand, "onduleur", source_doc=source)
    
    print(f"\n✅ {len(settings)} paramètres extraits")
    print(json.dumps(extractor.format_for_database(settings), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
