FROM python:3.10-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Kopiere die Requirements-Datei und installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Erstelle Konfigurationsverzeichnis
RUN mkdir -p /app/config

# Kopiere den Anwendungscode
COPY *.py .

# Environment-Variablen
ENV PYTHONUNBUFFERED=1

# Port freigeben
EXPOSE 8501

# Befehl zum Starten der Anwendung
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
