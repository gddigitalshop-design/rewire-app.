import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- 1. LOGO E HEADER CENTRATO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Analisi Intelligente in Tempo Reale</p>", unsafe_allow_html=True)

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with col2:
        pwd = st.text_input("Inserisci la chiave d'accesso:", type="password")
        if st.button("ENTRA NEL SISTEMA", use_container_width=True):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 3. INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- 4. SIDEBAR (Caricamento) ---
with st.sidebar:
    st.header("📁 Gestione Documenti")
    file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "jpg", "png"])
    
    if file and st.session_state.doc_text == "":
        with st.spinner("Elaborazione file..."):
            if file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
            else:
                st.session_state.doc_text = f"[Contenuto immagine: {file.name}]"
            
            # MOSTRA AL CENTRO: Inseriamo l'avviso direttamente nei messaggi
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"✅ **File caricato con successo:** `{file.name}`. Sono pronto ad analizzarlo, chiedimi pure!"
            })
            st.rerun()

    if st.button("🗑️ Reset Analisi"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- 5. VISUALIZZAZIONE CHAT ---
# Mostra i messaggi (incluso l'avviso del file caricato)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. AZIONE SALVA (Sotto la chat) ---
if st.session_state.messages:
    report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥 SALVA IL LAVORO SVOLTO", data=report, file_name="analisi_rewire.txt", key="save_final")

# --- 7. INPUT UTENTE ---
if prompt := st.chat_input("Scrivi qui la tua domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        context = st.session_state.doc_text if st.session_state.doc_text else "Nessun file."
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Sei un assistente business esperto. Contesto documento: {context}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        try:
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=10)
            ans = r.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
        except:
            st.error("Errore di comunicazione con l'AI. Riprova.")
