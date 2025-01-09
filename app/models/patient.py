from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class Patient(BaseModel):
    id: str = Field(..., alias="_id")
    nom: str
    prenom: str
    date_naissance: date
    lieu_residence: str
    ville: str
    pays: str
    code_postal: str
    sexe: str
    telephone: str
    contact_urgence: str
    poids: int
    taille: int
    groupe_sanguin: str
    conditions_chroniques: List[str] = []
    allergies: List[str] = []
    antecedents: List[str] = []