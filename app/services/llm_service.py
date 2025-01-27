# services/llm_service.py
"""
Service principal gérant les interactions avec le modèle de langage
Compatible avec les fonctionnalités du TP1 et du TP2
"""
from datetime import datetime
import logging
from optparse import Option
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from services.tools import AssistantTools
from services.memory import EnhancedMemoryHistory
from services.chain import SummaryService
from services.mongo_service import MongoService
import os
import spacy
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
        
        self.nlp = spacy.load("fr_core_news_md")

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
        self.mongo_service = MongoService()
    
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
        
        if session_id:
            # Mode TP2 avec historique, récupération depuis MongoDB
            try:
                history = await self.mongo_service.get_conversation_history(session_id)
                messages = [SystemMessage(content="Vous êtes un assistant utile et concis.")]
                
                # Conversion de l'historique en messages LangChain
                for msg in history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
                
                # Ajout du nouveau message
                messages.append(HumanMessage(content=message))
                
                # Génération de la réponse
                response = await self.llm.agenerate([messages])
                response_text = response.generations[0][0].text

                # Sauvegarde des messages dans MongoDB
                await self.mongo_service.save_message(session_id, "user", message)
                await self.mongo_service.save_message(session_id, "assistant", response_text)
                return response_text

            except Exception as e:
                raise RuntimeError(f"Erreur lors de la gestion du mode historique : {e}")

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

            # Génération de la réponse sans historique MongoDB
            try:
                response = await self.llm.agenerate([messages])
                return response.generations[0][0].text
            except Exception as e:
                raise RuntimeError(f"Erreur lors de la génération de réponse : {e}")

    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
        return await self.mongo_service.get_conversation_history(session_id)
    
    async def get_all_sessions(self) -> List[str]:
        """Récupère toutes les sessions depuis MongoDB"""
        return await self.mongo_service.get_all_sessions()

    async def delete_conversation(self, session_id: str) -> bool:
        """Supprime une conversation"""
        return await self.mongo_service.delete_conversation(session_id)
    

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

    def preprocess_message(self, message: str) -> str:
        """Prétraite le message en supprimant les mots vides"""
        doc = self.nlp(message)
        tokens = [token.text for token in doc if not token.is_stop]
        return " ".join(tokens)
    
    def pseudonymize_message(self, message: str, patient: Dict[str, Any]) -> str:
        """Pseudonymise les données sensibles dans un message"""
        pseudonymized_message = message
        sensitive_data = {
            patient["date_naissance"]: "[DATE_NAISSANCE_CHIFFREE]",
            patient["lieu_residence"]: "[LIEU_RESIDENCE_CHIFFRE]",
            patient["contact_urgence"]: "[CONTACT_URGENCE_CHIFFRE]"
        }
        
        # Remplacer les données sensibles spécifiques
        for data, pseudonym in sensitive_data.items():
            pseudonymized_message = pseudonymized_message.replace(data, pseudonym)
        
        # Remplacer les dates au format jour mois année (ex: 14 mai 1990)
        date_pattern = r'\b\d{1,2} \w+ \d{4}\b'
        pseudonymized_message = re.sub(date_pattern, '[DATE_NAISSANCE_CHIFFREE]', pseudonymized_message)
        
        return pseudonymized_message

    async def generate_patient_response(self, patient: Dict[str, Any], question: str, session_id: Option, history : any) -> str:
        """Génère une réponse basée sur les informations du patient"""
        
        encrypted_data = {
            "date_naissance": patient["date_naissance"],
            "lieu_residence": patient["lieu_residence"],
            "contact_urgence": patient["contact_urgence"]
        }
        
        # Pseudonymiser ou masquer les données sensibles avant de les envoyer au LLM
        pseudonymized_patient = {
            "nom": patient["nom"],
            "prenom": patient["prenom"],
            "date_naissance": "[DATE_NAISSANCE_CHIFFREE]",
            "lieu_residence": "[LIEU_RESIDENCE_CHIFFRE]",
            "ville": patient["ville"],
            "sexe": patient["sexe"],
            "contact_urgence": "[CONTACT_URGENCE_CHIFFRE]",
            "poids": patient["poids"],
            "taille": patient["taille"],
            "conditions_chroniques": patient["conditions_chroniques"],
            "allergies": patient["allergies"],
            "antecedents": patient["antecedents"]
        }

        preprocessed_question = self.preprocess_message(question)
        logging.info(f"Question prétraitée : {preprocessed_question}")
        history_join = " ".join(history)
        preprocessed_history = self.preprocess_message(history_join)
        logging.info(f"Historique prétraitée : {preprocessed_history}")

        logging.info(f"Données patient pseudonymisées : {pseudonymized_patient}")
        messages = [
            SystemMessage(content="Vous êtes un assistant médical. Qui aides et accompagnes les pompiers en leur fournissant des informations sur les patients et les guides pour les premiers secours."),
            HumanMessage(content=f"Voici les informations du patient : {pseudonymized_patient}"),
            HumanMessage(content=f"Voici l'historique de la conversation afin d'avoir le contexte : {preprocessed_history}"),
            HumanMessage(content=question)
        ]

        logging.info(f"Messages envoyés au LLM : {messages}")
        
        try:
            response = await self.llm.agenerate([messages])
            response_text = response.generations[0][0].text

            logging.info(f"Réponse du LLM crypté : {response_text}")

            #decrypter la reponse avnt de l'envoyer sur swagger 
            decrypted_response = response_text.replace("[DATE_NAISSANCE_CHIFFREE]", encrypted_data["date_naissance"])
            decrypted_response = decrypted_response.replace("[LIEU_RESIDENCE_CHIFFRE]", encrypted_data["lieu_residence"])
            decrypted_response = decrypted_response.replace("[CONTACT_URGENCE_CHIFFRE]", encrypted_data["contact_urgence"])

            logging.info(f"Réponse du LLM décrypté : {decrypted_response}")

            if session_id:
                await self.mongo_service.save_message(session_id, "user", question)
                await self.mongo_service.save_message(session_id, "assistant", decrypted_response)


            # Décoder ou transformer la réponse si nécessaire
            return decrypted_response
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la génération de réponse : {e}")
