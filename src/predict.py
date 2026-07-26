# CONTENU de src/predict.py

import joblib, pandas as pd
from src import config

_model = None                                  # cache : charge une seule fois

def load_model(path=config.MODEL_PATH):
    global _model
    if _model is None:
        _model = joblib.load(path)             # charge le .pkl depuis le disque
    return _model

def predict_one(patient: dict):
    model = load_model()
    X = pd.DataFrame([patient])                # 1 patient -> tableau 1 ligne
    classe = int(model.predict(X)[0])         # 0=sain, 1=malade
    proba = float(model.predict_proba(X)[0][1])   # probabilite d'etre malade
    return {"classe": classe,
            "label": "malade" if classe == 1 else "sain",
            "proba_malade": round(proba, 3)}

if __name__ == "__main__":
    p = {"age": 62, "salaire": 28000, "conso_produit_x": 9.5,
         "conso_produit_y": 8.0, "niveau_vie": "moyen"}
    print(predict_one(p))
