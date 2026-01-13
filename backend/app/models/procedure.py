from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    category = Column(String, index=True)
    tags = Column(JSON, default=list)  # Liste de tags
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    flowchart_data = Column(JSON)  # Données du logigramme React Flow
    is_active = Column(Integer, default=1)  # 0 ou 1 pour SQLite
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    steps = relationship("Step", back_populates="procedure", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="procedure")


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Ordre dans la procédure
    title = Column(String, nullable=False)
    description = Column(Text)
    instructions = Column(Text)  # Instructions détaillées
    photos = Column(JSON, default=list)  # Liste d'URLs de photos
    files = Column(JSON, default=list)  # Liste d'URLs de fichiers
    validation_type = Column(String, default="manual")  # manual, photo, signature, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    procedure = relationship("Procedure", back_populates="steps")
    step_executions = relationship("StepExecution", back_populates="step")
