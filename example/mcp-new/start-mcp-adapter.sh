#!/bin/bash

# Pfad zum Projektverzeichnis
PROJECT_DIR="/Users/daniel/GitRepository/FFHS/BiscuITs"
MCP_DIR="$PROJECT_DIR/example/mcp-new"

# Log-Datei
LOG_FILE="/tmp/zeit-mcp-server.log"

# Beende eventuell laufende Instanzen auf Port 8081
pid=$(lsof -ti:8081)
if [ -n "$pid" ]; then
  echo "Beende laufenden Server auf Port 8081 (PID: $pid)"
  kill -9 "$pid" 2>/dev/null
fi

# Starte den HTTP-Server im Hintergrund
cd "$MCP_DIR" || exit 1
echo "$(date): Starte Zeit-Demo-Server auf http://127.0.0.1:8081" >> "$LOG_FILE"
poetry run python "$MCP_DIR/mcp-server.py" >> "$LOG_FILE" 2>&1 &

# Warte kurz, bis der Server gestartet ist
sleep 2

# Prüfe, ob der Server läuft
if ! curl -s http://127.0.0.1:8081/ > /dev/null; then
  echo "Fehler: Zeit-Demo-Server konnte nicht gestartet werden" >> "$LOG_FILE"
  exit 1
fi

# Starte den MCP-Adapter im Vordergrund
echo "$(date): Starte MCP-Adapter" >> "$LOG_FILE"
exec poetry run python "$MCP_DIR/mcp-adapter.py"
