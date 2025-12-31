import streamlit as st
import requests

GROQ_API_KEY = "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"
headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

st.title("RE-WIRE: Scanner Modelli Attivi")

if st.button("SCANSIONA MODELLI"):
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json()['data']
            st.success("Modelli trovati!")
            for m in models:
                st.write(f"✅ ID Modello: `{m['id']}`")
        else:
            st.error(f"Errore {response.status_code}: Chiave non valida o scaduta.")
    except Exception as e:
        st.error(f"Errore: {e}")
