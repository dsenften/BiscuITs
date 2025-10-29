"""
Claude-Client für MCP-Integration mit PydanticAI
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Konfiguration laden
load_dotenv()
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Anthropic API-Schlüssel
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.warning(
        "ANTHROPIC_API_KEY nicht gesetzt. Claude-Integration wird nicht funktionieren."
    )

# MCP-Konfigurationspfad
MCP_CONFIG_PATH = os.getenv("MCP_CONFIG_PATH", "mcp_config.json")


# Modelle für PydanticAI
class MCPRequest(BaseModel):
    """Anfrage an einen MCP-Server"""

    server_name: str = Field(
        ..., description="Name des MCP-Servers (z.B. puppeteer, playwright)"
    )
    action: str = Field(
        ...,
        description="Aktion, die ausgeführt werden soll (z.B. navigate, screenshot)",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameter für die Aktion"
    )


class MCPResponse(BaseModel):
    """Antwort von einem MCP-Server"""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class MCPTool(BaseModel):
    """Beschreibung eines MCP-Tools"""

    name: str
    description: str
    server: str
    parameters: Dict[str, Dict[str, Any]]


class ChatMessage(BaseModel):
    """Chat-Nachricht"""

    role: str
    content: str


class ClaudeClient:
    """Client für die Kommunikation mit Claude und MCP-Servern"""

    def __init__(self):
        """Initialisiert den Claude-Client"""
        self.anthropic = (
            Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        )
        self.mcp_config = self._load_mcp_config()
        self.mcp_tools = self._prepare_mcp_tools()
        self.conversation_history: List[ChatMessage] = []

    def _load_mcp_config(self) -> Dict:
        """Lädt die MCP-Konfiguration aus der Datei"""
        try:
            with open(MCP_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der MCP-Konfiguration: {e}")
            return {"mcpServers": {}}

    def _prepare_mcp_tools(self) -> List[MCPTool]:
        """Bereitet die MCP-Tools für Claude vor"""
        tools = []
        for server_name, config in self.mcp_config.get("mcpServers", {}).items():
            # Hier würden wir normalerweise die verfügbaren Aktionen vom Server abfragen
            # Für dieses Beispiel definieren wir einige Standard-Aktionen
            if "puppeteer" in server_name:
                tools.append(
                    MCPTool(
                        name="puppeteer_navigate",
                        description="Navigiere zu einer URL im Browser",
                        server=server_name,
                        parameters={
                            "url": {
                                "type": "string",
                                "description": "URL, zu der navigiert werden soll",
                            }
                        },
                    )
                )
                tools.append(
                    MCPTool(
                        name="puppeteer_screenshot",
                        description="Mache einen Screenshot der aktuellen Seite",
                        server=server_name,
                        parameters={
                            "name": {
                                "type": "string",
                                "description": "Name für den Screenshot",
                            }
                        },
                    )
                )
            elif "playwright" in server_name:
                tools.append(
                    MCPTool(
                        name="playwright_navigate",
                        description="Navigiere zu einer URL im Browser",
                        server=server_name,
                        parameters={
                            "url": {
                                "type": "string",
                                "description": "URL, zu der navigiert werden soll",
                            }
                        },
                    )
                )
                tools.append(
                    MCPTool(
                        name="playwright_screenshot",
                        description="Mache einen Screenshot der aktuellen Seite",
                        server=server_name,
                        parameters={
                            "name": {
                                "type": "string",
                                "description": "Name für den Screenshot",
                            }
                        },
                    )
                )
            elif "sequential-thinking" in server_name:
                tools.append(
                    MCPTool(
                        name="sequential_thinking",
                        description="Führe sequentielles Denken durch",
                        server=server_name,
                        parameters={
                            "problem": {
                                "type": "string",
                                "description": "Problem, das gelöst werden soll",
                            }
                        },
                    )
                )
        return tools

    def execute_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Führt eine MCP-Anfrage aus"""
        server_name = request.server_name
        if server_name not in self.mcp_config.get("mcpServers", {}):
            logger.error(f"MCP-Server '{server_name}' nicht gefunden")
            return MCPResponse(
                success=False, error=f"MCP-Server '{server_name}' nicht gefunden"
            )

        server_url = self.mcp_config["mcpServers"][server_name].get("url")
        if not server_url:
            logger.error(f"Keine URL für MCP-Server '{server_name}' konfiguriert")
            return MCPResponse(
                success=False,
                error=f"Keine URL für MCP-Server '{server_name}' konfiguriert",
            )

        try:
            # Anfrage an den MCP-Server senden
            # Sende die Anfrage direkt im Format, das der MCP-Server erwartet
            # Hier verwenden wir das Format, das in der mcp-proxy.js erwartet wird

            # Erstelle die Anfrage im Format, das der MCP-Proxy erwartet
            request_payload = {
                "message": json.dumps(
                    {"name": request.action, "parameters": request.parameters}
                )
            }

            # Debug-Ausgabe der Anfrage
            logger.info(f"Sende Anfrage an MCP-Server {server_name} ({server_url}):")
            logger.info(f"Aktion: {request.action}")
            logger.info(f"Parameter: {request.parameters}")
            logger.info(f"Payload: {request_payload}")

            # Anfrage senden
            response = requests.post(
                f"{server_url}/chat", json=request_payload, timeout=30
            )

            # Debug-Ausgabe der Antwort
            logger.info(f"Antwort vom MCP-Server {server_name} erhalten:")
            logger.info(f"Status-Code: {response.status_code}")
            logger.info(f"Antwort: {response.text}")

            response.raise_for_status()
            return MCPResponse(success=True, data=response.json())
        except Exception as e:
            logger.error(f"Fehler bei MCP-Anfrage an {server_name}: {e}")
            return MCPResponse(success=False, error=str(e))

    def chat(self, message: str) -> str:
        """Chat mit Claude, mit MCP-Integration"""
        if not self.anthropic:
            return "Claude-Integration ist nicht konfiguriert. Bitte setze ANTHROPIC_API_KEY in der .env-Datei."

        # Nachricht zur Konversationshistorie hinzufügen
        self.conversation_history.append(ChatMessage(role="user", content=message))

        # System-Prompt mit MCP-Tool-Beschreibungen
        system_prompt = """
        Du bist Claude, ein KI-Assistent, der mit Model Context Protocol (MCP) Servern kommunizieren kann.
        Du kannst folgende MCP-Tools verwenden:
        """

        for tool in self.mcp_tools:
            system_prompt += f"\n- {tool.name}: {tool.description}"
            system_prompt += f"\n  Server: {tool.server}"
            system_prompt += "\n  Parameter:"
            for param_name, param_info in tool.parameters.items():
                system_prompt += (
                    f"\n    - {param_name}: {param_info.get('description', '')}"
                )

        system_prompt += """
        
        Wenn du ein MCP-Tool verwenden möchtest, antworte mit einem JSON-Objekt im folgenden Format:
        ```json
        {
          "mcp_request": {
            "server_name": "name_des_servers",
            "action": "name_der_aktion",
            "parameters": {
              "param1": "wert1",
              "param2": "wert2"
            }
          }
        }
        ```
        
        Ich werde dann die Anfrage an den entsprechenden MCP-Server weiterleiten und dir die Antwort mitteilen.
        """

        # Konversationshistorie in Anthropic-Format umwandeln
        messages = []
        for msg in self.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Aktuelle Nachricht hinzufügen
        messages.append({"role": "user", "content": message})
        self.conversation_history.append(ChatMessage(role="user", content=message))

        # Anfrage an Claude senden
        response = self.anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            system=system_prompt,
            messages=messages,
        )

        claude_response = response.content[0].text

        # Prüfen, ob Claude eine oder mehrere MCP-Anfragen stellen möchte
        try:
            # Nach allen JSON-Objekten in der Antwort suchen
            all_mcp_requests = []
            current_pos = 0

            while True:
                json_start = claude_response.find("```json", current_pos)
                if json_start == -1:
                    break

                json_start += 7  # Länge von "```json"
                json_end = claude_response.find("```", json_start)
                if json_end == -1:
                    break

                json_str = claude_response[json_start:json_end].strip()
                current_pos = (
                    json_end + 3
                )  # Nach dem Ende dieses JSON-Blocks fortsetzen

                try:
                    # JSON parsen
                    data = json.loads(json_str)

                    # Prüfen, ob es sich um eine MCP-Anfrage handelt
                    if "mcp_request" in data:
                        all_mcp_requests.append(data["mcp_request"])
                except json.JSONDecodeError:
                    logger.warning(f"Ungültiges JSON gefunden: {json_str}")

            # Wenn MCP-Anfragen gefunden wurden, diese nacheinander ausführen
            if all_mcp_requests:
                # Antwort zur Konversationshistorie hinzufügen
                self.conversation_history.append(
                    ChatMessage(role="assistant", content=claude_response)
                )

                # Alle MCP-Anfragen nacheinander ausführen und die Ergebnisse sammeln
                all_results = []

                for i, mcp_request_data in enumerate(all_mcp_requests):
                    # Extrahiere die Daten aus der Anfrage
                    server_name = mcp_request_data["server_name"]
                    action = mcp_request_data["action"]
                    parameters = mcp_request_data.get("parameters", {})

                    # Korrigiere die Aktion, um sicherzustellen, dass sie mit den definierten Tool-Namen übereinstimmt
                    if server_name == "playwright":
                        if action == "navigate":
                            action = "playwright_navigate"
                        elif action == "screenshot":
                            action = "playwright_screenshot"
                    elif server_name == "puppeteer":
                        if action == "navigate":
                            action = "puppeteer_navigate"
                        elif action == "screenshot":
                            action = "puppeteer_screenshot"
                    elif server_name == "sequential-thinking":
                        action = "sequential_thinking"

                    # Erstelle die MCP-Anfrage mit der korrigierten Aktion
                    mcp_request = MCPRequest(
                        server_name=server_name, action=action, parameters=parameters
                    )

                    # MCP-Anfrage ausführen
                    mcp_response = self.execute_mcp_request(mcp_request)
                    all_results.append(mcp_response)

                    # Informationen über diese Anfrage für die Protokollierung
                    logger.info(
                        f"MCP-Anfrage {i+1}/{len(all_mcp_requests)}: {action} auf {server_name}"
                    )

                # Alle Ergebnisse zusammenfassen und an Claude senden
                mcp_result_msg = "Ergebnisse der MCP-Anfragen:\n"
                for i, result in enumerate(all_results):
                    mcp_result_msg += f"\nAnfrage {i+1}/{len(all_results)}:\n```json\n{json.dumps(result.dict(), indent=2)}\n```\n"

                # Neue Anfrage an Claude senden
                updated_messages = messages.copy()
                updated_messages.append(
                    {"role": "assistant", "content": claude_response}
                )
                updated_messages.append({"role": "user", "content": mcp_result_msg})

                follow_up_response = self.anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=updated_messages,
                )

                final_response = follow_up_response.content[0].text
                self.conversation_history.append(
                    ChatMessage(role="assistant", content=final_response)
                )
                return final_response
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung der MCP-Anfrage: {e}")

        # Wenn keine MCP-Anfrage oder ein Fehler auftritt, normale Antwort zurückgeben
        self.conversation_history.append(
            ChatMessage(role="assistant", content=claude_response)
        )
        return claude_response

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Gibt die Konversationshistorie zurück"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]

    def clear_conversation(self):
        """Löscht die Konversationshistorie"""
        self.conversation_history = []
