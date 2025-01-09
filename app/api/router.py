from fastapi import APIRouter
from api.endpoints import chat
from api.endpoints import summarize
from api.endpoints import memory
from api.endpoints import tools
from api.endpoints import chat, summarize, memory, tools, patient


router = APIRouter()

router.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["chat"]
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

router.include_router(
    patient.router,
    prefix="/patient",
    tags=["patient"]
)