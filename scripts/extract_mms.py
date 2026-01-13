#!/usr/bin/env python3
"""
Script d'extraction et d'analyse des fichiers MMS (Delta DSS)
Les fichiers MMS sont des fichiers de configuration pour les onduleurs Delta
"""

import os
import json
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class MMSExtractor:
    """Classe pour extraire le contenu des fichiers MMS"""
    
    def __init__(self):
        self.supported_models = []
    
    def detect_file_type(self, file_path: Path) -> str:
        """Détecter le type de fichier MMS"""
        # Lire les premiers octets
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            
            # Vérifier si c'est un fichier texte
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    if 'Delta' in first_line or 'DSS' in first_line:
                        return 'text_config'
            except:
                pass
            
            # Vérifier si c'est un fichier binaire
            if header.startswith(b'\x00') or len(header) > 0:
                # Essayer de détecter le format
                if b'MMS' in header or b'mms' in header:
                    return 'binary_mms'
                return 'binary_unknown'
        
        except Exception as e:
            return f'error: {str(e)}'
        
        return 'unknown'
    
    def extract_text_config(self, file_path: Path) -> Dict[str, Any]:
        """Extraire depuis un fichier de configuration texte"""
        result = {
            "type": "text_config",
            "parameters": {},
            "sections": [],
            "raw_text": ""
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            result["raw_text"] = content
            
            # Parser les paramètres (format clé=valeur)
            lines = content.split('\n')
            current_section = None
            section_content = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Détecter les sections
                if line.startswith('[') and line.endswith(']'):
                    if current_section:
                        result["sections"].append({
                            "name": current_section,
                            "content": "\n".join(section_content),
                            "parameters": self._parse_section_parameters(section_content)
                        })
                    current_section = line[1:-1]
                    section_content = []
                else:
                    section_content.append(line)
                    # Parser paramètre clé=valeur
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            result["parameters"][key] = value
            
            # Ajouter la dernière section
            if current_section:
                result["sections"].append({
                    "name": current_section,
                    "content": "\n".join(section_content),
                    "parameters": self._parse_section_parameters(section_content)
                })
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _parse_section_parameters(self, lines: List[str]) -> Dict[str, Any]:
        """Parser les paramètres d'une section"""
        params = {}
        for line in lines:
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    # Essayer de convertir en nombre
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except:
                        pass
                    params[key] = value
        return params
    
    def extract_binary(self, file_path: Path) -> Dict[str, Any]:
        """Extraire depuis un fichier binaire (tentative)"""
        result = {
            "type": "binary",
            "size": 0,
            "hex_preview": "",
            "text_strings": []
        }
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            result["size"] = len(data)
            result["hex_preview"] = data[:64].hex()
            
            # Extraire les chaînes de caractères ASCII
            strings = re.findall(rb'[\x20-\x7E]{4,}', data)
            result["text_strings"] = [s.decode('ascii', errors='ignore') for s in strings[:20]]
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def extract(self, mms_path: Path) -> Dict[str, Any]:
        """Extraire le contenu d'un fichier MMS"""
        if not mms_path.exists():
            return {"error": f"Fichier non trouvé: {mms_path}"}
        
        result = {
            "file_path": str(mms_path),
            "file_name": mms_path.name,
            "file_size": mms_path.stat().st_size
        }
        
        # Détecter le type
        file_type = self.detect_file_type(mms_path)
        result["detected_type"] = file_type
        
        # Extraire selon le type
        if file_type == 'text_config':
            extracted = self.extract_text_config(mms_path)
            result.update(extracted)
        elif file_type.startswith('binary'):
            extracted = self.extract_binary(mms_path)
            result.update(extracted)
        else:
            # Essayer les deux méthodes
            try:
                extracted = self.extract_text_config(mms_path)
                if "error" not in extracted:
                    result.update(extracted)
                else:
                    extracted = self.extract_binary(mms_path)
                    result.update(extracted)
            except:
                result["error"] = "Impossible d'extraire le contenu"
        
        # Détecter le modèle d'onduleur depuis le nom du fichier ou le chemin
        result["detected_model"] = self._detect_model(mms_path)
        
        return result
    
    def _detect_model(self, file_path: Path) -> Optional[str]:
        """Détecter le modèle d'onduleur depuis le chemin"""
        path_str = str(file_path).lower()
        
        # Modèles Delta connus
        models = [
            'm88', 'm70', 'm50', 'm30', 'm20', 'm15', 'm10', 'm6',
            'h5', 'h3', 'h2.5', 'h5a', '222',
            'flex', 'wifi',
            'bx', 'hybrid', 'e5'
        ]
        
        for model in models:
            if model in path_str:
                return model.upper()
        
        # Chercher dans le nom du fichier
        filename = file_path.name.lower()
        for model in models:
            if model in filename:
                return model.upper()
        
        return None


def extract_mms(mms_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour extraire un fichier MMS
    
    Args:
        mms_path: Chemin vers le fichier MMS
        output_path: Chemin optionnel pour sauvegarder le résultat JSON
    
    Returns:
        Dictionnaire avec le contenu extrait
    """
    extractor = MMSExtractor()
    result = extractor.extract(mms_path)
    
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
        print("Usage: python extract_mms.py <mms_path> [output_json_path]")
        sys.exit(1)
    
    mms_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"📄 Extraction de: {mms_path}")
    result = extract_mms(mms_path, output_path)
    
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
    else:
        print(f"✅ Extraction réussie:")
        print(f"  - Type détecté: {result.get('detected_type', 'unknown')}")
        print(f"  - Modèle: {result.get('detected_model', 'unknown')}")
        if 'sections' in result:
            print(f"  - Sections: {len(result['sections'])}")
        if 'parameters' in result:
            print(f"  - Paramètres: {len(result['parameters'])}")


if __name__ == "__main__":
    main()
