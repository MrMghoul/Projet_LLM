from fastapi import APIRouter, HTTPException
from models.chat import ChatRequestTP1, ChatRequestTP2, ChatRequestWithContext, ChatResponse
from models.summary import SummaryRequestTP1, SummaryResponse, SummaryRequestWithContext
from services.llm_service import LLMService
from typing import Dict, List

router = APIRouter()
llm_service = LLMService()

@router.post("/summarize/simple", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequestTP1):
    try:
        summary = await llm_service.generate_summary(request.message)
        return SummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/summarize/context", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequestWithContext):
    try:
        summary = await llm_service.generate_summary(request.message)
        return SummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))