# CONTENU de src/retrain.py

import pandas as pd
from sqlalchemy import create_engine
from src import config
from src.train import train

def charger_verite():
    # Lit UNIQUEMENT la table de verite (diagnostics confirmes par le medecin).
    engine = create_engine(config.DATABASE_URL)
    return pd.read_sql("SELECT * FROM diagnostics_confirmes", engine)

if __name__ == "__main__":
    df = charger_verite()
    print(f"{len(df)} diagnostics confirmes disponibles")
    if len(df) < 20:
        print("Trop peu de donnees pour reentrainer -> on garde le modele actuel")
    else:
        train(df.drop(columns=["id"]))    # enleve la cle technique, reentraine sur la verite
        print("Reentrainement termine -> nouveau best_classifier.pkl")
