import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configurazione
genai.configure(api_key="AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc")

# Invece di scrivere il nome, chiediamo a Google quali modelli HAI ATTIVI
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Scegliamo il primo della lista che Google ci dà come "buono"
    model_to_use = models[0] if models else "gemini-1.5-flash"
except:
    model_to_use = "gemini-1.5-flash"

model = genai.GenerativeModel(model_to_use)

st.title("RE-WIRE AI - Test Finale")
st.write(f"Modello rilevato: {model_to_use}")

file = st.file_uploader("Carica immagine")
if file and st.button("Analizza"):
    img = Image.open(file)
    try:
        response = model.generate_content(["Cosa vedi?", img])
        st.success(response.text)
    except Exception as e:
        st.error(f"Ancora errore: {e}")
