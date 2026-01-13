"""
Utilitaires pour la gestion des uploads de fichiers
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings


async def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Sauvegarder un fichier uploadé
    Retourne le chemin relatif du fichier
    """
    # Vérifier l'extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension de fichier non autorisée. Autorisées: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Créer le répertoire si nécessaire
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer un nom de fichier unique
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}{file_ext}"
    
    # Lire et sauvegarder le fichier
    content = await file.read()
    
    # Vérifier la taille
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Maximum: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Retourner le chemin relatif
    return str(file_path.relative_to(settings.UPLOAD_DIR))


def delete_upload_file(file_path: str) -> bool:
    """
    Supprimer un fichier uploadé
    """
    try:
        full_path = Path(settings.UPLOAD_DIR) / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception:
        return False
