from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.procedure import Procedure, Step
from app.schemas.procedure import Procedure as ProcedureSchema, ProcedureCreate, ProcedureUpdate, Step as StepSchema, StepCreate

router = APIRouter()


@router.get("/", response_model=List[ProcedureSchema])
async def get_procedures(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir la liste des procédures"""
    query = db.query(Procedure).filter(Procedure.is_active == 1)
    
    if category:
        query = query.filter(Procedure.category == category)
    
    procedures = query.offset(skip).limit(limit).all()
    return procedures


@router.get("/{procedure_id}", response_model=ProcedureSchema)
async def get_procedure(
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir une procédure par ID"""
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure


@router.post("/", response_model=ProcedureSchema, status_code=status.HTTP_201_CREATED)
async def create_procedure(
    procedure_data: ProcedureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Créer une nouvelle procédure (Admin uniquement)"""
    db_procedure = Procedure(
        title=procedure_data.title,
        description=procedure_data.description,
        category=procedure_data.category,
        tags=procedure_data.tags or [],
        created_by=current_user.id,
        flowchart_data=procedure_data.flowchart_data
    )
    db.add(db_procedure)
    db.flush()
    
    # Créer les étapes
    if procedure_data.steps:
        for step_data in sorted(procedure_data.steps, key=lambda x: x.order):
            db_step = Step(
                procedure_id=db_procedure.id,
                title=step_data.title,
                description=step_data.description,
                instructions=step_data.instructions,
                order=step_data.order,
                validation_type=step_data.validation_type or "manual",
                photos=step_data.photos or [],
                files=step_data.files or []
            )
            db.add(db_step)
    
    db.commit()
    db.refresh(db_procedure)
    # Recharger avec les étapes
    db_procedure = db.query(Procedure).filter(Procedure.id == db_procedure.id).first()
    return db_procedure


@router.put("/{procedure_id}", response_model=ProcedureSchema)
async def update_procedure(
    procedure_id: int,
    procedure_data: ProcedureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Mettre à jour une procédure (Admin uniquement)"""
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    update_data = procedure_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(procedure, field, value)
    
    db.commit()
    db.refresh(procedure)
    return procedure


@router.delete("/{procedure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_procedure(
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprimer une procédure (Admin uniquement)"""
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    procedure.is_active = 0
    db.commit()
    return None
