import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="✨")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🌟 Benvenuto in RE-WIRE")
    pwd = st.text_input("Chiave d'accesso:", type="password")
    if st.button("ENTRA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Documenti")
    file = st.file_uploader("Carica PDF o Foto", type=["pdf", "jpg", "png"])
    if file and not st.session_state.doc_text:
        with st.spinner("Leggo..."):
            if file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
            else:
                st.session_state.doc_text = f"[Immagine: {file.name}]"
            st.success("File caricato!")

    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- CHAT LOGIC ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Se non c'è testo, inviamo un prompt pulito senza errori
        context = st.session_state.doc_text if st.session_state.doc_text else "Nessun documento caricato."
        
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Sei un assistente amichevole. Contesto: {context}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=10)
            if r.status_code == 200:
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
                # PULSANTE SALVA (Appare solo dopo la risposta)
                report = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                st.download_button("📥 SALVA LAVORO", data=report, file_name="report.txt", key="dl_btn")
            else:
                st.error("Il server è un po' lento, riprova tra un istante! ⏳")
        except:
            st.error("Connessione instabile. Riprova! 😊")
