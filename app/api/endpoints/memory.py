from langchain.schema import HumanMessage
from fastapi import APIRouter, HTTPException
from services.llm_service import LLMService
from models.chat import ChatRequestTP1
from typing import Dict, List
import uuid

router = APIRouter()
llm_service = LLMService()

@router.post("/session/create", response_model=Dict[str, str])
async def create_session():
    session_id = str(uuid.uuid4())
    llm_service._get_session_history(session_id)
    return {"session_id": session_id}

@router.post("/session/{session_id}/add_message", response_model=Dict[str, str])
async def add_message_to_session(session_id: str, message: ChatRequestTP1):
    try:
        history = llm_service._get_session_history(session_id)
        history.add_messages([HumanMessage(content=message.message)])
        return {"status": "message added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/history", response_model=List[Dict[str, str]])
async def get_session_history(session_id: str):
    try:
        history = llm_service.get_conversation_history(session_id)
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