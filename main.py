import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- STILE CSS PER FISSARE LA CHAT ---
st.markdown("""
    <style>
    .block-container { padding-bottom: 100px; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

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
        if "last_file" not in st.session_state or st.session_state.last_file != file.name:
            st.session_state.doc_text = ""
            st.session_state.messages = []
            st.session_state.last_file = file.name
            
            with st.spinner("Apertura file..."):
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    text = "".join([p.get_text() for p in doc])[:4000]
                    st.session_state.doc_text = text
                    # PUNTO 2: Mostriamo il contenuto al centro
                    st.session_state.messages.append({"role": "assistant", "content": f"📄 **Contenuto del PDF estratto:**\n\n{text[:500]}..."})
                else:
                    st.session_state.doc_text = f"[Immagine: {file.name}]"
                    st.session_state.messages.append({"role": "assistant", "content": f"📸 Hai caricato l'immagine: `{file.name}`. Analizziamola!"})
                st.rerun()

    if st.button("🗑️ Reset"):
        st.session_state.clear()
        st.rerun()

# --- AREA CHAT (PUNTO 3: Scorrimento) ---
# Contenitore per i messaggi
chat_container = st.container()

with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# --- INPUT E LOGICA ---
if prompt := st.chat_input("Chiedi all'AI..."):
    # 1. Mostra subito la domanda
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # 2. Genera risposta
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Sto scrivendo..."):
                context = st.session_state.doc_text if st.session_state.doc_text else "Assistente generale."
                try:
                    r = requests.post(API_URL, 
                                     json={"model": MODEL_ID, "messages": [{"role": "system", "content": f"Contesto: {context}"}, {"role": "user", "content": prompt}]},
                                     headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
                    ans = r.json()['choices'][0]['message']['content']
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except:
                    st.error("Errore di rete, riprova tra un istante.")

# --- SALVATAGGIO (Sempre visibile in fondo) ---
if st.session_state.messages:
    report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.sidebar.download_button("📥 SALVA REPORT", data=report, file_name="analisi.txt")
