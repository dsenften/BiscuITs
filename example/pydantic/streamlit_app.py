import streamlit as st
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

# Initialize the agent
agent = Agent(
    model='anthropic:claude-3-5-sonnet-latest')

# Musterfrage und Musterlösung
max_punkte = 8
musterfrage = f'''
Rechnen Sie folgende Zahlen in das angegebene Zahlensystem um. 
({max_punkte} Punkte)

- 237₈ → Dezimal
- 3E9₁₆ → Dezimal
- 1011010₂ → Dezimal
- 195₁₀ → Binär

**Wichtig**: Es muss bei jeder Aufgabe der Lösungsweg und nicht nur das Resultat aufgezeigt werden.
'''

musterloesung = '''
237₈ → Dezimal
2 × 8² + 3 × 8¹ + 7 × 8⁰
= 2 × 64 + 3 × 8 + 7 × 1
= 128 + 24 + 7
= 159₁₀

3E9₁₆ → Dezimal
3 × 16² + 14 × 16¹ + 9 × 16⁰
= 3 × 256 + 14 × 16 + 9 × 1
= 768 + 224 + 9
= 1001₁₀

1011010₂ → Dezimal
1 × 2⁶ + 0 × 2⁵ + 1 × 2⁴ + 1 × 2³ + 0 × 2² + 1 × 2¹ + 0 × 2⁰
= 64 + 0 + 16 + 8 + 0 + 2 + 0
= 90₁₀

195₁₀ → Binär
195 ÷ 2 = 97 mit Rest 1
97 ÷ 2 = 48 mit Rest 1
48 ÷ 2 = 24 mit Rest 0
24 ÷ 2 = 12 mit Rest 0
12 ÷ 2 = 6 mit Rest 0
6 ÷ 2 = 3 mit Rest 0
3 ÷ 2 = 1 mit Rest 1
1 ÷ 2 = 0 mit Rest 1
= 11000011₂
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
