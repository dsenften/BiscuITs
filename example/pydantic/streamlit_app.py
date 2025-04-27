import streamlit as st
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# Initialize the agent
agent = Agent(
    model='anthropic:claude-3-5-sonnet-latest')

# Musterfrage und Musterlösung
max_punkte = 6
musterfrage = f'''
Erklären Sie den Unterschied zwischen dem Einerkomplement und dem Zweierkomplement bei der Darstellung negativer Zahlen. 
Welche Vorteile bietet das Zweierkomplement, die dazu geführt haben, dass es in modernen Computern universell 
eingesetzt wird?  
({max_punkte} Punkte)
'''

musterloesung = '''
Einerkomplement (Ones' Complement):
Beim Einerkomplement wird eine negative Zahl dargestellt, indem alle Bits der entsprechenden positiven Zahl invertiert 
werden (0 wird zu 1 und 1 wird zu 0). Beispielsweise wird für eine 8-Bit-Darstellung die Zahl +5 (00000101) zu -5 im 
Einerkomplement (11111010).

Zweierkomplement (Two's Complement):
Im Zweierkomplement wird eine negative Zahl durch Invertieren aller Bits der positiven Zahl und anschliessendes 
Addieren von 1 dargestellt. Für das obige Beispiel: +5 (00000101) wird zu -5 im Zweierkomplement durch Invertieren 
(11111010) und Addieren von 1, was 11111011 ergibt. Vorteile des Zweierkomplements, die zu seiner universellen 
Verwendung geführt haben:

Einheitliche Arithmetik: Die Addition und Subtraktion funktionieren mit dem gleichen Hardware-Schaltkreis für 
positive und negative Zahlen ohne spezielle Behandlung. Im Einerkomplement muss ein End-Around-Carry bei der 
Addition berücksichtigt werden.

Eindeutige Darstellung der Null: Im Zweierkomplement gibt es nur eine Darstellung für Null (00000000), während im 
Einerkomplement zwei Darstellungen existieren (+0 als 00000000 und -0 als 11111111), was zu Komplikationen führen kann.

Grösserer Wertebereich: Für n Bits kann das Zweierkomplement Werte von -2^(n-1) bis +2^(n-1)-1 darstellen, während 
das Einerkomplement nur Werte von -(2^(n-1)-1) bis +(2^(n-1)-1) darstellen kann.

Effizientere Hardware-Implementierung: Die Erzeugung des Zweierkomplements kann mit einfachen digitalen Schaltkreisen 
realisiert werden und erfordert weniger spezielle Fallbehandlungen.

Keine Überläufe bei Umwandlungen: Die Umwandlung zwischen positiven und negativen Zahlen verursacht im Zweierkomplement 
keine Überläufe, was die Implementierung von arithmetischen Operationen vereinfacht.

Diese Vorteile, insbesondere die einheitliche Arithmetik und die eindeutige Null-Darstellung, haben dazu geführt, 
dass das Zweierkomplement in praktisch allen modernen Computern für die Darstellung von Ganzzahlen mit Vorzeichen 
verwendet wird.
'''

st.title("KI-gestützte Bewertung von Prüfungsantworten")
st.markdown("**Musterfrage:**")
st.info(musterfrage)

st.markdown("**Musterlösung:**")
st.success(musterloesung)

st.markdown("---")
st.markdown("**Antwort eines Studierenden eingeben:**")
user_input = st.text_area("Antwort", height=200)

if st.button("Bewerten lassen"):
    if user_input.strip() == "":
        st.warning("Bitte eine Antwort eingeben.")
    else:
        prompt = f"""
Basierend auf meinem Script habe ich den Studierenden folgende Frage gestellt: \n\n{musterfrage}\n\n---\n\n Die Musterlösung für diese Frage lautet:\n\n{musterloesung}\n\n---\n\nIch werde dir im Anschluss die Lösungen meiner Studierenden präsentieren. Bitte erstelle eine Bewertung (maximal {max_punkte} Punkte) dieser Arbeiten mit entsprechenden Begründungen.\n\nHier ist die Antwort eines Studierenden:\n\n{user_input}\n\nBitte bewerte diese Antwort (maximal 6 Punkte) und gib eine kurze Begründung für die Punktevergabe.\n"""


        async def evaluate():
            result = await agent.run(prompt)
            return result.data


        # Streamlit unterstützt keine direkten async calls, daher Workaround:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        with st.spinner("Bewertung wird von der KI erstellt..."):
            bewertung = loop.run_until_complete(evaluate())
        st.markdown("**Bewertung der KI:**")
        st.info(bewertung)
