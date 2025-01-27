import re
import spacy
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from models.patient import Patient
from services.mongo_service import MongoService
from services.llm_service import LLMService
from fastapi.responses import JSONResponse
import re
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

router = APIRouter()
mongo_service = MongoService()
llm_service = LLMService()

nlp = spacy.load("fr_core_news_md")

@router.get("/patients", response_model=List[Patient])
async def get_patients() -> List[Patient]:
    """Récupère la liste de tous les patients"""
    try:
        patients = await mongo_service.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str) -> Patient:
    """Récupère les informations d'un patient par son ID"""
    try:
        patient = await mongo_service.get_patient_by_id(patient_id)
        if patient:
            return patient
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients/name/{nom}/{prenom}", response_model=Patient)
async def get_patient_by_name(nom: str, prenom: str) -> Patient:
    """Récupère les informations d'un patient par son nom et prénom"""
    try:
        patient = await mongo_service.get_patient_by_name(nom, prenom)
        if patient:
            return patient
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_name_and_surname(question: str) -> (str, str):
    """Extrait le nom et le prénom de la question en utilisant spaCy"""
    doc = nlp(question)
    print(f"Entités détectées : {[ent.text for ent in doc.ents]}")
    names = [ent.text for ent in doc.ents if ent.label_ == "PER"]
    if len(names) == 1:
        # Si une seule entité est détectée, essayer de la diviser en prénom et nom
        parts = names[0].split()
        if len(parts) == 2:
            return parts[0].capitalize(), parts[1].capitalize()
    elif len(names) >= 2:
        return names[0].capitalize(), names[1].capitalize()
    return None, None

@router.post("/patients/query", response_model=Dict[str, str])
async def query_patient_info(request: QueryRequest) -> Dict[str, str]:
    """Interroge les informations d'un patient par une question et génère une réponse"""
    try:
        nom, prenom = extract_name_and_surname(request.question)
        print(f"Nom extrait: {nom}, Prénom extrait: {prenom}")  # Ajout de console.log

        if not nom or not prenom:
            raise HTTPException(status_code=400, detail="Nom et prénom non trouvés dans la question")
        
        # Essayer de trouver le patient avec le nom et prénom extraits
        patient = await mongo_service.get_patient_by_name(nom, prenom)

        # Essayer de trouver la conversation avec le session_id
        history = await mongo_service.get_conversation_history(request.session_id)
        
        # Si le patient n'est pas trouvé, inverser le nom et le prénom et refaire la recherche
        if not patient:
            print(f"Patient non trouvé avec {nom} {prenom}, tentative avec {prenom} {nom}")  # Ajout de console.log
            patient = await mongo_service.get_patient_by_name(prenom, nom)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        preprocessed_question = llm_service.preprocess_message(request.question)
        #print("\n history : \n")
        #print(history)
        #preprocesses_history = [llm_service.preprocess_message(messages) for messages in history]
        #preprocesses_history = [llm_service.preprocess_message(messages["content"]) for messages in history]
        preprocesses_history = [llm_service.preprocess_message(messages["content"]) for messages in history[-10:]]
        #print("\n preprocesses_history : \n")
        #print(preprocesses_history)
        #response = await llm_service.generate_patient_response(patient, preprocessed_question, request.session_id)
        response = await llm_service.generate_patient_response(patient, preprocessed_question, request.session_id, preprocesses_history)
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))