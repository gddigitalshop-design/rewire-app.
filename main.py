import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configurazione API
API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=API_KEY)

st.title("🧠 RE-WIRE Business AI")

# Login rapido
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# Caricamento e Analisi
file = st.file_uploader("Carica un documento (Immagine)", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, width=300)
    
    if st.button("Analizza Documento"):
        try:
            # Usiamo il modello Flash che è il più veloce
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(["Cosa vedi in questa immagine? Riassumi per un'azienda.", img])
            st.success(response.text)
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
