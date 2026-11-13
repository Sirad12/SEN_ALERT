# app/schemas.py
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Statut = Literal["Signalé", "Vérifié", "En traitement", "Résolu", "Rejeté"]
TypeProbleme = Literal["Rue bouchée", "Canal bouché", "Caniveau bouché"]


class EtapeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    statut: Statut
    date: str
    note: str = ""


class SignalementCreate(BaseModel):
    type: TypeProbleme
    description: str = Field(..., min_length=10)
    x: int = Field(..., ge=0, le=600)
    y: int = Field(..., ge=0, le=380)
    photo: str = Field(..., min_length=1)


class SignalementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    type: str
    description: str
    x: int
    y: int
    statut: Statut
    photo: Optional[str] = None
    apres: Optional[str] = None
    historique: list[EtapeOut]


class ChangementStatut(BaseModel):
    statut: Statut
    note: str = ""
    apres: Optional[str] = None


class Connexion(BaseModel):
    username: str
    password: str


class Jeton(BaseModel):
    token: str
