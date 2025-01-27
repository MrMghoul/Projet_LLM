import logging
from datetime import datetime
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.conversation import Conversation, Message
from core.config import settings

class MongoService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.database_name]
        self.conversations = self.db[settings.collection_name]

    async def save_message(self, session_id: str, role: str, content: str) -> bool:
        """Sauvegarde un nouveau message dans une conversation"""
        message = Message(role=role, content=content)
        logging.info(f"Tentative de sauvegarde du message pour la session {session_id}: {message}")
        result = await self.conversations.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        success = result.modified_count > 0 or result.upserted_id is not None
        if success:
            logging.info(f"Message sauvegardé pour la session {session_id}: {message}")
        else:
            logging.error(f"Échec de la sauvegarde du message pour la session {session_id}: {message}")
        return success

    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
        logging.info(f"Tentative de récupération de l'historique pour la session {session_id}")
        conversation = await self.conversations.find_one({"session_id": session_id})
        if conversation:
            logging.info(f"Conversation trouvée: {conversation}")
            messages = conversation.get("messages", [])
            # Convertir les messages en dictionnaires et gérer les champs JSON
            messages = [
                {
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None,
                }
                for msg in messages
            ]
            return messages

        logging.info(f"Aucune conversation trouvée pour session_id: {session_id}")
        return []

    async def delete_conversation(self, session_id: str) -> bool:
        """Supprime une conversation"""
        result = await self.conversations.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    async def get_all_sessions(self) -> List[str]:
        """Récupère tous les IDs de session"""
        cursor = self.conversations.find({}, {"session_id": 1})
        sessions = await cursor.to_list(length=None)
        return [session["session_id"] for session in sessions]

    async def get_all_patients(self) -> List[Dict]:
        """Récupère tous les patients"""
        cursor = self.db["patient"].find({})
        patients = await cursor.to_list(length=None)
        for patient in patients:
            patient["_id"] = str(patient["_id"])
        return patients

    async def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Récupère un patient par son ID"""
        patient = await self.db["patient"].find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
        return patient

    async def get_patient_by_name(self, nom: str, prenom: str) -> Optional[Dict]:
        """Récupère un patient par son nom et prénom"""
        patient = await self.db["patient"].find_one({"nom": nom, "prenom": prenom}, {"code_postal": 0, "telephone": 0, "groupe_sanguin": 0, "pays": 0})
        if patient:
            patient["_id"] = str(patient["_id"])
        return patient
    
    async def create_session(self, session_id: str) -> bool:
        """Crée une nouvelle session"""
        conversation = Conversation(session_id=session_id)
        result = await self.conversations.insert_one(conversation.model_dump())
        return result.inserted_id is not None