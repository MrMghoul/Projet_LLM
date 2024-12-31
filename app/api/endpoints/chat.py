from fastapi import APIRouter, HTTPException
from models.chat import ChatRequestTP1, ChatRequestTP2, ChatRequestWithContext, ChatResponse
from services.llm_service import LLMService
from typing import Dict, List
import logging
from fastapi.responses import JSONResponse

router = APIRouter()
llm_service = LLMService()

@router.post("/chat/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequestTP1) -> ChatResponse:
    """Endpoint simple du TP1"""
    try:
        response = await llm_service.generate_response(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/with-context", response_model=ChatResponse)
async def chat_with_context(request: ChatRequestWithContext) -> ChatResponse:
    """Endpoint avec contexte du TP1"""
    try:
        response = await llm_service.generate_response(
            message=request.message,
            context=request.context
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequestTP2) -> ChatResponse:
    """Nouvel endpoint du TP2 avec gestion de session"""
    try:
        response = await llm_service.generate_response(
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(session_id: str) -> JSONResponse:
    """Récupération de l'historique d'une conversation"""
    try:
        logging.info(f"Récupération de l'historique pour session_id: {session_id}")
        history = await llm_service.get_conversation_history(session_id)
        logging.info(f"Historique récupéré: {history}")
        return JSONResponse(content=history)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_all_sessions() -> JSONResponse:
    """Récupération de toutes les sessions"""
    try:
        sessions = await llm_service.get_all_sessions()
        return JSONResponse(content=sessions)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> JSONResponse:
    """Supprime une session"""
    try:
        result = await llm_service.delete_conversation(session_id)
        if result:
            return JSONResponse(content={"message": "Session deleted"})
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression de la session: {e}")
        raise HTTPException(status_code=500, detail=str(e))