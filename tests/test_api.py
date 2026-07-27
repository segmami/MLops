# CONTENU de tests/test_api.py

from fastapi.testclient import TestClient       # simule des appels sans lancer uvicorn
from api.main import app
from src.data import load_data, split_data
from src.predict import predict_one

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_predict():
    p = {"age":62,"salaire":28000,"conso_produit_x":9.5,"conso_produit_y":8.0,"niveau_vie":"moyen"}
    r = client.post("/predict", json=p)          # FRONT 1 (infirmiere)
    assert r.status_code == 200
    assert r.json()["classe"] in [0, 1]
    assert "prediction_id" in r.json()           # doit renvoyer un ID de suivi

def test_predict_invalide():
    r = client.post("/predict", json={"age": 50})   # patient incomplet
    assert r.status_code == 422

def test_confirmer():
    # FRONT 2 (medecin) : on confirme en reliant par prediction_id
    p = {"prediction_id": 1, "malade": 1}
    r = client.post("/confirmer", json=p)
    assert r.status_code == 200
    assert r.json()["prediction_id"] == 1

def test_confirmer_invalide():
    # sans le champ malade -> refuse (422)
    p = {"prediction_id": 1}
    assert client.post("/confirmer", json=p).status_code == 422

def test_split_data():
    X_train, X_test, *_ = split_data(load_data())
    assert len(X_train) == 80 and len(X_test) == 20