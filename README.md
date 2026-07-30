# Projet MLOps : Classification patients (malade / sain)

Pipeline MLOps complet de bout en bout : de la creation d'un dossier patient jusqu'a une API deployee en ligne, avec suivi par identifiant, monitoring de la performance reelle et reentrainement automatique base sur les diagnostics confirmes par un medecin.

## Objectif

Predire la maladie d'un patient, mesurer la performance reelle du modele, et l'ameliorer en continu grace aux diagnostics confirmes (verite terrain).

---

## Le workflow metier

Le systeme reproduit un parcours realiste en cabinet, ou la prediction et la verite arrivent a deux moments differents, relies par un identifiant unique.

```
Semaine 1 : INFIRMIERE
   cree le dossier patient (page publique)
   le modele predit malade ou sain
   une ligne est creee dans "predictions" avec un ID
   l'ID est affiche et remis au patient
        |
        v
Le PATIENT repart avec son numero de suivi (ID)
        |
        v (une semaine plus tard)
Semaine 2 : MEDECIN
   tape l'ID du patient (page medecin)
   les champs se remplissent automatiquement
   il verifie avec le patient, entre le vrai diagnostic
   la verite est enregistree dans "diagnostics_confirmes"
   reliee a la prediction par l'ID
        |
        v
MONITORING
   relie prediction et verite par l'ID (JOIN)
   affiche predit vs reel + precision reelle du modele
        |
        v
REENTRAINEMENT
   le modele reapprend sur les diagnostics confirmes
```

Regle d'or : on reentraine sur la verite confirmee, jamais sur les predictions du modele (sinon il apprendrait sur ses propres suppositions et se renforcerait dans ses erreurs).

---

## Architecture globale

Les donnees sont pretraitees puis utilisees pour entrainer un modele scikit-learn. Les experiences sont suivies avec MLflow et le meilleur modele est sauvegarde au format .pkl. Une API FastAPI expose le modele via trois interfaces (infirmiere, medecin, monitoring). Chaque prediction est enregistree dans PostgreSQL avec un ID, puis les diagnostics confirmes (relies par cet ID) servent au monitoring et au reentrainement. GitHub Actions assure les tests et le reentrainement, Render construit l'image Docker et deploie l'API.

```
                    +----------------------+
                    |  Donnees patients    |
                    |   patients.csv       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Pretraitement        |
                    | nettoyage            |
                    | imputation           |
                    | encodage             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Entrainement ML      |
                    | train.py + MLflow    |
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
                    | API FastAPI          |
                    | /predict             |
                    | /confirmer           |
                    | /patient/{id}        |
                    | /monitoring          |
                    | /health              |
                    +-------+--------------+
                            |
        +-------------------+-------------------+
        v                                       v
+--------------------+                +--------------------+
| Page infirmiere    |                | Page medecin       |
| index.html         |                | recherche par ID   |
| predit + affiche ID|                | remplit + confirme |
+----------+---------+                +---------+----------+
           |                                    |
           v                                    v
+--------------------+                +--------------------+
| predictions        |  <-- ID reliee --  | diagnostics_       |
| (supposition IA)   |                | confirmes          |
| id, features,      |                | prediction_id,     |
| classe, proba      |                | malade (verite)    |
+----------+---------+                +---------+----------+
           |                                    |
           +----------------+-------------------+
                            v
                +----------------------+
                | PostgreSQL           |
                +----------+-----------+
                           |
              +------------+------------+
              v                         v
    +------------------+     +---------------------+
    | Page monitoring  |     | retrain.py          |
    | predit vs reel   |     | reentraine sur      |
    | precision reelle |     | la verite           |
    +------------------+     +----------+----------+
                                        |
                                        v
                            Nouveau best_classifier.pkl
                                        |
                                        v
                              GitHub -> GitHub Actions
                                        |
                                        v
                                     Render
                                 (redeploiement)
```

---

## Les trois tables et interfaces

| Interface | Role | Ecrit dans |
|---|---|---|
| Page infirmiere | cree le dossier, le modele predit, affiche l'ID | `predictions` |
| Page medecin | recherche par ID, verifie, confirme le vrai diagnostic | `diagnostics_confirmes` |
| Page monitoring | compare predit vs reel, affiche la precision reelle | lecture (JOIN) |

