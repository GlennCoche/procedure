from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    success = "success"
    error = "error"
    paused = "paused"
    running = "running"
    skipped = "skipped"


class StepProgress(BaseModel):
    current: int = 0
    total: int = 0


class ResourceUsage(BaseModel):
    cpu_percent: float = 0.0
    ram_mb: float = 0.0


class StepResult(BaseModel):
    step: str
    status: StepStatus
    message: str
    file: Optional[str] = None
    progress: StepProgress = Field(default_factory=StepProgress)
    resources: ResourceUsage = Field(default_factory=ResourceUsage)
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StepContext(BaseModel):
    source_dir: str
    staging_dir: str
    current_file: Optional[str] = None
    storage_url: Optional[str] = None
    extraction_output: Optional[Dict[str, Any]] = None
    supabase_inserted: Optional[Dict[str, Any]] = None
    run_id: Optional[int] = None


class ProcedureStep(BaseModel):
    order: int
    action: str
    description: str
    tools_required: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_page: int


class Procedure(BaseModel):
    title: str
    description: str
    category: str
    tags: List[str] = Field(default_factory=list)
    steps: List[ProcedureStep] = Field(default_factory=list)


class Tip(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    source_page: int


class Setting(BaseModel):
    brand: str
    equipment_type: str
    model: Optional[str] = None
    category: str
    name: str
    value: str
    unit: Optional[str] = None
    country: str = "FR"
    notes: Optional[str] = None
    source_page: Optional[int] = None


class ExtractionOutput(BaseModel):
    procedures: List[Procedure] = Field(default_factory=list)
    tips: List[Tip] = Field(default_factory=list)
    settings: List[Setting] = Field(default_factory=list)
