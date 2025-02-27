# Address Analyzer Service

## Beschreibung
Der Address Analyzer Service ist verantwortlich für die Analyse und Validierung von Adressen. Er empfängt Adressdaten über RabbitMQ und verarbeitet diese.

## Funktionen
- Validierung von Adressformaten
- Geokodierung (Umwandlung von Adressen in Koordinaten)
- Adresskorrektur und -normalisierung

## Konfiguration
Die Anwendung verwendet Umgebungsvariablen für die Konfiguration:
- `RABBITMQ_HOST`: Host der RabbitMQ-Instanz (Standard: localhost)
- `RABBITMQ_PORT`: Port der RabbitMQ-Instanz (Standard: 5672)
- `RABBITMQ_USER`: Benutzername für RabbitMQ (Standard: guest)
- `RABBITMQ_PASSWORD`: Passwort für RabbitMQ (Standard: guest)

## Schnittstellen
- Eingangs-Queue: `address_processing`
- Ausgangs-Queue: `processing_result`

## Start
```bash
python app.py
```

## Docker
```bash
docker build -t address-analyzer .
docker run -e RABBITMQ_HOST=rabbitmq address-analyzer
```