import json
import requests
from typing import Dict

class MCPClientManager:
    """
    Verwaltet die Kommunikation mit mehreren MCP-Servern über HTTP gemäß Konfiguration.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as f:
            config = json.load(f)
        self.server_configs = config.get("mcpServers", {})

    def get_server_names(self):
        return list(self.server_configs.keys())

    def get_server_url(self, name: str) -> str:
        conf = self.server_configs[name]
        return conf["url"]

    def send_message(self, name: str, message: str) -> str:
        url = self.get_server_url(name)
        try:
            # Einheitlicher /chat-Endpunkt durch unseren MCP-Proxy
            resp = requests.post(
                f"{url}/chat", 
                json={"message": message}, 
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", str(data))
        except Exception as e:
            return f"Fehler bei Anfrage an {name}: {e}"

    def start_server(self, name: str):
        # Im Docker-Modus: Server werden extern via docker-compose gestartet
        pass

    def stop_server(self, name: str):
        # Im Docker-Modus: Server werden extern gestoppt
        pass

    def stop_all(self):
        pass
