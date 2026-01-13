from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.execution import Execution, StepExecution
from app.models.procedure import Procedure, Step
from app.schemas.execution import Execution as ExecutionSchema, ExecutionCreate, StepExecution as StepExecutionSchema, StepExecutionCreate

router = APIRouter()


@router.post("/", response_model=ExecutionSchema, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_data: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle exécution de procédure"""
    # Vérifier que la procédure existe
    procedure = db.query(Procedure).filter(Procedure.id == execution_data.procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    
    db_execution = Execution(
        user_id=current_user.id,
        procedure_id=execution_data.procedure_id,
        status=execution_data.status,
        current_step=execution_data.current_step or 0
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.get("/{execution_id}", response_model=ExecutionSchema)
async def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir une exécution par ID"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return execution


@router.put("/{execution_id}/step", response_model=StepExecutionSchema)
async def update_step_execution(
    execution_id: int,
    step_data: StepExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour l'exécution d'une étape"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Vérifier que l'étape existe
    step = db.query(Step).filter(Step.id == step_data.step_id).first()
    if not step or step.procedure_id != execution.procedure_id:
        raise HTTPException(status_code=400, detail="Invalid step")
    
    # Chercher ou créer la step_execution
    step_execution = db.query(StepExecution).filter(
        StepExecution.execution_id == execution_id,
        StepExecution.step_id == step_data.step_id
    ).first()
    
    import json
    from datetime import datetime
    
    if step_execution:
        step_execution.status = step_data.status
        step_execution.photos = json.dumps(step_data.photos) if step_data.photos else "[]"
        step_execution.comments = step_data.comments
        if step_data.status == "completed":
            step_execution.completed_at = datetime.utcnow()
    else:
        step_execution = StepExecution(
            execution_id=execution_id,
            step_id=step_data.step_id,
            status=step_data.status,
            photos=json.dumps(step_data.photos) if step_data.photos else "[]",
            comments=step_data.comments,
            completed_at=datetime.utcnow() if step_data.status == "completed" else None
        )
        db.add(step_execution)
    
    # Mettre à jour l'exécution
    if step_data.status == "completed":
        execution.current_step = step.order + 1
    
    db.commit()
    db.refresh(step_execution)
    return step_execution


@router.put("/{execution_id}/complete", response_model=ExecutionSchema)
async def complete_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer une exécution comme terminée"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    from datetime import datetime
    from app.models.execution import ExecutionStatus
    execution.status = ExecutionStatus.COMPLETED.value
    execution.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(execution)
    return execution
