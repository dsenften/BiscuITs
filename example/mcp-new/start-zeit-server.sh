#!/bin/bash

# Pfad zum Projektverzeichnis
PROJECT_DIR="/Users/daniel/GitRepository/FFHS/BiscuITs"

# Wechsle ins Projektverzeichnis
cd "$PROJECT_DIR/example/mcp-new" || exit 1

# Beende eventuell laufende Instanzen auf Port 8081
pid=$(lsof -ti:8081)
if [ -n "$pid" ]; then
  echo "Beende laufenden Server auf Port 8081 (PID: $pid)"
  kill -9 "$pid" 2>/dev/null
fi

# Führe den Zeit-Demo-Server aus
exec poetry run python "$PROJECT_DIR/example/mcp-new/mcp-server.py"
