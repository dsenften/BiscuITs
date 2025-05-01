#!/bin/bash
# Aktiviere Poetry Environment
eval $(poetry env activate)

# Starte die Streamlit App
streamlit run app.py
