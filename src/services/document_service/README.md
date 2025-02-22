# Document Processing Service

Dieser Microservice nimmt Dokumente über eine REST-API entgegen und leitet sie zur Verarbeitung an eine RabbitMQ Message Queue weiter.

## Features

- Dokument-Upload über REST-API
- Unterstützung verschiedener Dateitypen (txt, pdf, png, jpg, jpeg, doc, docx)
- Sichere Dateinamenverarbeitung
- Asynchrone Verarbeitung über RabbitMQ
- Health Check Endpoint
- Konfigurierbar über Umgebungsvariablen

## Installation

1. Erstellen Sie eine virtuelle Umgebung und aktivieren Sie diese:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

2. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

3. Kopieren Sie die Beispiel-Umgebungsdatei und passen Sie sie an:
```bash
cp .env.example .env
```

4. Starten Sie den Service:
```bash
python app.py
```

## API Endpoints

### POST /upload
Lädt ein Dokument hoch und sendet es zur Verarbeitung.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (Datei)

**Response:**
```json
{
    "status": "success",
    "message": "Datei erfolgreich hochgeladen und zur Verarbeitung weitergeleitet",
    "filename": "example.pdf"
}
```

### GET /health
Health Check Endpoint

**Response:**
```json
{
    "status": "healthy",
    "service": "document_service"
}
```

## Konfiguration

Die folgenden Umgebungsvariablen können in der `.env` Datei konfiguriert werden:

- `PORT`: Server Port (Standard: 5000)
- `RABBITMQ_HOST`: RabbitMQ Host (Standard: localhost)
- `RABBITMQ_PORT`: RabbitMQ Port (Standard: 5672)
- `RABBITMQ_USER`: RabbitMQ Benutzername (Standard: guest)
- `RABBITMQ_PASSWORD`: RabbitMQ Passwort (Standard: guest)
