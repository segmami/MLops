# mini-Linux avec Python 3.12
FROM python:3.12-slim

# dossier de travail dans le conteneur
WORKDIR /app

# copie d'abord la liste des librairies
COPY requirements.txt .

# installe les librairies
RUN pip install --no-cache-dir -r requirements.txt

# copie tout le code
COPY . .

EXPOSE 8000
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}