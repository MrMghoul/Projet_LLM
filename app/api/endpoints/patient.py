from fastapi import APIRouter, HTTPException
from typing import List, Dict
from models.patient import Patient
from services.mongo_service import MongoService
from services.llm_service import LLMService
from fastapi.responses import JSONResponse
import re

router = APIRouter()
mongo_service = MongoService()
llm_service = LLMService()

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
    """Extrait le nom et le prénom de la question"""
    # Exemple simple d'extraction de nom et prénom
    match = re.search(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b", question)
    if match:
        return match.group(1), match.group(2)
    return None, None

@router.post("/patients/query", response_model=Dict[str, str])
async def query_patient_info(question: str) -> Dict[str, str]:
    """Interroge les informations d'un patient par une question et génère une réponse"""
    try:
        nom, prenom = extract_name_and_surname(question)
        print(f"Nom extrait: {nom}, Prénom extrait: {prenom}")  # Ajout de console.log

        if not nom or not prenom:
            raise HTTPException(status_code=400, detail="Nom et prénom non trouvés dans la question")
        
        patient = await mongo_service.get_patient_by_name(nom, prenom)
        print(f"Patient trouvé: {patient}")  # Ajout de console.log

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        response = await llm_service.generate_patient_response(patient, question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))