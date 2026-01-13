from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage as ChatMessageModel
from app.schemas.chat import ChatMessageCreate, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/", response_model=ChatResponse)
async def chat(
    chat_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Envoyer un message au chat IA"""
    try:
        # Obtenir la réponse de l'IA
        response = await ai_service.get_chat_response(
            message=chat_data.message,
            context=chat_data.context,
            user_id=current_user.id
        )
        
        # Sauvegarder le message
        db_message = ChatMessageModel(
            user_id=current_user.id,
            message=chat_data.message,
            response=response,
            context=chat_data.context
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        return ChatResponse(response=response, message_id=db_message.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    chat_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat IA avec streaming"""
    async def generate():
        try:
            async for chunk in ai_service.get_chat_response_stream(
                message=chat_data.message,
                context=chat_data.context,
                user_id=current_user.id
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Sauvegarder le message après streaming
            full_response = await ai_service.get_chat_response(
                message=chat_data.message,
                context=chat_data.context,
                user_id=current_user.id
            )
            
            db_message = ChatMessageModel(
                user_id=current_user.id,
                message=chat_data.message,
                response=full_response,
                context=chat_data.context
            )
            db.add(db_message)
            db.commit()
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
