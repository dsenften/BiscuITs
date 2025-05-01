# Todo-Manager

Ein einfacher Todo-Manager, der mit Python und Streamlit entwickelt wurde.

## Installation

1. Erstelle eine virtuelle Umgebung:
```bash
python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate
```

2. Installiere die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

## Starten der Anwendung

```bash
streamlit run app.py
```

## Features

- Erstellen und Verwalten von Todos
- Kategorisierung von Aufgaben
- Priorisierung (1-5)
- Fälligkeitsdaten
- Tags für bessere Organisation
- Filterung und Sortierung
- Responsive Design

## Datenbank

Die Anwendung verwendet SQLite als lokale Datenbank. Die Datenbank wird automatisch erstellt, wenn die Anwendung zum ersten Mal gestartet wird.

## Technologien

- Python 3.10+
- Streamlit
- SQLAlchemy
- Pydantic
