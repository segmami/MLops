import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.getenv("DATABASE_URL"))

# --- Table VERITE ---
verite = pd.read_sql("SELECT * FROM diagnostics_confirmes", engine)
verite.to_csv("export_diagnostics.csv", index=False)
print(f"diagnostics_confirmes : {len(verite)} lignes -> export_diagnostics.csv")

# ← ICI : séparer anciens et nouveaux (après avoir chargé "verite")
verite[verite["id"] <= 100].to_csv("anciens.csv", index=False)   # les 100 du CSV
verite[verite["id"] >  100].to_csv("nouveaux.csv", index=False)  # les confirmés récents
print(f"anciens : {len(verite[verite['id'] <= 100])} | nouveaux : {len(verite[verite['id'] > 100])}")

# --- Table PREDICTIONS ---
preds = pd.read_sql("SELECT * FROM predictions", engine)
preds.to_csv("export_predictions.csv", index=False)
print(f"predictions : {len(preds)} lignes -> export_predictions.csv")