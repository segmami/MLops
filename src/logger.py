# CONTENU de src/logger.py

import logging
from datetime import datetime
from sqlalchemy import create_engine, text     # create_engine=connexion | text=SQL
from src import config

# --- Logs console ---
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("patients_api")

# --- Connexion (SQLite local / PostgreSQL en ligne) ---
engine = create_engine(config.DATABASE_URL)

# --- Table des SUPPOSITIONS, creee si absente ---
with engine.begin() as conn:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS predictions ("
        "id SERIAL PRIMARY KEY, timestamp TEXT, age FLOAT, salaire FLOAT, "
        "conso_produit_x FLOAT, conso_produit_y FLOAT, niveau_vie TEXT, "
        "classe INTEGER, label TEXT, proba_malade FLOAT)"))

INSERT_SQL = (                                  # requete d'insertion preparee
    "INSERT INTO predictions "
    "(timestamp, age, salaire, conso_produit_x, conso_produit_y, "
    "niveau_vie, classe, label, proba_malade) VALUES "
    "(:timestamp, :age, :salaire, :cx, :cy, :niveau_vie, :classe, :label, :proba)")

def log_prediction(patient: dict, resultat: dict):
    logger.info(f"PREDICTION | {patient} -> {resultat}")   # 1) console
    with engine.begin() as conn:                           # 2) 1 ligne en base
        conn.execute(text(INSERT_SQL), {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "age": patient["age"], "salaire": patient["salaire"],
            "cx": patient["conso_produit_x"], "cy": patient["conso_produit_y"],
            "niveau_vie": patient["niveau_vie"],
            "classe": resultat["classe"], "label": resultat["label"],
            "proba": resultat["proba_malade"]})
