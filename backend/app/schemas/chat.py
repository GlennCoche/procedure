from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    response: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    response: str
    message_id: int
