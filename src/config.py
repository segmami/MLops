# CONTENU de src/config.py

from pathlib import Path                    # chemins de fichiers propres
import os                                   # lire la variable d'environnement DATABASE_URL

# --- Reproductibilite ---
SEED = 42                                   # fixe le hasard -> memes resultats

# --- Dossiers ---
ROOT = Path(__file__).resolve().parent.parent   # racine du projet
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
LOGS_DIR = ROOT / "logs"

# --- Fichiers ---
RAW_DATA = DATA_DIR / "patients.csv"                # donnees de depart
MODEL_PATH = MODELS_DIR / "best_classifier.pkl"     # modele (versionne sur GitHub)

# --- Base de donnees ---
# En local : DATABASE_URL absente -> SQLite (fichier local.db).
# En ligne : Render injecte DATABASE_URL -> PostgreSQL permanent.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'local.db'}")

# --- Colonnes (issues de l'exploration) ---
TARGET = "malade"                                   # cible (0=sain, 1=malade)
DROP_COLS = ["id_patient", "date_naissance"]        # supprimees
MEAN_IMPUTE_COLS = ["age"]                          # NaN -> moyenne
MEDIAN_IMPUTE_COLS = ["salaire"]                    # NaN -> mediane
CAT_COLS = ["niveau_vie"]                           # categoriel -> encode
PASSTHROUGH_COLS = ["conso_produit_x", "conso_produit_y"]  # gardees

# --- Parametres ---
TEST_SIZE = 0.2                             # 20% test / 80% train
MLFLOW_TRACKING_URI = f"sqlite:///{ROOT / 'mlflow.db'}"

# --- Cree les dossiers s'ils manquent ---
for d in (DATA_DIR, MODELS_DIR, LOGS_DIR):
    d.mkdir(exist_ok=True)