---

## Les deux tables (reliees par ID)

| Table | Contenu | Usage |
|---|---|---|
| `predictions` | id, features, classe predite, proba | monitoring |
| `diagnostics_confirmes` | prediction_id, malade (verite) | reentrainement |

Le lien : `diagnostics_confirmes.prediction_id` pointe vers `predictions.id`. Aucune redondance : le medecin ne re-saisit pas les infos du patient, il donne juste l'ID et le vrai diagnostic.

---

## Le monitoring

La table `predictions` (suppositions) et `diagnostics_confirmes` (verite) sont reliees par l'ID. Un JOIN permet de comparer, pour chaque patient, ce que le modele avait predit et le vrai diagnostic. La page monitoring affiche un tableau predit vs reel et calcule la precision reelle du modele en production. C'est cette mesure qui indique quand un reentrainement est utile.

---

## Flux technique : HTML, API, PostgreSQL

Les pages HTML ne parlent jamais directement a la base. Elles passent toujours par l'API, seule a communiquer avec PostgreSQL.

```
HTML  ->  (JSON)  ->  API FastAPI  ->  (SQL)  ->  PostgreSQL
```

Le detail du trajet, dans les deux sens :

```
1. HTML : le JavaScript cree le JSON de la requete (JSON.stringify)
          et appelle une route de l'API via fetch()
2. API  : FastAPI recoit le JSON, le valide avec Pydantic (objet Python)
3. Code : logger.py / confirm.py / main.py executent les requetes SQL
4. SQLAlchemy : envoie le SQL a PostgreSQL (create_engine + text)
5. PostgreSQL : stocke ou renvoie les donnees (hebergee sur Render)
6. API  : FastAPI transforme le resultat en JSON (automatiquement)
7. HTML : recoit le JSON (rep.json()) et l'affiche
```

Le JSON circule dans les deux sens : c'est le JavaScript qui cree le JSON de la requete, et FastAPI qui cree le JSON de la reponse.

---

## Les requetes SQL du projet

Le SQL est ecrit dans les fichiers Python (jamais dans le HTML), execute via SQLAlchemy avec des parametres nommes (`:param`) qui protegent de l'injection SQL.

