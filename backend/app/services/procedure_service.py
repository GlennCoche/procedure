"""
Service pour la gestion des procédures
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.procedure import Procedure, Step


class ProcedureService:
    @staticmethod
    def get_procedures(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_active: bool = True
    ) -> List[Procedure]:
        """Obtenir la liste des procédures"""
        query = db.query(Procedure)
        
        if is_active:
            query = query.filter(Procedure.is_active == 1)
        
        if category:
            query = query.filter(Procedure.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_procedure_by_id(db: Session, procedure_id: int) -> Optional[Procedure]:
        """Obtenir une procédure par ID"""
        return db.query(Procedure).filter(Procedure.id == procedure_id).first()
    
    @staticmethod
    def create_procedure(
        db: Session,
        title: str,
        description: Optional[str],
        category: Optional[str],
        tags: List[str],
        created_by: int,
        flowchart_data: Optional[dict] = None
    ) -> Procedure:
        """Créer une nouvelle procédure"""
        procedure = Procedure(
            title=title,
            description=description,
            category=category,
            tags=tags,
            created_by=created_by,
            flowchart_data=flowchart_data
        )
        db.add(procedure)
        db.commit()
        db.refresh(procedure)
        return procedure
