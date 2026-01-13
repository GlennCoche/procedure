from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.vision_service import VisionService

router = APIRouter()
vision_service = VisionService()


@router.post("/recognize")
async def recognize_equipment(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reconnaître un équipement via photo"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Lire le fichier
        image_data = await file.read()
        
        # Analyser avec OpenAI Vision
        result = await vision_service.recognize_equipment(image_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
