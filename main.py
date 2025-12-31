import streamlit as st
import requests
import fitz
import time

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Auto-AI", layout="wide", page_icon="⚡")

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

# --- FUNZIONE ANALISI AUTOMATICA ---
def auto_analyze(text):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Sei un analista business. Fornisci un riassunto esecutivo puntato del documento."},
            {"role": "user", "content": f"Analizza questo documento: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Errore durante l'analisi automatica."

# --- INTERFACCIA ---
st.title("⚡ RE-WIRE Auto-Analysis System")

with st.sidebar:
    st.header("📁 Caricamento")
    file = st.file_uploader("Trascina qui il PDF", type=["pdf"])
    
    if file and not st.session_state.file_processed:
        with st.spinner("Analisi automatica in corso..."):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "".join([page.get_text() for page in doc])[:4000]
            st.session_state.doc_text = text
            
            # Esegue l'analisi automatica
            summary = auto_analyze(text)
            st.session_state.messages.append({"role": "assistant", "content": f"✅ **Analisi Automatica Completata:**\n\n{summary}"})
            st.session_state.file_processed = True
            st.rerun()

    if st.button("🗑️ Reset / Nuovo File"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- CHAT AREA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda specifica sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Contesto documento: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        answer = response.json()['choices'][0]['message']['content']
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
