from fastapi import APIRouter
from api.endpoints import chat
from api.endpoints import summarize
from api.endpoints import memory
from api.endpoints import tools

router = APIRouter()

router.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["chat"]
)

router.include_router(
    summarize.router, 
    prefix="/summarize", 
    tags=["summarize"]
)

router.include_router(
    memory.router, 
    prefix="/memory", 
    tags=["memory"]
)

router.include_router(
    tools.router,
    prefix="/tools",
    tags=["tools"]
)