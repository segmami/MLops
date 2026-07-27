# Projet MLOps : Classification patients (malade / sain)

Pipeline MLOps complet de bout en bout : des donnees brutes jusqu'a une API deployee en ligne, avec reentrainement automatique base sur les diagnostics confirmes par un medecin.

## Objectif

Predire la maladie d'un patient, et ameliorer le modele en continu grace aux diagnostics confirmes (verite terrain).

---

## Architecture globale

L'architecture de mon projet suit un pipeline MLOps complet : les donnees sont pretraitees puis utilisees pour entrainer un modele Scikit-learn. Les experiences sont suivies avec MLflow et le meilleur modele est sauvegarde au format .pkl. Une API FastAPI expose le modele aux utilisateurs via un frontend. Chaque prediction est enregistree dans PostgreSQL, puis les diagnostics confirmes servent au reentrainement automatique. GitHub Actions assure les tests et le deploiement continu vers Render.

```
                    +----------------------+
                    |  Donnees patients    |
                    |   patients.csv       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Pretraitement        |
                    | - Nettoyage          |
                    | - Imputation         |
                    | - Encodage           |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Entrainement ML      |
                    | train.py             |
                    | + MLflow             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | best_classifier.pkl  |
                    | (GitHub)             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | FastAPI              |
                    | /predict             |
                    | /health              |
                    | /confirmer           |
                    +-------+--------------+
                            |
           +----------------+----------------+
           v                                 v
+--------------------+            +--------------------+
| Front Public       |            | Front Medecin      |
| index.html         |            | confirm.html       |
| Prediction         |            | Diagnostic reel    |
+----------+---------+            +---------+----------+
           |                                |
           v                                v
+--------------------+            +--------------------+
| predictions        |            | diagnostics_       |
| (supposition IA)   |            | confirmes          |
+----------+---------+            | (verite terrain)   |
           |                      +---------+----------+
           |                                |
           +---------------+----------------+
                           v
                +----------------------+
                | PostgreSQL           |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | retrain.py           |
                | Reentrainement       |
                +----------+-----------+
                           |
                           v
                Nouveau best_classifier.pkl
                           |
                           v
                        GitHub
                           |
                           v
                    GitHub Actions
                           |
                           v
                        Render
                    (Redeploiement)
```

---

## Flux complet

```
CSV
 v
Pretraitement
 v
Entrainement
 v
Modele (.pkl)
 v
FastAPI
 v
Prediction
 v
PostgreSQL
 v
Diagnostic confirme
 v
Reentrainement
 v
Nouveau modele
 v
GitHub
 v
CI/CD
 v
Render
```

---

## Architecture des composants

```
Frontend
    |
    v
FastAPI
    |
    +--------------> Modele (.pkl)
    |
    +--------------> PostgreSQL
```

---

## Pipeline MLOps

```
Collecte des donnees
        |
        v
Pretraitement
        |
        v
Entrainement
        |
        v
MLflow (suivi des experiences)
        |
        v
Sauvegarde du modele
        |
        v
Deploiement API
        |
        v
Predictions
        |
        v
Monitoring
        |
        v
Reentrainement automatique
```

---

## Architecture CI/CD

```
Developpeur
     |
 git push
     |
     v
GitHub
     |
     v
GitHub Actions
     |
     +-- Tests (pytest)
     +-- Build Docker
     +-- Verifications
     |
     v
Render
     |
     v
Application en ligne
```

---

## Les composants a retenir

| Composant | Role |
|---|---|
| CSV | Donnees d'origine |
| Preprocessing | Nettoyer et preparer les donnees |
| Scikit-learn | Entrainer le modele |
| MLflow | Suivre les experiences |
| Joblib | Sauvegarder le modele |
| FastAPI | Exposer le modele via une API |
| Frontend | Interface utilisateur |
| PostgreSQL | Stocker predictions et diagnostics |
| GitHub | Versionner le code et le modele |
| GitHub Actions | CI/CD |
| Docker | Conteneuriser l'application |
| Render | Heberger l'application |
| retrain.py | Reentrainer le modele |

---

## Les deux tables (a ne pas confondre)

| Table | Contenu | Usage |
|---|---|---|
| `predictions` | ce que le modele SUPPOSE | monitoring |
| `diagnostics_confirmes` | ce que le medecin CONFIRME | reentrainement |

Regle d'or : on reentraine sur la verite confirmee, jamais sur les predictions (sinon le modele apprendrait sur ses propres suppositions).

---

## Structure du projet

```
MLOPS/
├── data/patients.csv
├── src/
│   ├── config.py            constantes + DATABASE_URL
│   ├── data.py              chargement + split
│   ├── preprocessing.py     imputation + encodage
│   ├── train.py             entrainement + MLflow
│   ├── predict.py           charge le .pkl + predit
│   ├── logger.py            ecrit dans la table predictions
│   ├── confirm.py           ecrit dans diagnostics_confirmes
│   └── retrain.py           reentraine sur la verite
├── api/main.py              /predict + /confirmer + /health
├── frontend/index.html      page publique
├── confirme/index.html      page medecin
├── tests/test_api.py        tests pytest
├── .github/workflows/       ci.yml + retrain.yml
├── Dockerfile
└── requirements.txt
```

---

## Endpoints de l'API

| Route | Methode | Role |
|---|---|---|
| `/health` | GET | verifier que l'API tourne |
| `/predict` | POST | prediction (front public) |
| `/confirmer` | POST | diagnostic confirme (front medecin) |

---

## Deploiement

| Element | Ou |
|---|---|
| Code + Dockerfile + modele .pkl | GitHub |
| Image Docker construite + API | Render (Web Service) |
| Page publique | Render (Static Site) |
| Page medecin | Render (Static Site) |
| Base de donnees | Render (PostgreSQL) |

Le Dockerfile vit sur GitHub. Render construit l'image Docker et fait tourner l'API. A chaque `git push`, GitHub Actions teste (CI) puis Render reconstruit et redeploie (CD).

---

## Stack technique

Python · scikit-learn · MLflow · FastAPI · PostgreSQL · Docker · GitHub · GitHub Actions · Render

## Points cles

Suivi des experiences avec MLflow · API REST securisee et modulaire · Reentrainement automatique sur nouvelles donnees · CI/CD pour un deploiement continu · Modele toujours a jour et performant
