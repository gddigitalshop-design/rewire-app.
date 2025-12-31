import streamlit as st
import requests
import fitz
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
            {"role": "system", "content": "Sei un analista esperto. Estrai i punti chiave e i dati principali."},
            {"role": "user", "content": f"Documento: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Errore nell'analisi."

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Intelligence")

with st.sidebar:
    st.header("📁 Caricamento")
    file = st.file_uploader("Carica il PDF", type=["pdf"])
    
    if file and not st.session_state.file_processed:
        with st.spinner("Generazione Report..."):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            st.session_state.doc_text = "".join([page.get_text() for page in doc])[:4000]
            summary = auto_analyze(st.session_state.doc_text)
            st.session_state.messages.append({"role": "assistant", "content": summary})
            st.session_state.file_processed = True
            st.rerun()

    if st.button("🗑️ Carica Nuovo File"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- AREA CHAT E DOWNLOAD ---
if st.session_state.messages:
    # Mostriamo l'ultimo report generato
    st.subheader("📊 Analisi Documento")
    
    # Prepariamo il testo per il download
    full_report = "--- REPORT RE-WIRE ---\n\n"
    for m in st.session_state.messages:
        full_report += f"{m['role'].upper()}: {m['content']}\n\n"

    # PULSANTE DI SALVATAGGIO SEMPRE VISIBILE IN ALTO
    st.download_button(
        label="📥 SALVA ANALISI SU PC/CELLULARE",
        data=full_report,
        file_name="Analisi_REWIRE.txt",
        mime="text/plain",
        key="download_btn" # Chiave univoca per evitare errori
    )
    st.divider()

# Visualizzazione messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interattiva
if prompt := st.chat_input("Fai una domanda per approfondire..."):
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
        res = requests
