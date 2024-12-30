from fastapi import APIRouter, HTTPException
from models.chat import ChatRequestTP1, ChatResponse
from services.llm_service import LLMService
from typing import Dict, List

router = APIRouter()
llm_service = LLMService()

@router.post("/assistant/tool", response_model=ChatResponse)
async def use_tool(request: ChatRequestTP1):
    try:
        response = await llm_service.process_with_tools(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))