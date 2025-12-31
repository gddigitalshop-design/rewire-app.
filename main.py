import streamlit as st
import requests
import fitz  # PyMuPDF (già incluso nel file requirements)
from PIL import Image
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.3-70b-versatile" 
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- ESTRAZIONE TESTO (Metodo Stabile) ---
def get_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        # Estrae testo dai PDF in modo nativo
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        # Per le immagini, l'AI analizzerà la richiesta basandosi sul file caricato
        return "[Immagine Caricata]"

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")
st.info(f"Motore AI Attivo: {MODEL_ID}")

file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "jpg", "png", "jpeg"])

if file:
    st.success("File caricato correttamente!")
    testo_documento = get_content(file)
    
    domanda = st.text_input("Cosa vuoi sapere?", "Fai un riassunto professionale dei dati")
    
    if st.button("ANALIZZA CON RE-WIRE"):
        with st.spinner("Elaborazione dati in corso..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepariamo il messaggio per il modello di puro testo (Llama 3.3)
            payload = {
                "model": MODEL_ID,
                "messages": [{
                    "role": "user", 
                    "content": f"Documento fornito: {testo_documento}\n\nRichiesta utente: {domanda}"
                }],
                "temperature": 0.2
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    st.markdown("### 📊 Risultato Analisi:")
                    st.write(response.json()['choices'][0]['message']['content'])
                else:
                    st.error(f"Errore API {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Errore di connessione: {e}")

with st.sidebar:
    st.divider()
    if st.button("Esci dal sistema"):
        st.session_state.auth = False
        st.rerun()
