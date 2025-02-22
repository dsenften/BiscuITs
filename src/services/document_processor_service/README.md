# Document Processor Service

Dieser Microservice verarbeitet Dokumente mit Docling und speichert die Ergebnisse in Qdrant.

## Features

- Empfängt Dokument-IDs vom Document Service
- Verarbeitet Dokumente mit Docling (Embedding, Zusammenfassung, Keywords, Sentiment)
- Speichert die Ergebnisse in Qdrant

## Setup

1. Kopiere `.env.example` zu `.env` und passe die Werte an
2. Installiere die Abhängigkeiten: `pip install -r requirements.txt`
3. Starte den Service: `python app.py`

## API Endpoints

### POST /process

Verarbeitet ein Dokument anhand seiner ID.

Request Body:
```json
{
    "document_id": "string"
}
```

Response:
```json
{
    "status": "success",
    "document_id": "string",
    "summary": "string",
    "keywords": ["string"],
    "sentiment": "string"
}
```
