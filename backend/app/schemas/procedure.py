from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class StepBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    order: int
    validation_type: Optional[str] = "manual"
    photos: Optional[List[str]] = []
    files: Optional[List[str]] = []


class StepCreate(StepBase):
    pass


class StepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    order: Optional[int] = None
    validation_type: Optional[str] = None
    photos: Optional[List[str]] = None
    files: Optional[List[str]] = None


class Step(StepBase):
    id: int
    procedure_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProcedureBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    flowchart_data: Optional[Dict[str, Any]] = None


class ProcedureCreate(ProcedureBase):
    steps: Optional[List[StepCreate]] = []


class ProcedureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    flowchart_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class Procedure(ProcedureBase):
    id: int
    created_by: int
    version: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    steps: List[Step] = []

    class Config:
        from_attributes = True
