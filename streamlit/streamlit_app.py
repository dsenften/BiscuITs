import streamlit as st
import requests
import time

MICROSERVICE1_URL = "http://microservice1:5000"

st.title("KI-gestützte Microservice-Architektur")
st.write("Bitte gib deinen Namen und deine Adresse ein:")

with st.form(key='input_form'):
    name = st.text_input("Name")
    plz = st.text_input("PLZ")
    ort = st.text_input("Ort")
    submit_button = st.form_submit_button(label='Absenden')

if submit_button:
    address = {"plz": plz, "ort": ort}
    payload = {"name": name, "address": address}
    try:
        response = requests.post(f"{MICROSERVICE1_URL}/submit", json=payload)
        if response.status_code != 202:
            st.error("Fehler beim Absenden der Anfrage!")
        else:
            correlation_id = response.json().get("correlation_id")
            st.success("Anfrage gesendet. Warte auf Antwort...")

            # Polling-Schleife, bis das Ergebnis verfügbar ist
            result = None
            with st.spinner("Bitte warten..."):
                for _ in range(30):  # maximal 30 Versuche (ca. 30*2 Sekunden)
                    time.sleep(2)
                    res = requests.get(f"{MICROSERVICE1_URL}/result/{correlation_id}")
                    if res.status_code == 200:
                        result = res.json().get("result")
                        break
            if result:
                st.success("Antwort erhalten!")
                st.write(result)
            else:
                st.error("Keine Antwort erhalten. Bitte später erneut versuchen.")
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
