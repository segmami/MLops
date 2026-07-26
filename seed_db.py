# CONTENU de seed_db.py (a la racine)

import pandas as pd
from sqlalchemy import create_engine, text
from src import config

engine = create_engine(config.DATABASE_URL)

# --- Cree la table de verite si absente ---
with engine.begin() as conn:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS diagnostics_confirmes ("
        "id SERIAL PRIMARY KEY, age FLOAT, salaire FLOAT, "
        "conso_produit_x FLOAT, conso_produit_y FLOAT, "
        "niveau_vie TEXT, malade INTEGER)"))
    # Compte les lignes deja presentes (le garde-fou)
    deja = conn.execute(text("SELECT COUNT(*) FROM diagnostics_confirmes")).scalar()

# --- On verse le CSV UNIQUEMENT si la table est vide ---
if deja == 0:
    df = pd.read_csv(config.RAW_DATA).drop(columns=config.DROP_COLS)  # memes colonnes que la table
    df.to_sql("diagnostics_confirmes", engine, if_exists="append", index=False)
    print(f"Seed : {len(df)} lignes du CSV inserees")
else:
    print(f"Deja {deja} lignes -> pas de seed (garde-fou)")   # evite les doublons
