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
    max_length: Optional[int] = 1000

class SummaryResponse(BaseModel):
    """Réponse standard du chatbot"""
    full_summary: str
    bullet_points: List[str]
    one_liner: str

class SummaryRequestWithContext(BaseModel):
    """Requête avec contexte de conversation du TP1"""
    message: str
    max_length: Optional[int] = 1000
    context: Optional[List[Dict[str, str]]] = []

# ---- Nouveaux modèles pour le TP2 ----

class SummaryRequestTP2(BaseModel):
    """Requête de base pour une conversation sans contexte"""
    message: str
    session_id: str  # Ajouté pour supporter les deux versions

class SummaryMessage(BaseModel):
    """Structure d'un message individuel dans l'historique"""
    role: str  # "user" ou "assistant"
    content: str
    size: Optional[int] = 1000
    

class SummaryHistory(BaseModel):
    """Collection de messages formant une conversation"""
    messages: List[SummaryMessage]