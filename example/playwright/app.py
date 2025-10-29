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

import base64
import json
import os

#  Released under MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#  of the Software, and to permit persons to whom the Software is furnished to
#  do so, subject to the following conditions:
#
#
# app.py
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API-Key setzen
client = OpenAI(api_key=OPENAI_API_KEY)

# Seitentitel
st.set_page_config(page_title="LLM Playwright Chatbot", page_icon="🤖")
st.title("LLM Playwright Chatbot")
st.subheader("Stellen Sie Fragen oder geben Sie Anweisungen zur Webautomatisierung")

# Session States initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hallo! Ich bin dein Web-Automatisierungs-Assistent. Was möchtest du tun?",
        }
    ]

if "last_screenshot" not in st.session_state:
    st.session_state.last_screenshot = None


# Funktion zum Ausführen von Playwright-Aktionen
def run_playwright_action(action, params=None):
    if params is None:
        params = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            result = None
            # Aktion basierend auf dem Befehl ausführen
            if action == "navigate":
                url = params.get("url", "https://www.google.com")
                page.goto(url)
                result = {"success": True, "message": f"Navigiert zu {url}"}
            elif action == "get_title":
                result = {"success": True, "title": page.title()}
            elif action == "get_text":
                selector = params.get("selector")
                if selector:
                    text = page.text_content(selector)
                    result = {"success": True, "text": text}
                else:
                    result = {"success": False, "error": "Selector fehlt"}
            elif action == "screenshot":
                screenshot_bytes = page.screenshot(full_page=True)
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                result = {"success": True, "data": screenshot_base64}
            elif action == "click":
                selector = params.get("selector")
                if selector:
                    page.click(selector)
                    result = {"success": True, "message": f"Geklickt auf {selector}"}
                else:
                    result = {"success": False, "error": "Selector fehlt"}
            elif action == "fill":
                selector = params.get("selector")
                value = params.get("value")
                if selector and value:
                    page.fill(selector, value)
                    result = {
                        "success": True,
                        "message": f"Formular {selector} ausgefüllt mit '{value}'",
                    }
                else:
                    result = {"success": False, "error": "Selector oder Wert fehlt"}
            else:
                result = {"success": False, "error": "Unbekannte Aktion"}
            context.close()
            browser.close()
            return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# Funktion zum Aufrufen des LLM
