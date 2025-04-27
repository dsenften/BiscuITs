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
Wie funktioniert das Fork- und Exec-Modell in UNIX/MINIX 3 zur Prozesserstellung? Beschreiben Sie den Ablauf bei der 
Erstellung eines neuen Prozesses und erklären Sie, warum dieser Ansatz für Shell-Pipelines besonders vorteilhaft ist. 
({max_punkte} Punkte)
'''

musterloesung = '''
Das Fork- und Exec-Modell in UNIX/MINIX 3 teilt die Prozesserstellung in zwei separate Schritte:

1. Fork: Der fork()-Systemaufruf erstellt eine exakte Kopie des aufrufenden Prozesses (Elternprozess). 
Der neue Prozess (Kindprozess) erhält eine Kopie des Adressraums des Elternprozesses mit identischem Code, 
Daten, Stack, offenen Dateien und Umgebungsvariablen. Nach dem Fork gibt es zwei fast identische Prozesse, 
die unabhängig voneinander ausgeführt werden. Der Unterschied besteht darin, dass fork() im Elternprozess 
die Prozess-ID des Kindes zurückgibt, während im Kindprozess der Rückgabewert 0 ist.

2. Exec: Nach dem Fork kann der Kindprozess den execve()-Systemaufruf (oder eine der Varianten wie execl, execlp, 
execv, etc.) verwenden, um sein Speicherabbild durch ein neues Programm zu ersetzen. Der exec-Aufruf lädt eine 
ausführbare Datei in den Adressraum des Prozesses und beginnt mit deren Ausführung. Die Prozess-ID bleibt dabei 
erhalten.

Dieser Ablauf ist für Shell-Pipelines besonders vorteilhaft aus folgenden Gründen:

- Zwischen Fork und Exec kann der Kindprozess seine Umgebung modifizieren, insbesondere seine Standardein- und 
-ausgabe umleiten. Dies ist entscheidend für Pipelines, bei denen die Ausgabe eines Programms zur Eingabe eines anderen 
wird. 

- Der Elternprozess (die Shell) kann nach dem Fork weiterhin ausgeführt werden und auf die Beendigung des Kindes 
warten oder weitere Kinder erzeugen, um komplexe Pipelines zu bauen.

- Für eine Pipeline wie `cmd1 | cmd2` kann die Shell:
  1. Einen Pipe-Systemaufruf machen, um zwei verbundene Dateideskriptoren zu erstellen
  2. Forken und im ersten Kind die Standardausgabe auf das Schreibende der Pipe umleiten, dann exec für cmd1 ausführen
  3. Erneut forken und im zweiten Kind die Standardeingabe auf das Lesende der Pipe umleiten, dann exec für cmd2 ausführen

Diese Flexibilität bei der Dateideskriptor-Manipulation zwischen Fork und Exec ermöglicht die einfache Konstruktion
beliebig komplexer Pipelines und Umleitungen und ist ein Hauptgrund für die Leistungsfähigkeit und Eleganz der UNIX-Shell.
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
