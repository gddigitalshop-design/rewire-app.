import streamlit as st
import requests
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. CONFIGURAZIONE (Usiamo il modello 'instant' per evitare i limiti di dimensione) ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant" # Più veloce e con limiti di traffico più alti
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONE ESTRAZIONE TESTO ---
def get_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "".join([page.get_text() for page in doc])
        # LIMITATORE DI SICUREZZA: Prende solo i primi 10.000 caratteri per evitare l'errore 413
        return text[:10000] 
    else:
        return "L'utente ha caricato un'immagine. Analizza i dati in base alla richiesta."

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")
st.info(f"Sistema Ottimizzato: {MODEL_ID}")

file = st.file_uploader("Carica Documento (PDF consigliato)", type=["pdf", "jpg", "png", "jpeg"])

if file:
    testo_documento = get_content(file)
    st.success(f"Documento pronto per l'analisi ({len(testo_documento)} caratteri acquisiti)")
    
    domanda = st.text_input("Cosa vuoi analizzare?", "Estrai i dati principali e fai un riassunto")
    
    if st.button("AVVIA ANALISI"):
        with st.spinner("L'AI sta elaborando il documento..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": MODEL_ID,
                "messages": [{
                    "role": "user", 
                    "content": f"DOCUMENTO: {testo_documento}\n\nRICHIESTA: {domanda}"
                }],
                "temperature": 0.2
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    st.markdown("### 📊 Report RE-WIRE:")
                    st.write(response.json()['choices'][0]['message']['content'])
                elif response.status_code == 413:
                    st.error("Il documento è ancora troppo grande. Prova con un file più piccolo o meno pagine.")
                else:
                    st.error(f"Errore {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Errore connessione: {e}")

with st.sidebar:
    st.caption("Versione Business 2026")
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()
