import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- LOGO CENTRATO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with col2:
        pwd = st.text_input("Chiave d'accesso:", type="password")
        if st.button("ENTRA", use_container_width=True):
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
    
    if file:
        # Se il nome del file è diverso da quello in memoria, puliamo tutto (Auto-Clear)
        if "last_file" not in st.session_state or st.session_state.last_file != file.name:
            st.session_state.doc_text = ""
            st.session_state.messages = []
            st.session_state.last_file = file.name
            
            with st.spinner("Preparazione ambiente pulito..."):
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
                else:
                    st.session_state.doc_text = f"[Immagine: {file.name}]"
                
                st.session_state.messages.append({"role": "assistant", "content": f"✅ File `{file.name}` pronto per l'analisi!"})
                st.rerun()

    if st.button("🗑️ Reset Totale"):
        st.session_state.clear() # Questo pulisce TUTTO, inclusa la cache di sessione
        st.rerun()

# --- CHAT & SALVATAGGIO ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if st.session_state.messages:
    report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥 SALVA REPORT", data=report, file_name="analisi.txt", key="dl_1")

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        context = st.session_state.doc_text if st.session_state.doc_text else "Assistente generale."
        try:
            r = requests.post(API_URL, 
                             json={"model": MODEL_ID, "messages": [{"role": "system", "content": f"Contesto: {context}"}, {"role": "user", "content": prompt}]},
                             headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
            ans = r.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
        except:
            st.error("Errore temporaneo. Riprova tra un secondo! 😊")
