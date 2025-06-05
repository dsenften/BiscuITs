#  Released under MIT License
#
#  Copyright (©) 2025. Talent Factory GmbH
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#  of the Software, and to permit persons to whom the Software is furnished to
#  do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

import streamlit as st
from streamlit_integration import mcp_chat_page, mcp_settings_page
from dotenv import load_dotenv

# Umgebungsvariablen laden
load_dotenv()

# Streamlit-Konfiguration
st.set_page_config(
    page_title="MCP-unterstützter Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Seitenzustand initialisieren
    if "page" not in st.session_state:
        st.session_state["page"] = "chat"
    
    # Seitennavigation
    st.sidebar.title("MCP Chat Client")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation:",
        options=["Chat mit MCP", "MCP-Einstellungen"],
        index=0 if st.session_state["page"] == "chat" else 1
    )
    
    # Integration mit bestehender PydanticAI-Funktionalität
    st.sidebar.markdown("---")
    st.sidebar.title("API-Optionen")
    
    # Wechsel zwischen MCP und herkömmlicher API
    api_mode = st.sidebar.radio(
        "API-Modus:",
        options=["MCP-unterstützt", "Standard PydanticAI"],
        index=0
    )
    
    # Entsprechende Seite anzeigen
    if page == "Chat mit MCP":
        st.session_state["page"] = "chat"
        if api_mode == "MCP-unterstützt":
            mcp_chat_page()
        else:
            # Hier kannst du deine bestehende PydanticAI-Implementierung aufrufen
            st.title("Standard PydanticAI Chat")
            st.info("Hier wird deine bestehende PydanticAI-Implementierung verwendet")
            # pydantic_ai_chat_page()  # Deine bestehende Funktion
    else:
        st.session_state["page"] = "settings"
        mcp_settings_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("📝 **MCP (Model Context Protocol)**")
    st.sidebar.markdown("Ermöglicht LLMs, Code und Dateien im Kontext zu verstehen")

if __name__ == "__main__":
    main()
