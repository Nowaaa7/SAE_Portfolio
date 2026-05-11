# Image de base
FROM python:3.10-slim

# --- AJOUT CRUCIAL : Proxy pour le conteneur ---
ENV http_proxy="http://cache-etu.univ-artois.fr:3128"
ENV https_proxy="http://cache-etu.univ-artois.fr:3128"
ENV HTTP_PROXY="http://cache-etu.univ-artois.fr:3128"
ENV HTTPS_PROXY="http://cache-etu.univ-artois.fr:3128"
# -----------------------------------------------

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copie et installation de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Lancement
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]