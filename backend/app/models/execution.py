from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ExecutionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    status = Column(String, default=ExecutionStatus.IN_PROGRESS.value, nullable=False)
    current_step = Column(Integer, default=0)  # Index de l'étape actuelle
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    procedure = relationship("Procedure", back_populates="executions")
    step_executions = relationship("StepExecution", back_populates="execution")


class StepExecution(Base):
    __tablename__ = "step_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("steps.id"), nullable=False)
    status = Column(String, default="pending")  # pending, completed, skipped
    photos = Column(String, default="[]")  # JSON string de photos
    comments = Column(String)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    execution = relationship("Execution", back_populates="step_executions")
    step = relationship("Step", back_populates="step_executions")
