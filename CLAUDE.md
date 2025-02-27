# BiscuITs Development Guide

## Development Commands
- Setup: `poetry install`
- Run UI: `streamlit run ui/app.py`
- Run Service: `python src/services/<service_name>/app.py`
- Run Docker: `docker-compose up`
- Run Example: `python example/docling/<script_number>-<script_name>.py`

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local imports
- **Formatting**: Use docstrings for functions, follow PEP 8 guidelines
- **Types**: Use type hints for function arguments and return values
- **Naming**: 
  - Variables/functions: snake_case
  - Classes: CamelCase
  - Constants: UPPER_CASE
- **Error Handling**: Use try/except blocks with specific exceptions, log errors
- **Documentation**: Include docstrings with Args/Returns sections
- **Environment**: Use dotenv for configuration with sensible defaults

## Project Structure
- Microservice architecture with Flask-based services
- OpenAI for AI integration
- RabbitMQ for inter-service communication

## Git-Commit Messages
Vermeide zu ausführliche Beschreibungen oder unnötige Details.
Beginnen Sie mit einem kurzen Satz in Imperativform, der nicht länger als 50 Zeichen sein sollte und folgende
Präfixe beinhaltet:

- "fix:" für Fehlerbehebungen
- "feat:" für neue Funktionen
- "perf:" für Leistungsverbesserungen
- "docs:" für Dokumentationsänderungen
- "style:" für Formatierungsänderungen
- "refactor:" für Code-Umstrukturierung
- "test:" für das Hinzufügen fehlender Tests
- "chore:" für Wartungsaufgaben

Lassen dann eine Leerzeile frei und fahre mit einer ausführlicheren Erklärung fort. Schreibe nur einen Satz für 
den ersten Teil und nicht mehr als drei oder vier Sätze für die ausführliche Erläuterung, wobei du jeden Satz 
durch einen Aufzählungspunkt abrennst.
