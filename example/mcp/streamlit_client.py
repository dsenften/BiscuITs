import streamlit as st
import os
from dotenv import load_dotenv
from claude_client import ClaudeClient

# Schritt 1: Konfiguration laden und Claude-Client initialisieren
load_dotenv()

# Prüfen, ob API-Key gesetzt ist
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("🔍 API-Schlüssel fehlt! Bitte erstelle eine .env-Datei mit ANTHROPIC_API_KEY.")
    st.info("Eine Beispiel-Datei .env.example ist im Projektverzeichnis verfügbar.")
    st.stop()

# Claude-Client initialisieren
if "claude_client" not in st.session_state:
    st.session_state.claude_client = ClaudeClient()

# Streamlit-Konfiguration
st.set_page_config(page_title="Claude MCP Client", layout="wide")
st.title("🧩 Claude MCP Client")

# Sidebar mit Konfiguration
st.sidebar.header("Konfiguration")

# MCP-Server-Status anzeigen
mcp_config = st.session_state.claude_client.mcp_config
server_names = list(mcp_config.get("mcpServers", {}).keys())

if not server_names:
    st.sidebar.error("Keine MCP-Server in der Konfiguration gefunden.")
else:
    st.sidebar.subheader("Verfügbare MCP-Server:")
    for server in server_names:
        st.sidebar.markdown(f"- {server}: `{mcp_config['mcpServers'][server]['url']}`")

# Verfügbare Tools anzeigen
st.sidebar.subheader("Verfügbare MCP-Tools:")
for tool in st.session_state.claude_client.mcp_tools:
    with st.sidebar.expander(f"{tool.name}"):
        st.markdown(f"**Beschreibung:** {tool.description}")
        st.markdown(f"**Server:** {tool.server}")
        st.markdown("**Parameter:**")
        for param_name, param_info in tool.parameters.items():
            st.markdown(f"- `{param_name}`: {param_info.get('description', '')}")

# Konversation zurücksetzen
if st.sidebar.button("Konversation zurücksetzen"):
    st.session_state.claude_client.clear_conversation()
    st.rerun()

# Hauptbereich: Chat-UI
st.subheader("💬 Chat mit Claude (mit MCP-Tools)")

# Chat-Verlauf anzeigen
for message in st.session_state.claude_client.get_conversation_history():
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f"**Du:** {content}")
    elif role == "assistant":
        st.markdown(f"<span style='color: #0a6cfc;'><b>Claude:</b> {content}</span>", unsafe_allow_html=True)

# Eingabefeld
user_input = st.text_input("Deine Nachricht an Claude:")

if st.button("Senden") and user_input:
    with st.spinner("Claude denkt nach..."): 
        try:
            # Anfrage an Claude senden
            response = st.session_state.claude_client.chat(user_input)
            
            # Seite neu laden, um den aktualisierten Chat-Verlauf anzuzeigen
            st.rerun()
        except Exception as e:
            st.error(f"Fehler bei der Kommunikation mit Claude: {e}")

# Hinweis zur Verwendung
st.markdown("---")
st.markdown("""
**Hinweis zur Verwendung:**

Dieser Client verbindet Claude mit MCP-Servern. Du kannst Claude bitten, die verfügbaren MCP-Tools zu verwenden, 
z.B. "Kannst du mit Playwright zu Google navigieren und einen Screenshot machen?".

Claude wird dann die entsprechenden MCP-Befehle ausführen und dir die Ergebnisse mitteilen.

Die verfügbaren Tools sind in der Seitenleiste aufgeführt.
""")

# Docker-Container stoppen (optional)
if st.sidebar.button("Docker-Container stoppen"):
    if st.sidebar.button("Bestätigen"):
        import subprocess
        try:
            subprocess.run(
                ["docker", "compose", "-f", "docker-compose.mcp.yml", "down"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                check=True
            )
            st.sidebar.success("Docker-Container erfolgreich gestoppt")
        except Exception as e:
            st.sidebar.error(f"Fehler beim Stoppen der Docker-Container: {e}")
