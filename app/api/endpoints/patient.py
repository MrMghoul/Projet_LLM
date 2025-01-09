from fastapi import APIRouter, HTTPException
from typing import List
from models.patient import Patient
from services.mongo_service import MongoService
from fastapi.responses import JSONResponse

router = APIRouter()
mongo_service = MongoService()

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