# CONTENU de src/confirm.py

import logging
from sqlalchemy import create_engine, text
from src import config

logger = logging.getLogger("patients_api")

engine = create_engine(config.DATABASE_URL)     # meme base que logger.py

# --- Table de la VERITE, creee si absente ---
# Memes colonnes que le CSV (apres drop) + malade = le VRAI diagnostic.
with engine.begin() as conn:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS diagnostics_confirmes ("
        "id SERIAL PRIMARY KEY, age FLOAT, salaire FLOAT, "
        "conso_produit_x FLOAT, conso_produit_y FLOAT, "
        "niveau_vie TEXT, malade INTEGER)"))

INSERT_SQL = (
    "INSERT INTO diagnostics_confirmes "
    "(age, salaire, conso_produit_x, conso_produit_y, niveau_vie, malade) VALUES "
    "(:age, :salaire, :cx, :cy, :niveau_vie, :malade)")

def confirm_diagnostic(patient: dict):
    # patient DOIT contenir "malade" (0 ou 1) : c'est la verite fournie par le medecin.
    logger.info(f"CONFIRMATION | {patient}")
    with engine.begin() as conn:
        conn.execute(text(INSERT_SQL), {
            "age": patient["age"], "salaire": patient["salaire"],
            "cx": patient["conso_produit_x"], "cy": patient["conso_produit_y"],
            "niveau_vie": patient["niveau_vie"], "malade": patient["malade"]})
