from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.execution import ExecutionStatus


class StepExecutionBase(BaseModel):
    step_id: int
    status: Optional[str] = "pending"
    photos: Optional[List[str]] = []
    comments: Optional[str] = None


class StepExecutionCreate(StepExecutionBase):
    pass


class StepExecution(StepExecutionBase):
    id: int
    execution_id: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExecutionBase(BaseModel):
    procedure_id: int
    status: Optional[str] = ExecutionStatus.IN_PROGRESS.value
    current_step: Optional[int] = 0


class ExecutionCreate(ExecutionBase):
    pass


class Execution(ExecutionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    step_executions: List[StepExecution] = []

    class Config:
        from_attributes = True
