from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.tip import Tip
from app.schemas.tip import Tip as TipSchema, TipCreate, TipUpdate

router = APIRouter()


@router.get("/", response_model=List[TipSchema])
async def get_tips(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir la liste des tips"""
    query = db.query(Tip)
    
    if category:
        query = query.filter(Tip.category == category)
    
    if search:
        query = query.filter(
            (Tip.title.contains(search)) | (Tip.content.contains(search))
        )
    
    tips = query.offset(skip).limit(limit).all()
    return tips


@router.get("/{tip_id}", response_model=TipSchema)
async def get_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir un tip par ID"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    return tip


@router.post("/", response_model=TipSchema, status_code=status.HTTP_201_CREATED)
async def create_tip(
    tip_data: TipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Créer un nouveau tip (Admin uniquement)"""
    db_tip = Tip(
        title=tip_data.title,
        content=tip_data.content,
        category=tip_data.category,
        tags=tip_data.tags or [],
        created_by=current_user.id
    )
    db.add(db_tip)
    db.commit()
    db.refresh(db_tip)
    return db_tip


@router.put("/{tip_id}", response_model=TipSchema)
async def update_tip(
    tip_id: int,
    tip_data: TipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Mettre à jour un tip (Admin uniquement)"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    update_data = tip_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tip, field, value)
    
    db.commit()
    db.refresh(tip)
    return tip


@router.delete("/{tip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprimer un tip (Admin uniquement)"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    db.delete(tip)
    db.commit()
    return None
