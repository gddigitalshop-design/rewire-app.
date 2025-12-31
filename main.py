import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business AI", layout="wide", page_icon="💾")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "file_processed" not in st.session_state: st.session_state.file_processed = False

# --- FUNZIONE ANALISI ---
def auto_analyze(text):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Sei un analista esperto. Riassumi i dati principali del documento."},
            {"role": "user", "content": f"Documento: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Errore nell'analisi AI."

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Caricamento (PDF o FOTO)")
    file = st.file_uploader("Trascina qui il file", type=["pdf", "jpg", "jpeg", "png"])
    
    if file and not st.session_state.file_processed:
        with st.spinner("Analisi in corso..."):
            if file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([page.get_text() for page in doc])[:4000]
            else:
                # Se è una FOTO, informiamo l'AI che è un'immagine (l'analisi avanzata richiederebbe Tesseract)
                st.session_state.doc_text = f"L'utente ha caricato una foto denominata {file.name}. Analizza le richieste dell'utente."
            
            summary = auto_analyze(st.session_state.doc_text)
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.session_state.file_processed = True
            st.rerun()

    if st.button("🗑️ Carica Nuovo File"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- AREA SALVATAGGIO (Migliorata) ---
if st.session_state.messages:
    # Creiamo il file di testo in memoria per il download
    report_text = "--- REPORT RE-WIRE ---\n\n"
    for m in st.session_state.messages:
        report_text += f"{m['role'].upper()}: {m['content']}\n\n"
    
    # Pulsante di salvataggio ultra-stabile
    st.download_button(
        label="📥 SALVA LAVORO (Download Report)",
        data=report_text,
        file_name="Analisi_Business.txt",
        mime="text/plain",
        help="Clicca qui per salvare tutta la chat e l'analisi sul tuo dispositivo"
    )
    st.divider()

# Visualizzazione chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interattiva
if prompt := st.chat_input("Chiedi dettagli sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Contesto: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        res = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = res.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
