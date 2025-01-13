import re
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from models.chat import ChatRequestTP1, ChatResponse
from services import llm_service
from models.patient import Patient
from services.mongo_service import MongoService
from fastapi.responses import JSONResponse

router = APIRouter()
mongo_service = MongoService()
llm_service = llm_service.LLMService()

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
    

@router.post("/patients/summarize", response_model=ChatResponse)
async def summarize_patient_info(request: ChatRequestTP1) -> ChatResponse:
    """Récupère les informations d'un patient mentionné dans le prompt et génère un résumé"""
    try:
        # Extraire le nom du patient mentionné dans le prompt
        first_name, last_name = extract_name(request.message)
        if not first_name or not last_name:
            raise HTTPException(status_code=400, detail="Patient name not found in the prompt")

        # Rechercher les informations du patient dans la base de données
        patient = await mongo_service.get_patient_by_name(first_name, last_name)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Générer un résumé des informations du patient
        patient_info = f"Nom: {patient['nom']}\nPrénom: {patient['prenom']}\nAntécédents médicaux: {', '.join(patient['antecedents'])}"
        prompt = f"{request.message}\n\nInformations du patient:\n{patient_info}"
        summary = await llm_service.generate_summary(prompt)

        return ChatResponse(response=summary["full_summary"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/patients/extract-name", response_model=Dict[str, str])
async def extract_name_endpoint(request: ChatRequestTP1) -> Dict[str, str]:
    """Extrait le nom et prénom d'un prompt utilisateur"""
    first_name, last_name = extract_name(request.message)
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="Patient name not found in the prompt")
    return {"first_name": first_name, "last_name": last_name}
    

 
def extract_name(prompt):
    """
    Extrait le nom et prénom d'un prompt utilisateur.
    
    :param prompt: Texte saisi par l'utilisateur
    :return: Tuple contenant (prénom, nom) ou (None, None) si non trouvé
    """
    # Exemple de pattern pour un format "Prénom Nom"
    match = re.search(r"\b([A-Z][a-z]+)\s([A-Z][a-z]+)\b", prompt)
    if match:
        first_name, last_name = match.groups()
        return first_name, last_name
    return None, None
