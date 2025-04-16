## Beschreibung von agent.py

Dieses Beispielprogramm demonstriert den Einsatz eines KI-Agenten mit der Bibliothek `pydantic_ai` und der API von Anthropic (Claude 3.5 Sonnet).

**Funktionen und Ablauf:**

1. **Umgebungsvariablen laden:** Mit `dotenv` werden Umgebungsvariablen wie z.B. API-Schlüssel geladen.
2. **Logging konfigurieren:** Die Bibliothek `logfire` wird mit einem Token aus den Umgebungsvariablen konfiguriert, um Logs zu ermöglichen.
3. **Agent initialisieren:** Ein `Agent`-Objekt wird erstellt, das auf das Modell `anthropic:claude-3-5-sonnet-latest` zugreift.
4. **Interaktive Konversation:** Im asynchronen Hauptprogramm wird eine Unterhaltung mit dem Agenten geführt. Zuerst wird eine Begrüßung gesendet, dann kann der Benutzer beliebig viele Nachrichten eingeben und erhält jeweils eine Antwort vom KI-Agenten. Die Nachrichtenhistorie bleibt dabei erhalten.

Das Skript eignet sich als Vorlage für eigene Chatbots oder KI-gestützte Anwendungen mit Pydantic und Anthropic.


## Fetch MCP Server

URL: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch

Ein Model Context Protocol-Server, der Funktionen zum Abrufen von Webinhalten 
bietet. Dieser Server ermöglicht es LLMs, Inhalte von Webseiten abzurufen 
und zu verarbeiten, wobei HTML zur einfacheren Nutzung in Markdown konvertiert 
wird.

Das Fetch-Tool schneidet die Antwort ab, aber mit dem start_index-Argument 
können Sie angeben, wo die Extraktion des Inhalts beginnen soll. 
Auf diese Weise können die Modelle eine Webseite in Stücken lesen, 
bis sie die benötigten Informationen finden.

