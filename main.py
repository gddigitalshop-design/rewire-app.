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
    st.markdown("<p style='text-align: center;'>Analisi Intelligente Professionale</p>", unsafe_allow_html=True)

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    with col2:
        pwd = st.text_input("Chiave d'accesso:", type="password")
        if st.button("ENTRA NEL SISTEMA", use_container_width=True):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 3. INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("📁 Documenti")
    file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "jpg", "png"])
    
    if file and st.session_state.doc_text == "":
        with st.spinner("Lettura in corso..."):
            if file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
            else:
                st.session_state.doc_text = f"[File immagine: {file.name}]"
            
            # Annuncio al centro della chat
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"✅ Ho ricevuto il file: `{file.name}`. Chiedimi pure cosa vuoi sapere!"
            })
            st.rerun()

    if st.button("🗑️ Reset Totale"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- 5. VISUALIZZAZIONE CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. SALVATAGGIO ---
if st.session_state.messages:
    report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥 SCARICA REPORT", data=report, file_name="report_rewire.txt", key="save_final")

# --- 7. LOGICA CHAT (Correzione Errore Comunicazione) ---
if prompt := st.chat_input("Scrivi qui la tua domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Se non c'è documento, usiamo un contesto neutro invece di mandare un errore
        doc_context = st.session_state.doc_text if st.session_state.doc_text else "Nessun documento caricato. Rispondi come assistente generale."
        
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Sei un assistente business amichevole. Contesto: {doc_context}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        try:
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
            if r.status_code == 200:
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            else:
                # Mostra l'errore reale solo se necessario
                st.error(f"Il server AI è occupato (Codice {r.status_code}). Riprova tra 5 secondi.")
        except Exception as e:
            st.error(f"Problema di rete. Controlla la connessione.")