Creation des tables (au demarrage de l'API) :

```sql
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY, timestamp TEXT, age FLOAT, salaire FLOAT,
    conso_produit_x FLOAT, conso_produit_y FLOAT, niveau_vie TEXT,
    classe INTEGER, label TEXT, proba_malade FLOAT);

CREATE TABLE IF NOT EXISTS diagnostics_confirmes (
    id SERIAL PRIMARY KEY, prediction_id INTEGER, malade INTEGER);
```

Page infirmiere (ecrire une prediction et recuperer son ID) :

```sql
INSERT INTO predictions (timestamp, age, salaire, conso_produit_x,
    conso_produit_y, niveau_vie, classe, label, proba_malade)
VALUES (:timestamp, :age, :salaire, :cx, :cy, :niveau_vie,
    :classe, :label, :proba)
RETURNING id;
```

Page medecin (lire une prediction par ID pour remplir les champs) :

```sql
SELECT * FROM predictions WHERE id = :id;
```

Page medecin (enregistrer la verite, reliee par prediction_id) :

```sql
INSERT INTO diagnostics_confirmes (prediction_id, malade)
VALUES (:prediction_id, :malade);
```

Page monitoring (relier prediction et verite pour comparer predit vs reel) :

```sql
SELECT p.id, p.age, p.classe AS predit, p.proba_malade, d.malade AS reel
FROM predictions p
JOIN diagnostics_confirmes d ON d.prediction_id = p.id
ORDER BY p.id DESC;
```

Correspondance page, route et SQL :

| Page | Route API | Operation SQL |
|---|---|---|
| Infirmiere | POST `/predict` | `INSERT INTO predictions ... RETURNING id` |
| Medecin | GET `/patient/{id}` | `SELECT * FROM predictions WHERE id` |
| Medecin | POST `/confirmer` | `INSERT INTO diagnostics_confirmes` |
| Monitoring | GET `/monitoring` | `SELECT ... JOIN diagnostics_confirmes` |

---

## Reentrainement automatique

```
Declencheur   : GitHub Actions, cron (chaque 6 mois) ou manuel
Reentrainement: sur une machine GitHub, retrain.py lit
                diagnostics_confirmes et reentraine. MLflow trace
                params et metriques, le meilleur modele (F1) est garde
Nouveau modele: best_classifier.pkl commit sur GitHub
Redeploiement : Render reconstruit l'image Docker, l'API utilise
                le nouveau modele
```

Garde-fous : on reentraine sur la verite (pas les predictions), jamais a chaque prediction (periodique), les tests CI bloquent le mauvais code, MLflow trace chaque version, PostgreSQL conserve la verite et Pydantic valide chaque entree.

---

## Pipeline CI/CD

```
Code local
   |
 git push
   |
   v
GitHub
   |
   v
GitHub Actions
   +-- Tests (pytest)
   +-- si un test echoue, tout s'arrete
   |
   v
Render
   +-- reconstruit l'image Docker
   +-- redeploie l'API
   |
   v
Application en ligne
```

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
│   ├── logger.py            ecrit dans predictions + renvoie l'ID
│   ├── confirm.py           ecrit dans diagnostics_confirmes (prediction_id)
│   └── retrain.py           reentraine sur la verite
├── api/main.py              /predict /confirmer /patient/{id} /monitoring /health
├── frontend/index.html      page infirmiere (predit + affiche ID)
├── confirme/index.html      page medecin (recherche par ID + confirme)
├── monitoring/index.html    page monitoring (predit vs reel + precision)
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
| `/predict` | POST | prediction + renvoie l'ID de suivi (infirmiere) |
| `/patient/{id}` | GET | recupere une prediction par ID (auto-remplissage medecin) |
| `/confirmer` | POST | enregistre le vrai diagnostic, relie par prediction_id (medecin) |
| `/monitoring` | GET | compare predit vs reel, precision reelle |

---

## Deploiement

| Element | Ou |
|---|---|
| Code + Dockerfile + modele .pkl | GitHub |
| Image Docker construite + API | Render (Web Service) |
| Page infirmiere | Render (Static Site) |
| Page medecin | Render (Static Site) |
| Page monitoring | Render (Static Site) |
| Base de donnees | Render (PostgreSQL) |

Le Dockerfile vit sur GitHub. Render construit l'image Docker et fait tourner l'API. A chaque git push, GitHub Actions teste (CI) puis Render reconstruit et redeploie (CD). Les pages HTML sont des Static Sites separes, redeployes individuellement.

---

## Composants a retenir

| Composant | Role |
|---|---|
| CSV | donnees d'origine |
| Preprocessing | nettoyer et preparer les donnees |
| scikit-learn | entrainer le modele |
| MLflow | suivre les experiences |
| Joblib | sauvegarder le modele |
| FastAPI | exposer le modele via une API |
| Frontend | interfaces infirmiere, medecin, monitoring |
| PostgreSQL | stocker predictions et diagnostics (relies par ID) |
| GitHub | versionner le code et le modele |
| GitHub Actions | tests + reentrainement |
| Docker | conteneuriser l'application |
| Render | heberger l'application |
| retrain.py | reentrainer le modele sur la verite |

---

## Stack technique

Python · scikit-learn · MLflow · FastAPI · PostgreSQL · Docker · GitHub · GitHub Actions · Render

## Points cles

Suivi par identifiant unique (pas de redondance) · Monitoring de la precision reelle (predit vs verite) · Reentrainement automatique sur la verite terrain · CI/CD pour un deploiement continu · Modele mesure et maintenu a jour

---

## Note sur la pratique industrielle

En production reelle, la prediction et la verite terrain arrivent a des moments differents et sont reliees par un identifiant. Ce projet reproduit ce principe : l'infirmiere cree la prediction (avec ID), le medecin apporte la verite plus tard (relie par le meme ID). C'est ce qui permet un monitoring fiable et un reentrainement sur des donnees reellement verifiees.
