#!/usr/bin/env python3
"""
Script principal d'import de documents techniques
Orchestre l'extraction, la structuration et l'import dans la base de données
"""

import os
import sys
import json
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from tqdm import tqdm
import time

# Ajouter les chemins nécessaires
scripts_dir = Path(__file__).parent
project_root = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(project_root / "backend"))

# Importer les modules d'extraction
from extract_pdf import PDFExtractor, extract_pdf
from extract_mms import MMSExtractor, extract_mms
from structure_document import DocumentStructurer, structure_document


class DocumentImporter:
    """Classe pour importer les documents dans la base de données"""
    
    def __init__(self, api_url: str = "http://localhost:8000", admin_email: str = None, admin_password: str = None):
        self.api_url = api_url.rstrip('/')
        self.admin_email = admin_email
        self.admin_password = admin_password
        self.token = None
        self.admin_user_id = None
        
        # Cache pour éviter les doublons
        self.processed_files = set()
    
    def authenticate(self) -> bool:
        """S'authentifier en tant qu'admin"""
        if not self.admin_email or not self.admin_password:
            print("⚠️  Identifiants admin non fournis, utilisation de l'API publique")
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={
                    "email": self.admin_email,
                    "password": self.admin_password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.admin_user_id = data.get("user", {}).get("id")
                print(f"✅ Authentifié en tant qu'admin (ID: {self.admin_user_id})")
                return True
            else:
                print(f"❌ Erreur d'authentification: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
            return False
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculer le hash d'un fichier pour détecter les doublons"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def create_procedure(self, procedure_data: Dict[str, Any]) -> Optional[int]:
        """Créer une procédure via l'API"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            response = requests.post(
                f"{self.api_url}/api/procedures",
                json=procedure_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("id")
            else:
                print(f"⚠️  Erreur création procédure: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def create_tip(self, tip_data: Dict[str, Any]) -> Optional[int]:
        """Créer un tip via l'API"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            response = requests.post(
                f"{self.api_url}/api/tips",
                json=tip_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("id")
            else:
                print(f"⚠️  Erreur création tip: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def process_pdf(self, pdf_path: Path, brand: str = None) -> Dict[str, Any]:
        """Traiter un fichier PDF"""
        result = {
            "file": str(pdf_path),
            "procedures_created": 0,
            "tips_created": 0,
            "errors": []
        }
        
        try:
            # Extraire le contenu
            print(f"  📄 Extraction: {pdf_path.name}")
            extracted = extract_pdf(pdf_path)
            
            if "error" in extracted:
                result["errors"].append(extracted["error"])
                return result
            
            # Structurer
            print(f"  🔧 Structuration...")
            structured = structure_document(extracted, str(pdf_path))
            
            # Créer les procédures
            for proc_data in structured.get("procedures", []):
                # Ajouter l'ID de l'admin
                if self.admin_user_id:
                    proc_data["createdById"] = self.admin_user_id
                
                # Convertir les steps
                steps = proc_data.pop("steps", [])
                
                # Créer la procédure
                proc_id = self.create_procedure(proc_data)
                if proc_id:
                    result["procedures_created"] += 1
                    print(f"    ✅ Procédure créée: {proc_data.get('title', '')[:50]}")
                    
                    # Créer les steps (nécessite une API pour créer les steps)
                    # Pour l'instant, on les met dans la description
                    if steps:
                        steps_text = "\n\n".join([
                            f"{i+1}. {s.get('title', '')}: {s.get('instructions', '')}"
                            for i, s in enumerate(steps)
                        ])
                        # TODO: Créer les steps via API si disponible
            
            # Créer les tips
            for tip_data in structured.get("tips", []):
                if self.admin_user_id:
                    tip_data["createdById"] = self.admin_user_id
                
                tip_id = self.create_tip(tip_data)
                if tip_id:
                    result["tips_created"] += 1
                    print(f"    ✅ Tip créé: {tip_data.get('title', '')[:50]}")
        
        except Exception as e:
            result["errors"].append(str(e))
            print(f"    ❌ Erreur: {e}")
        
        return result
    
    def process_mms(self, mms_path: Path, brand: str = "Delta") -> Dict[str, Any]:
        """Traiter un fichier MMS"""
        result = {
            "file": str(mms_path),
            "procedures_created": 0,
            "tips_created": 0,
            "errors": []
        }
        
        try:
            # Extraire le contenu
            print(f"  📄 Extraction: {mms_path.name}")
            extracted = extract_mms(mms_path)
            
            if "error" in extracted:
                result["errors"].append(extracted["error"])
                return result
            
            # Structurer
            print(f"  🔧 Structuration...")
            structured = structure_document(extracted, str(mms_path))
            
            # Créer les procédures
            for proc_data in structured.get("procedures", []):
                if self.admin_user_id:
                    proc_data["createdById"] = self.admin_user_id
                
                steps = proc_data.pop("steps", [])
                
                proc_id = self.create_procedure(proc_data)
                if proc_id:
                    result["procedures_created"] += 1
                    print(f"    ✅ Procédure créée: {proc_data.get('title', '')[:50]}")
        
        except Exception as e:
            result["errors"].append(str(e))
            print(f"    ❌ Erreur: {e}")
        
        return result
    
    def import_brand(self, brand: str, docs_dir: Path, file_types: List[str] = None) -> Dict[str, Any]:
        """Importer tous les documents d'une marque"""
        if file_types is None:
            file_types = ['.pdf', '.mms']
        
        brand_dir = docs_dir / brand
        if not brand_dir.exists():
            print(f"❌ Dossier non trouvé: {brand_dir}")
            return {"error": f"Dossier {brand} non trouvé"}
        
        print(f"\n🏭 Import de la marque: {brand}")
        print(f"📁 Dossier: {brand_dir}")
        
        # Trouver tous les fichiers
        files = []
        for ext in file_types:
            files.extend(brand_dir.rglob(f"*{ext}"))
        
        if not files:
            print(f"⚠️  Aucun fichier trouvé pour {brand}")
            return {"files_processed": 0}
        
        print(f"📊 {len(files)} fichiers trouvés")
        
        results = {
            "brand": brand,
            "files_processed": 0,
            "procedures_created": 0,
            "tips_created": 0,
            "errors": []
        }
        
        # Traiter chaque fichier
        for file_path in tqdm(files, desc=f"Import {brand}"):
            # Vérifier si déjà traité
            file_hash = self.get_file_hash(file_path)
            if file_hash in self.processed_files:
                print(f"  ⏭️  Déjà traité: {file_path.name}")
                continue
            
            self.processed_files.add(file_hash)
            
            # Traiter selon le type
            if file_path.suffix.lower() == '.pdf':
                result = self.process_pdf(file_path, brand)
            elif file_path.suffix.lower() == '.mms':
                result = self.process_mms(file_path, brand)
            else:
                continue
            
            results["files_processed"] += 1
            results["procedures_created"] += result.get("procedures_created", 0)
            results["tips_created"] += result.get("tips_created", 0)
            results["errors"].extend(result.get("errors", []))
            
            # Pause pour ne pas surcharger l'API
            time.sleep(0.5)
        
        print(f"\n✅ Import {brand} terminé:")
        print(f"  - Fichiers traités: {results['files_processed']}")
        print(f"  - Procédures créées: {results['procedures_created']}")
        print(f"  - Tips créés: {results['tips_created']}")
        if results["errors"]:
            print(f"  - Erreurs: {len(results['errors'])}")
        
        return results


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Importer des documents techniques")
    parser.add_argument("--brand", type=str, help="Marque à importer (ABB, Delta, Huawei, etc.)")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="URL de l'API")
    parser.add_argument("--email", type=str, help="Email admin")
    parser.add_argument("--password", type=str, help="Mot de passe admin")
    parser.add_argument("--all", action="store_true", help="Importer toutes les marques")
    parser.add_argument("--docs-dir", type=str, default=None, help="Dossier docs/ (par défaut: ../docs)")
    
    args = parser.parse_args()
    
    # Déterminer le dossier docs
    if args.docs_dir:
        docs_dir = Path(args.docs_dir)
    else:
        docs_dir = Path(__file__).parent.parent / "docs"
    
    if not docs_dir.exists():
        print(f"❌ Dossier non trouvé: {docs_dir}")
        return
    
    # Créer l'importeur
    importer = DocumentImporter(
        api_url=args.api_url,
        admin_email=args.email,
        admin_password=args.password
    )
    
    # Authentifier
    if args.email and args.password:
        importer.authenticate()
    
    # Marques disponibles
    brands = ["ABB", "Huawei", "Goodwe", "Sungrow", "Webdynsun", "WebdynsunPM", "Delta", "Bridage Raccordement"]
    
    if args.all:
        # Importer toutes les marques
        for brand in brands:
            importer.import_brand(brand, docs_dir)
    elif args.brand:
        # Importer une marque spécifique
        if args.brand not in brands:
            print(f"⚠️  Marque inconnue: {args.brand}")
            print(f"Marques disponibles: {', '.join(brands)}")
            return
        
        importer.import_brand(args.brand, docs_dir)
    else:
        print("❌ Spécifiez --brand <marque> ou --all")
        parser.print_help()


if __name__ == "__main__":
    main()
