FROM python:3.12-slim                              # mini-Linux + Python 3.12
WORKDIR /app                                       # dossier de travail
COPY requirements.txt .                            # copie D'ABORD la liste des libs
RUN pip install --no-cache-dir -r requirements.txt # installe (cache-friendly)
COPY . .                                           # copie le code + models/*.pkl
EXPOSE 8000
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}