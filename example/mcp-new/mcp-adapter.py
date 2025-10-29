#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP-Adapter für den Zeit-Demo-Server
Übersetzt zwischen MCP-Protokoll (STDIO) und HTTP-Anfragen an den Zeit-Demo-Server
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict

import httpx

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/tmp/zeit-mcp-adapter.log",  # Log in eine Datei schreiben
)
logger = logging.getLogger(__name__)

# Server-URL
SERVER_URL = "http://127.0.0.1:8081"


# MCP-Protokoll-Handler
class MCPAdapter:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet eine MCP-Nachricht und gibt eine Antwort zurück"""
        try:
            message_type = message.get("type")

            if message_type == "ping":
                return {"type": "pong"}

            elif message_type == "list_tools":
                # Werkzeuge vom Server abrufen
                response = await self.client.get(f"{SERVER_URL}/tools")
                tools = response.json()

                # In MCP-Format umwandeln
                mcp_tools = []
                for tool in tools:
                    mcp_tools.append(
                        {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": {},  # Vereinfachte Parameter
                        }
                    )

                return {"type": "tools", "tools": mcp_tools}

            elif message_type == "call_tool":
                tool_name = message.get("name")
                parameters = message.get("parameters", {})

                if tool_name == "add":
                    response = await self.client.post(
                        f"{SERVER_URL}/tools/add", json=parameters
                    )
                    result = response.json()
                    return {"type": "tool_result", "result": result}

                elif tool_name == "get_local_time":
                    response = await self.client.post(
                        f"{SERVER_URL}/tools/get_local_time", json={}
                    )
                    result = response.json()
                    return {"type": "tool_result", "result": result}

                else:
                    return {
                        "type": "error",
                        "message": f"Unbekanntes Werkzeug: {tool_name}",
                    }

            elif message_type == "list_resources":
                # Ressourcen simulieren (nur greeting)
                return {
                    "type": "resources",
                    "resources": [
                        {
                            "uri": "greeting://{name}",
                            "description": "Get a personalized greeting",
                        }
                    ],
                }

            elif message_type == "get_resource":
                uri = message.get("uri", "")

                if uri.startswith("greeting://"):
                    name = uri.replace("greeting://", "")
                    response = await self.client.get(
                        f"{SERVER_URL}/resources/greeting/{name}"
                    )
                    content = response.text

                    return {"type": "resource", "content": content}

                else:
                    return {"type": "error", "message": f"Unbekannte Ressource: {uri}"}

            else:
                return {
                    "type": "error",
                    "message": f"Unbekannter Nachrichtentyp: {message_type}",
                }

        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung der Nachricht: {e}")
            return {"type": "error", "message": f"Interner Fehler: {str(e)}"}

    async def run(self):
        """Hauptschleife für die Verarbeitung von MCP-Nachrichten"""
        logger.info("MCP-Adapter gestartet")

        try:
            # Prüfen, ob der Server erreichbar ist
            response = await self.client.get(f"{SERVER_URL}/")
            if response.status_code != 200:
                logger.error(f"Server nicht erreichbar: {response.status_code}")
                return

            logger.info(f"Server erreichbar: {response.json()}")

            # Hauptschleife
            while True:
                # Nachricht von STDIN lesen
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    logger.info("Ende der Eingabe erreicht")
                    break

                # Nachricht verarbeiten
                try:
                    message = json.loads(line)
                    logger.info(f"Nachricht empfangen: {message}")

                    # Antwort generieren
                    response = await self.handle_message(message)
                    logger.info(f"Antwort generiert: {response}")

                    # Antwort senden
                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError:
                    logger.error(f"Ungültiges JSON: {line}")
                    print(
                        json.dumps({"type": "error", "message": "Ungültiges JSON"}),
                        flush=True,
                    )

        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
        finally:
            await self.client.aclose()
            logger.info("MCP-Adapter beendet")


# Hauptfunktion
async def main():
    adapter = MCPAdapter()
    await adapter.run()


# Programm starten
if __name__ == "__main__":
    asyncio.run(main())
