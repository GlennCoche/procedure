#!/usr/bin/env python3
"""
Script d'inventaire des documents techniques
Scanne récursivement le dossier docs/ et génère un rapport JSON/CSV
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import hashlib


def get_file_hash(file_path: Path) -> str:
    """Calculer le hash MD5 d'un fichier"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"error: {str(e)}"


def get_file_info(file_path: Path, base_path: Path) -> Dict[str, Any]:
    """Extraire les informations d'un fichier"""
    stat = file_path.stat()
    
    # Déterminer la marque depuis le chemin
    relative_path = file_path.relative_to(base_path)
    parts = relative_path.parts
    brand = parts[0] if len(parts) > 0 else "Unknown"
    
    # Déterminer le type de fichier
    ext = file_path.suffix.lower()
    file_type = ext[1:] if ext else "unknown"
    
    return {
        "path": str(relative_path),
        "absolute_path": str(file_path),
        "filename": file_path.name,
        "brand": brand,
        "type": file_type,
        "size": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "hash": get_file_hash(file_path)
    }


def scan_directory(docs_dir: Path) -> List[Dict[str, Any]]:
    """Scanner récursivement un répertoire"""
    files = []
    
    if not docs_dir.exists():
        print(f"Erreur: Le dossier {docs_dir} n'existe pas")
        return files
    
    # Extensions de fichiers à traiter
    supported_extensions = {'.pdf', '.mms', '.zip', '.docx', '.txt', '.csv', '.jpg', '.jpeg', '.png'}
    
    for root, dirs, filenames in os.walk(docs_dir):
        # Ignorer les dossiers système
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()
            
            # Inclure tous les fichiers ou seulement ceux supportés
            if ext in supported_extensions or not supported_extensions:
                try:
                    file_info = get_file_info(file_path, docs_dir)
                    files.append(file_info)
                except Exception as e:
                    print(f"Erreur lors du traitement de {file_path}: {e}")
    
    return files


def generate_summary(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Générer un résumé des fichiers"""
    summary = {
        "total_files": len(files),
        "total_size_mb": sum(f["size_mb"] for f in files),
        "by_brand": {},
        "by_type": {},
        "by_brand_and_type": {}
    }
    
    for file_info in files:
        brand = file_info["brand"]
        file_type = file_info["type"]
        
        # Par marque
        if brand not in summary["by_brand"]:
            summary["by_brand"][brand] = {"count": 0, "size_mb": 0}
        summary["by_brand"][brand]["count"] += 1
        summary["by_brand"][brand]["size_mb"] += file_info["size_mb"]
        
        # Par type
        if file_type not in summary["by_type"]:
            summary["by_type"][file_type] = {"count": 0, "size_mb": 0}
        summary["by_type"][file_type]["count"] += 1
        summary["by_type"][file_type]["size_mb"] += file_info["size_mb"]
        
        # Par marque et type
        key = f"{brand}_{file_type}"
        if key not in summary["by_brand_and_type"]:
            summary["by_brand_and_type"][key] = {"count": 0, "size_mb": 0}
        summary["by_brand_and_type"][key]["count"] += 1
        summary["by_brand_and_type"][key]["size_mb"] += file_info["size_mb"]
    
    # Arrondir les tailles
    for brand in summary["by_brand"]:
        summary["by_brand"][brand]["size_mb"] = round(summary["by_brand"][brand]["size_mb"], 2)
    for file_type in summary["by_type"]:
        summary["by_type"][file_type]["size_mb"] = round(summary["by_type"][file_type]["size_mb"], 2)
    for key in summary["by_brand_and_type"]:
        summary["by_brand_and_type"][key]["size_mb"] = round(summary["by_brand_and_type"][key]["size_mb"], 2)
    
    return summary


def save_json(data: Dict[str, Any], output_path: Path):
    """Sauvegarder en JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(files: List[Dict[str, Any]], output_path: Path):
    """Sauvegarder en CSV"""
    if not files:
        return
    
    fieldnames = files[0].keys()
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(files)


def main():
    """Fonction principale"""
    # Chemins
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    output_dir = project_root / "scripts" / "inventory_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Scan du dossier: {docs_dir}")
    print("⏳ Analyse en cours...")
    
    # Scanner les fichiers
    files = scan_directory(docs_dir)
    
    if not files:
        print("❌ Aucun fichier trouvé")
        return
    
    # Générer le résumé
    summary = generate_summary(files)
    
    # Données complètes
    inventory = {
        "generated_at": datetime.now().isoformat(),
        "docs_directory": str(docs_dir),
        "summary": summary,
        "files": files
    }
    
    # Sauvegarder
    json_path = output_dir / "inventory.json"
    csv_path = output_dir / "inventory.csv"
    summary_path = output_dir / "summary.json"
    
    save_json(inventory, json_path)
    save_csv(files, csv_path)
    save_json(summary, summary_path)
    
    # Afficher le résumé
    print(f"\n✅ Inventaire terminé: {len(files)} fichiers trouvés")
    print(f"\n📊 Résumé par marque:")
    for brand, info in sorted(summary["by_brand"].items()):
        print(f"  - {brand}: {info['count']} fichiers ({info['size_mb']} MB)")
    
    print(f"\n📊 Résumé par type:")
    for file_type, info in sorted(summary["by_type"].items()):
        print(f"  - .{file_type}: {info['count']} fichiers ({info['size_mb']} MB)")
    
    print(f"\n💾 Fichiers générés:")
    print(f"  - {json_path}")
    print(f"  - {csv_path}")
    print(f"  - {summary_path}")


if __name__ == "__main__":
    main()
