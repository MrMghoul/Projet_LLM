from fastapi import APIRouter, HTTPException
from models.chat import ChatRequestTP1
from services.llm_service import LLMService
from typing import Dict, List
import uuid

router = APIRouter()
llm_service = LLMService()

@router.post("/session/create", response_model=Dict[str, str])
async def create_session():
    session_id = str(uuid.uuid4())
    await llm_service.mongo_service.create_session(session_id)
    return {"session_id": session_id}

@router.post("/session/{session_id}/add_message", response_model=Dict[str, str])
async def add_message_to_session(session_id: str, message: ChatRequestTP1):
    try:
        await llm_service.mongo_service.save_message(session_id, "user", message.message)
        return {"status": "message added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/history", response_model=List[Dict[str, str]])
async def get_session_history(session_id: str):
    try:
        history = await llm_service.get_conversation_history(session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/cleanup", response_model=Dict[str, str])
async def cleanup_sessions():
    try:
        llm_service.cleanup_inactive_sessions()
        return {"status": "inactive sessions cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))