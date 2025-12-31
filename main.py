import streamlit as st
import requests
import fitz
import time

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business AI", layout="wide", page_icon="🧠")

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

# --- INTERFACCIA SIDEBAR ---
with st.sidebar:
    st.header("📁 Documenti")
    file = st.file_uploader("Carica PDF", type=["pdf"])
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        # Estraiamo il testo e lo salviamo stabilmente
        st.session_state.doc_text = "".join([page.get_text() for page in doc])[:4000]
        st.success("Documento memorizzato!")

    st.divider()
    if st.session_state.messages:
        report = "--- REPORT RE-WIRE ---\n\n" + "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Scarica Report", data=report, file_name="analisi.txt")

    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- AREA CHAT ---
st.title("🧠 RE-WIRE Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda sul file..."):
    # 1. Registra domanda utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Genera risposta
    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            # COSTRUZIONE PROMPT INFALLIBILE
            # Fondiamo il documento direttamente nell'ultimo messaggio dell'utente
            document_context = f"CONTESTO DOCUMENTO CARICATO:\n{st.session_state.doc_text}\n\n---\n\nDOMANDA UTENTE: {prompt}"
            
            payload_messages = [
                {"role": "system", "content": "Sei un analista business. Rispondi SEMPRE basandoti sul documento fornito sopra. Se il documento è vuoto, avvisa l'utente."},
                {"role": "user", "content": document_context}
            ]

            try:
                response = requests.post(
                    API_URL,
                    json={"model": MODEL_ID, "messages": payload_messages, "temperature": 0.1},
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    st.error("Errore di sincronizzazione. Riprova.")
            except Exception as e:
                st.error(f"Connessione persa: {e}")
