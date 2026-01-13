from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TipBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []


class TipCreate(TipBase):
    pass


class TipUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class Tip(TipBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
