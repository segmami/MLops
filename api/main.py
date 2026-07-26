# CONTENU de api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware   # autorise les pages web a appeler l'API
from pydantic import BaseModel                       # valide les donnees recues
from src.predict import predict_one
from src.logger import log_prediction                # -> table predictions
from src.confirm import confirm_diagnostic           # -> table diagnostics_confirmes

app = FastAPI(title="API Classification Patients")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# --- Schema FRONT 1 : un patient a predire (PAS de malade) ---
class Patient(BaseModel):
    age: float
    salaire: float
    conso_produit_x: float
    conso_produit_y: float
    niveau_vie: str

# --- Schema FRONT 2 : un diagnostic confirme (AVEC malade) ---
class PatientConfirme(Patient):    # herite de Patient + ajoute le vrai diagnostic
    malade: int                    # 0 = sain, 1 = malade (verite)

@app.get("/health")                # verifier que l'API tourne
def health():
    return {"status": "ok"}

# --- FRONT 1 (public) : predire ---
@app.post("/predict")
def predict(patient: Patient):
    d = patient.model_dump()       # patient -> dict
    r = predict_one(d)             # prediction (dernier .pkl)
    log_prediction(d, r)           # trace dans predictions (supposition)
    return r

# --- FRONT 2 (medecin) : confirmer le vrai diagnostic ---
@app.post("/confirmer")
def confirmer(patient: PatientConfirme):
    d = patient.model_dump()       # contient malade (la verite)
    confirm_diagnostic(d)          # ecrit dans diagnostics_confirmes
    return {"status": "diagnostic enregistre", "malade": d["malade"]}
