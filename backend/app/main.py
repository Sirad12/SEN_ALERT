# app/main.py
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas, seed
from .database import Base, SessionLocal, engine

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "demo123")
# Jeton de session administrateur, régénéré à chaque démarrage
ADMIN_TOKEN = secrets.token_urlsafe(32)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed.charger(db)
    yield


app = FastAPI(title="SenAlert API", lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def exiger_admin(authorization: str = Header(default="")):
    if not secrets.compare_digest(authorization, f"Bearer {ADMIN_TOKEN}"):
        raise HTTPException(status_code=401, detail="Connexion administrateur requise.")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/signalements", response_model=list[schemas.SignalementOut])
def lire_signalements(db: Session = Depends(get_db)):
    return crud.get_signalements(db)


@app.get("/api/signalements/{signalement_id}", response_model=schemas.SignalementOut)
def lire_signalement(signalement_id: str, db: Session = Depends(get_db)):
    s = crud.get_signalement(db, signalement_id.upper())
    if s is None:
        raise HTTPException(status_code=404, detail="Aucun signalement avec ce code.")
    return s


@app.post("/api/signalements", response_model=schemas.SignalementOut, status_code=201)
def creer_signalement(data: schemas.SignalementCreate, db: Session = Depends(get_db)):
    return crud.create_signalement(db, data)


@app.post("/api/admin/login", response_model=schemas.Jeton)
def connexion(data: schemas.Connexion):
    ok_user = secrets.compare_digest(data.username, ADMIN_USER)
    ok_pass = secrets.compare_digest(data.password, ADMIN_PASSWORD)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=401, detail="Identifiants incorrects.")
    return {"token": ADMIN_TOKEN}


@app.patch(
    "/api/signalements/{signalement_id}/statut",
    response_model=schemas.SignalementOut,
    dependencies=[Depends(exiger_admin)],
)
def changer_statut(signalement_id: str, data: schemas.ChangementStatut, db: Session = Depends(get_db)):
    s = crud.get_signalement(db, signalement_id.upper())
    if s is None:
        raise HTTPException(status_code=404, detail="Aucun signalement avec ce code.")
    try:
        return crud.changer_statut(db, s, data)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
