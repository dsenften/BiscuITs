# Result Processor Service

## Beschreibung
Der Result Processor Service verarbeitet die Ergebnisse der Dokumenten- und Adressanalyse. Er empfängt die Ergebnisse über RabbitMQ, bereitet diese auf und sendet sie an die UI-Komponente.

## Funktionen
- Verarbeitung von Analyseergebnissen
- Formatierung und Strukturierung der Daten
- Weiterleitung an die UI

## Konfiguration
Die Anwendung verwendet Umgebungsvariablen für die Konfiguration:
- `RABBITMQ_HOST`: Host der RabbitMQ-Instanz (Standard: localhost)
- `RABBITMQ_PORT`: Port der RabbitMQ-Instanz (Standard: 5672)
- `RABBITMQ_USER`: Benutzername für RabbitMQ (Standard: guest)
- `RABBITMQ_PASSWORD`: Passwort für RabbitMQ (Standard: guest)

## Schnittstellen
- Eingangs-Queue: `processing_result`
- Ausgangs-Queue: `ui_updates`

## Start
```bash
python app.py
```

## Docker
```bash
docker build -t result-processor .
docker run -e RABBITMQ_HOST=rabbitmq result-processor
```