def call_llm(user_message, messages_history):
    try:
        # Systemanweisung für das LLM
        system_message = """Du bist ein hilfreicher Assistent, der mit Playwright-Automatisierung arbeitet.
        
        Wenn der Benutzer eine Web-Automatisierungsaufgabe beschreibt, analysiere die Anfrage und gib eine der folgenden Anweisungen in deiner Antwort an:
        
        - Für Navigation: [PLAYWRIGHT_ACTION:navigate,{"url":"https://example.com"}]
        - Für Screenshots: [PLAYWRIGHT_ACTION:screenshot]
        - Für Titel abrufen: [PLAYWRIGHT_ACTION:get_title]
        - Für Text abrufen: [PLAYWRIGHT_ACTION:get_text,{"selector":".example-class"}]
        - Für Klicken: [PLAYWRIGHT_ACTION:click,{"selector":"button.submit"}]
        - Für Formulare ausfüllen: [PLAYWRIGHT_ACTION:fill,{"selector":"input#search","value":"Suchbegriff"}]
        
        Erkläre auch in natürlicher Sprache, was du tust."""

        # LLM-Anfrage senden
        messages = [{"role": "system", "content": system_message}]

        # Füge Konversationsverlauf hinzu
        for msg in messages_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Neue Benutzernachricht hinzufügen
        messages.append({"role": "user", "content": user_message})

        # API-Anfrage
        response = client.chat.completions.create(
            model="gpt-4",  # oder ein anderes verfügbares Modell
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Fehler bei der Anfrage an das LLM: {str(e)}"


# Chat-Historie anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Zeige Screenshot an, wenn vorhanden
        if message.get("screenshot"):
            st.image(message["screenshot"], caption="Screenshot", use_column_width=True)

# Benutzereingabe
if prompt := st.chat_input("Gib deine Nachricht ein..."):
    # Neue Benutzereingabe zur Chat-Historie hinzufügen
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Benutzernachricht anzeigen
    with st.chat_message("user"):
        st.write(prompt)

    # Antwort generieren
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("Denke nach...")

        # LLM aufrufen
        llm_response = call_llm(prompt, st.session_state.messages)

        # Nach Playwright-Aktionen in der Antwort suchen
        import re

        # Finde alle Aktionen in der LLM-Antwort
        action_matches = list(
            re.finditer(r"\[PLAYWRIGHT_ACTION:(\w+)(?:,\s*(\{.*?\}))?\]", llm_response)
        )

        if action_matches:
            last_action_result = None
            last_action = None
            last_action_name = None
            last_action_params = None
            for match in action_matches:
                action = match.group(1)
                params_str = match.group(2) if match.group(2) else "{}"
                try:
                    params = json.loads(params_str)
                    with st.spinner(f"Führe Playwright-Aktion '{action}' aus..."):
                        action_result = run_playwright_action(action, params)
                    last_action_result = action_result
                    last_action = match
                    last_action_name = action
                    last_action_params = params
                except json.JSONDecodeError:
                    message_placeholder.write(
                        f"{llm_response}\n\n⚠️ Fehler beim Parsen der Parameter für die Playwright-Aktion."
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": f"{llm_response}\n\n⚠️ Fehler beim Parsen der Parameter für die Playwright-Aktion.",
                        }
                    )
                    break
                except Exception as e:
                    error_msg = f"⚠️ Unerwarteter Fehler bei der Ausführung der Playwright-Aktion: {str(e)}"
                    message_placeholder.write(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                    break
            # Nach der letzten Aktion: Antwort aktualisieren
            if last_action_result and last_action_result.get("success", False):
                clean_response = re.sub(
                    r"\[PLAYWRIGHT_ACTION:(\w+)(?:,\s*(\{.*?\}))?\]",
                    lambda m: f"Aktion '{m.group(1)}' erfolgreich ausgeführt!",
                    llm_response,
                )
                if last_action_name == "get_title" and "title" in last_action_result:
                    clean_response += f"\n\nDer Titel der Seite ist: **{last_action_result['title']}**"
                elif last_action_name == "get_text" and "text" in last_action_result:
                    clean_response += f"\n\nText-Inhalt: {last_action_result['text']}"
                new_assistant_message = {"role": "assistant", "content": clean_response}
                if "data" in last_action_result and last_action_result.get("data"):
                    image_data = f"data:image/png;base64,{last_action_result['data']}"
                    st.image(image_data, caption="Screenshot", use_column_width=True)
                    new_assistant_message["screenshot"] = image_data
                st.session_state.messages.append(new_assistant_message)
            else:
                error_message = (
                    last_action_result.get("error", "Unbekannter Fehler")
                    if last_action_result
                    else "Unbekannter Fehler"
                )
                message_placeholder.write(
                    f"{llm_response}\n\n⚠️ Fehler bei der Ausführung: {error_message}"
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"{llm_response}\n\n⚠️ Fehler bei der Ausführung: {error_message}",
                    }
                )
        else:
            # LLM-Antwort ohne Playwright-Aktion anzeigen
            message_placeholder.write(llm_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": llm_response}
            )

# Sidebar-Optionen
st.sidebar.header("Optionen")

# Chat löschen Button
if st.sidebar.button("Chat zurücksetzen"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hallo! Ich bin dein Web-Automatisierungs-Assistent. Was möchtest du tun?",
        }
    ]
    st.session_state.last_screenshot = None
    st.experimental_rerun()

# Hinweise hinzufügen
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
### Beispielbefehle:
- "Öffne die Website example.com"
- "Mache einen Screenshot von google.com"
- "Wie lautet der Titel der Seite github.com?"
- "Klicke auf den Login-Button auf example.com"
- "Fülle das Suchfeld auf google.com mit 'Playwright Python' aus"
"""
)
