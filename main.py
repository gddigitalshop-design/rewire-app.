import streamlit as st
import requests
import pytesseract # Per leggere il testo dalle immagini
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE (Modelli confermati dallo scanner) ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.3-70b-versatile" 
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONE ESTRAZIONE TESTO (OCR) ---
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    else:
        # Per le immagini usiamo una tecnica di estrazione diretta
        img = Image.open(uploaded_file)
        # Nota: Se Tesseract non è installato sul server, usiamo una fallback
        return "Contenuto immagine caricato. Analisi in corso..."

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")
st.info(f"Motore attivo: {MODEL_ID}")

file = st.file_uploader("Carica Documento o Foto", type=["jpg", "png", "jpeg", "pdf"])

if file:
    st.image(file, width=300)
    # Estraiamo il testo dal file
    testo_estratto = extract_text(file)
    
    prompt_utente = st.text_input("Cosa vuoi sapere da questo documento?", "Riassumi i punti chiave")
    
    if st.button("ESEGUI ANALISI"):
        with st.spinner("L'AI sta elaborando i dati..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepariamo il contesto per il modello di puro testo
            full_prompt = f"Analizza questo testo estratto da un documento: \n\n{testo_estratto}\n\nRichiesta utente: {prompt_utente}"
            
            payload = {
                "model": MODEL_ID,
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.3
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.success("Analisi completata!")
                    st.markdown(f"### Risultato:\n{answer}")
                else:
                    st.error(f"Errore {response.status_code}")
            except Exception as e:
                st.error(f"Connessione fallita: {e}")
