import asyncio

import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# Initialize the agent
agent = Agent(model="anthropic:claude-3-5-sonnet-latest")

# Musterfrage und Musterlösung
max_punkte = 6
musterfrage = f"""
In einem Computer mit 8-Bit-Worten werden negative Zahlen im Zweierkomplement dargestellt. Geben Sie die Bitmuster 
für folgende dezimale Zahlen an:

({max_punkte} Punkte)

1.   -5₁₀
2. -128₁₀
3.  127₁₀
"""

musterloesung = """
1.  -5₁₀ 
    - Positive Zahl: 5₁₀ = 00000101₂
    - Invertieren: 11111010₂ + 1 
    - Ergebnis: 11111011₂
2. -128₁₀
    - -128 ist der kleinste darstellbare 8-Bit-Wert im Zweierkomplement
    - Direkt: 10000000₂
3. 127₁₀
    - 127 ist der grösste darstellbare positive 8-Bit-Wert im Zweierkomplement
    - Direkt: 01111111₂
    
Zumindest bei der ersten Aufgabe muss gezeigt werden, wie das 2er-Komplement gerechnet wird.
"""

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
