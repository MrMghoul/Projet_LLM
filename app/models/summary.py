# models/chat.py
"""
Modèles Pydantic pour la validation des données
Inclut les modèles du TP1 et les nouveaux modèles pour le TP2
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

# ---- Modèles du TP1 ----
class SummaryRequestTP1(BaseModel):
    """Requête de base pour une conversation sans contexte"""
    message: str

class SummaryResponse(BaseModel):
    """Réponse standard du chatbot"""
    response: str

class SummaryRequestWithContext(BaseModel):
    """Requête avec contexte de conversation du TP1"""
    message: str
    context: Optional[List[Dict[str, str]]] = []

# ---- Nouveaux modèles pour le TP2 ----

class SummaryRequestTP2(BaseModel):
    """Requête de base pour une conversation sans contexte"""
    message: str
    session_id: str  # Ajouté pour supporter les deux versions

class SummuryMessage(BaseModel):
    """Structure d'un message individuel dans l'historique"""
    role: str  # "user" ou "assistant"
    content: str
    size: Optional[int] = 100 

class SummuryHistory(BaseModel):
    """Collection de messages formant une conversation"""
    messages: List[ChatMessage]