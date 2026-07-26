# CONTENU de src/train.py

import joblib, mlflow, mlflow.sklearn
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.model_selection import train_test_split
from src import config
from src.data import load_data
from src.preprocessing import build_preprocessor

def get_models():
    # Les 2 candidats a comparer :
    return {
        "logreg": LogisticRegression(class_weight="balanced", max_iter=1000,
                                     random_state=config.SEED),
        "random_forest": RandomForestClassifier(max_depth=2, n_estimators=25,
                          class_weight="balanced", random_state=config.SEED),
    }

def evaluate(pipe, X_test, y_test):
    y_pred = pipe.predict(X_test)                     # predictions sur le test
    return {"accuracy":  accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall":    recall_score(y_test, y_pred, zero_division=0),
            "f1":        f1_score(y_test, y_pred, zero_division=0)}

def train(df=None):
    # df=None -> on lit le CSV. Sinon on utilise le DataFrame fourni (ex: la base de verite).
    if df is None:
        df = load_data()
    data = df.drop(columns=[c for c in config.DROP_COLS if c in df.columns])  # enleve id/date si presents
    X = data.drop(columns=config.TARGET); y = data[config.TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.SEED)

    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)   # ou MLflow enregistre
    mlflow.set_experiment("classification_patients")

    resultats = {}
    for nom, clf in get_models().items():
        with mlflow.start_run(run_name=nom):              # un run MLflow par modele
            pipe = Pipeline([("preprocessing", build_preprocessor()), ("clf", clf)])
            pipe.fit(X_train, y_train)                    # entraine
            metrics = evaluate(pipe, X_test, y_test)      # evalue

            mlflow.log_param("model", nom)                # trace le nom
            mlflow.log_metrics(metrics)                   # trace les 4 metriques
            mlflow.sklearn.log_model(pipe, name="model",
                                     serialization_format="cloudpickle")  # evite bug skops/numpy

            resultats[nom] = {"pipeline": pipe, "f1": metrics["f1"]}
            print(f"{nom:15} | F1={metrics['f1']:.3f} | recall={metrics['recall']:.3f}")

    meilleur = max(resultats, key=lambda n: resultats[n]["f1"])   # F1 le plus haut
    joblib.dump(resultats[meilleur]["pipeline"], config.MODEL_PATH)  # sauve le .pkl
    print(f"Meilleur : {meilleur} -> sauvegarde {config.MODEL_PATH}")

if __name__ == "__main__":
    train()
