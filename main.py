import streamlit as st
import requests
import fitz
import time

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

# --- FUNZIONE ANALISI AUTOMATICA ---
def auto_analyze(text):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Sei un analista esperto. Estrai i punti chiave, scadenze e dati numerici dal documento."},
            {"role": "user", "content": f"Analizza questo documento: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Errore durante l'analisi."

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Intelligence")

with st.sidebar:
    st.header("📁 Caricamento Documento")
    file = st.file_uploader("Trascina qui il PDF", type=["pdf"])
    
    # Analisi Automatica al caricamento
    if file and not st.session_state.file_processed:
        with st.spinner("Generazione Report Automatico..."):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "".join([page.get_text() for page in doc])[:4000]
            st.session_state.doc_text = text
            
            summary = auto_analyze(text)
            st.session_state.messages.append({"role": "assistant", "content": f"📑 **REPORT AUTOMATICO GENERATO:**\n\n{summary}"})
            st.session_state.file_processed = True
            st.rerun()

    st.divider()
    
    # --- SEZIONE SALVATAGGIO ---
    if st.session_state.messages:
        st.header("💾 Esporta Risultati")
        # Prepariamo il testo del report
        full_report = "--- REPORT RE-WIRE ---\n\n"
        for m in st.session_state.messages:
            full_report += f"{m['role'].upper()}: {m['content']}\n\n"
        
        st.download_button(
            label="📥 SCARICA ANALISI (TXT)",
            data=full_report,
            file_name="Report_Analisi_REWIRE.txt",
            mime="text/plain"
        )
    
    if st.button("🗑️ Carica nuovo file"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- CHAT AREA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda per approfondire..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Base dati: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        answer = response.json()['choices'][0]['message']['content']
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun() # Refresh per aggiornare il file scaricabile con l'ultima risposta
