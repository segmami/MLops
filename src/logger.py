import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from src import config

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("patients_api")

engine = create_engine(config.DATABASE_URL)

CREATE_SQL = (
    "CREATE TABLE IF NOT EXISTS predictions ("
    "id SERIAL PRIMARY KEY, timestamp TEXT, age FLOAT, salaire FLOAT, "
    "conso_produit_x FLOAT, conso_produit_y FLOAT, niveau_vie TEXT, "
    "classe INTEGER, label TEXT, proba_malade FLOAT)"
)
with engine.begin() as conn:
    conn.execute(text(CREATE_SQL))

INSERT_SQL = (
    "INSERT INTO predictions "
    "(timestamp, age, salaire, conso_produit_x, conso_produit_y, "
    "niveau_vie, classe, label, proba_malade) VALUES "
    "(:timestamp, :age, :salaire, :cx, :cy, :niveau_vie, :classe, :label, :proba) "
    "RETURNING id"                                  # renvoie l'id cree
)

def log_prediction(patient: dict, resultat: dict):
    logger.info(f"PREDICTION | {patient} -> {resultat}")
    with engine.begin() as conn:
        result = conn.execute(text(INSERT_SQL), {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "age": patient["age"], "salaire": patient["salaire"],
            "cx": patient["conso_produit_x"], "cy": patient["conso_produit_y"],
            "niveau_vie": patient["niveau_vie"],
            "classe": resultat["classe"], "label": resultat["label"],
            "proba": resultat["proba_malade"],
        })
        return result.scalar()                       # l'id de la ligne