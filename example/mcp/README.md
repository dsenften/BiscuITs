# MCP-unterstützter Streamlit Client

Diese Anwendung erweitert einen Streamlit-basierten LLM-Chat-Client mit MCP (Model Context Protocol) Unterstützung, ähnlich wie bei Produkten wie Cursor oder Windsurf.

## Was ist MCP?

Das Model Context Protocol (MCP) ermöglicht es, Kontextinformationen wie Codedateien an LLMs zu übermitteln. Dies verbessert die Fähigkeit der Modelle, Code zu verstehen und mit bestehenden Codebasen zu arbeiten.

## Funktionen

- Integration mit verschiedenen MCP-Servern (OpenAI, Anthropic und benutzerdefinierte Server)
- Einfache Konfiguration über UI oder JSON-Import
- Datei-Upload für Kontextinformationen
- Nahtlose Integration in bestehende Streamlit-Anwendungen
- Docker-Unterstützung für einfache Bereitstellung

## Vorbereitung

1. Stelle sicher, dass Docker und docker-compose installiert sind
2. Klone dieses Repository:
```bash
git clone <repository-url>
cd mcp-streamlit-client
```

## Installation & Start

### Mit Docker

1. Baue und starte den Container:
```bash
docker-compose up --build
```

2. Öffne die Anwendung im Browser unter `http://localhost:8501`

### Ohne Docker

1. Erstelle eine virtuelle Umgebung:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

2. Installiere die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

3. Starte die Anwendung:
```bash
streamlit run app.py
```

## Server-Konfiguration

### Vordefinierte Server

Die Anwendung enthält bereits Konfigurationen für:
- OpenAI MCP
- Anthropic MCP
- Einen lokalen MCP-Server

### Eigenen Server hinzufügen

Es gibt zwei Möglichkeiten, eigene Server hinzuzufügen:

1. **Über die UI:**
   - Navigiere zu "MCP-Einstellungen"
   - Fülle das Formular aus und klicke auf "Server speichern"

2. **Über JSON-Import:**
   - Erstelle eine JSON-Konfiguration im Format:
   ```json
   {
     "name": "Mein MCP-Server",
     "url": "https://mein-server.de/api/mcp",
     "api_key": "mein-api-key",
     "headers": {
       "X-Custom-Header": "Wert"
     }
   }
   ```
   - Kopiere diese JSON in das Import-Formular unter "MCP-Einstellungen"

## Verwendung

1. Wähle "Chat mit MCP" in der Navigation
2. Wähle einen MCP-Server aus der Dropdown-Liste
3. Lade Dateien als Kontext hoch (optional)
4. Gib deine Anfrage ein und sende sie ab

## Anpassung und Erweiterung

Die Anwendung ist modular aufgebaut und kann leicht an eigene Bedürfnisse angepasst werden:

- `mcp_client.py`: Enthält die grundlegende MCP-Funktionalität
- `streamlit_integration.py`: Enthält die Streamlit-UI-Komponenten
- `app.py`: Hauptanwendung und Integrationslogik

## Integration mit bestehenden Projekten

Um MCP in ein bestehendes Projekt zu integrieren:

1. Kopiere die Dateien `mcp_client.py` und `streamlit_integration.py` in dein Projekt
2. Importiere die benötigten Komponenten in deine Anwendung
3. Füge die MCP-Funktionalität zu deiner bestehenden UI hinzu

Beispiel:
```python
from mcp_client import MCPClient, MCPContext
from streamlit_integration import mcp_chat_page, mcp_settings_page

# Dann in deiner Anwendung:
if use_mcp:
    mcp_chat_page()
else:
    your_existing_chat_page()
```

## Weitere Anpassungen

- **API-Keys**: Du kannst API-Keys direkt in der UI angeben oder als Umgebungsvariablen in `docker-compose.yml` setzen
- **Persistente Konfiguration**: Die Konfigurationsdaten werden im Verzeichnis `./config` gespeichert
- **Benutzerdefinierten MCP-Server**: Das generische MCP-Format kann an deine spezifischen Bedürfnisse angepasst werden
