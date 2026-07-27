# CONTENU de src/confirm.py
import logging
from sqlalchemy import create_engine, text
from src import config

logger = logging.getLogger("patients_api")

engine = create_engine(config.DATABASE_URL)

# La table relie la verite a une prediction par prediction_id
with engine.begin() as conn:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS diagnostics_confirmes ("
        "id SERIAL PRIMARY KEY, prediction_id INTEGER, malade INTEGER)"))

INSERT_SQL = (
    "INSERT INTO diagnostics_confirmes (prediction_id, malade) "
    "VALUES (:prediction_id, :malade)"
)

def confirm_diagnostic(data: dict):
    # data contient prediction_id (l'ID) et malade (le vrai diagnostic)
    logger.info(f"CONFIRMATION | {data}")
    with engine.begin() as conn:
        conn.execute(text(INSERT_SQL), {
            "prediction_id": data["prediction_id"],
            "malade": data["malade"],
        })