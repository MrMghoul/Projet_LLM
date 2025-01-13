from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Any, List, Dict, Optional
from models.conversation import Conversation, Message
from core.config import settings
import logging
from bson import ObjectId

class MongoService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.database_name]
        self.conversations = self.db[settings.collection_name]

    async def save_message(self, session_id: str, role: str, content: str) -> bool:
        """Sauvegarde un nouveau message dans une conversation"""
        message = Message(role=role, content=content)
        result = await self.conversations.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Récupère l'historique d'une conversation"""
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
    
    async def get_patient_by_name(self, first_name: str, last_name: str) -> Optional[Dict]:
        """Récupère un patient par son prénom et nom"""
        patient = await self.db["patient"].find_one({"prenom": first_name, "nom": last_name})
        if patient:
            patient["_id"] = str(patient["_id"])
        return patient
    