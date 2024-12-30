# services/llm_service.py
"""
Service principal gérant les interactions avec le modèle de langage
Compatible avec les fonctionnalités du TP1 et du TP2
"""
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from services.tools import AssistantTools
from services.memory import EnhancedMemoryHistory
from services.chain import SummaryService
import os
from typing import List, Dict, Optional, Any


class LLMService:
    """
    Service LLM unifié supportant à la fois les fonctionnalités du TP1 et du TP2
    """
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY n'est pas définie")
        
        # Configuration commune
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            api_key=api_key
        )
        
        # Configuration pour le TP2
        self.conversation_store = {}
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Vous êtes un assistant utile et concis."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
        
        self.chain = self.prompt | self.llm
        
        # Configuration du gestionnaire d'historique
        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

        self.summary_service = SummaryService(self.llm)
        self.tools = AssistantTools(self.llm)
        #self.session_manager = SessionManager()
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Récupère ou crée l'historique pour une session donnée"""
        if session_id not in self.conversation_store:
            self.conversation_store[session_id] = EnhancedMemoryHistory()
        return self.conversation_store[session_id]
    
    def cleanup_inactive_sessions(self):
        """Nettoie les sessions inactives"""
        current_time = datetime.now()
        for session_id, history in list(self.conversation_store.items()):
            if not history.is_active():
                del self.conversation_store[session_id]

    async def process_with_tools(self, query: str) -> str:
        return await self.tools.process_request(query)

    async def generate_response(self, 
                              message: str, 
                              context: Optional[List[Dict[str, str]]] = None,
                              session_id: Optional[str] = None) -> str:
        """
        Méthode unifiée pour générer des réponses
        Supporte les deux modes : avec contexte (TP1) et avec historique (TP2)
        """
        if session_id:
            # Mode TP2 avec historique
            response = await self.chain_with_history.ainvoke(
                {"question": message},
                config={"configurable": {"session_id": session_id}}
            )
            return response.content
        else:
            # Mode TP1 avec contexte explicite
            messages = [SystemMessage(content="Vous êtes un assistant utile et concis.")]
            
            if context:
                for msg in context:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            messages.append(HumanMessage(content=message))
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Récupère l'historique d'une conversation spécifique"""
        if session_id in self.conversation_store:
            history = self.conversation_store[session_id].messages
            return [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                }
                for msg in history
            ]
        return []


    async def generate_summary(self, message: str) -> Dict[str, Any]:
        return await self.summary_service.generate_summary(message)