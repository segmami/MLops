# CONTENU de api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from src import config
from src.predict import predict_one
from src.logger import log_prediction
from src.confirm import confirm_diagnostic

app = FastAPI(title="API Classification Patients")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

engine = create_engine(config.DATABASE_URL)

# --- Schemas ---
class Patient(BaseModel):
    age: float
    salaire: float
    conso_produit_x: float
    conso_produit_y: float
    niveau_vie: str

class Confirmation(BaseModel):
    prediction_id: int          # l'ID de la prediction a confirmer
    malade: int                 # le vrai diagnostic (0 ou 1)

@app.get("/health")
def health():
    return {"status": "ok"}

# --- INFIRMIERE : predire + renvoyer l'ID ---
@app.post("/predict")
def predict(patient: Patient):
    d = patient.model_dump()
    r = predict_one(d)
    prediction_id = log_prediction(d, r)   # recupere l'ID
    r["prediction_id"] = prediction_id      # l'ajoute a la reponse
    return r

# --- MEDECIN : recuperer une prediction par ID (auto-remplissage) ---
@app.get("/patient/{pred_id}")
def get_patient(pred_id: int):
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT * FROM predictions WHERE id = :id"), {"id": pred_id}).fetchone()
    if row is None:
        return {"trouve": False}
    return {"trouve": True, **dict(row._mapping)}

# --- MEDECIN : confirmer le vrai diagnostic (relie par ID) ---
@app.post("/confirmer")
def confirmer(c: Confirmation):
    d = c.model_dump()
    confirm_diagnostic(d)
    return {"status": "diagnostic enregistre", "prediction_id": d["prediction_id"]}

# --- MONITORING : comparer predit vs reel ---
@app.get("/monitoring")
def monitoring():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT p.id, p.age, p.salaire, p.niveau_vie,
                   p.classe AS predit, p.proba_malade, d.malade AS reel
            FROM predictions p
            JOIN diagnostics_confirmes d ON d.prediction_id = p.id
            ORDER BY p.id DESC
        """)).fetchall()
    total = len(rows)
    corrects = sum(1 for r in rows if r.predit == r.reel)
    return {
        "cas_evalues": total,
        "corrects": corrects,
        "precision_reelle": round(corrects/total, 3) if total else None,
        "details": [dict(r._mapping) for r in rows],
    }