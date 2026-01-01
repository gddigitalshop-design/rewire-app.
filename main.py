import streamlit as st
import requests
import fitz
from PIL import Image

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI Factory", layout="wide", page_icon="⚙️")

# --- CSS PROFESSIONALE ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #1a1c24; border-right: 1px solid #333; }
    .file-preview-card {
        background-color: #1e212b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3b82f6;
        margin-bottom: 20px;
        text-align: center;
    }
    .stButton>button { width: 100%; border-radius: 8px; margin-bottom: 10px; }
    /* Colore specifico per i tasti */
    .btn-save { background-color: #10b981 !important; color: white !important; }
    .btn-reset { background-color: #ef4444 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("⚙️ Accesso Riservato")
        pwd = st.text_input("Inserisci Password", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "file_view" not in st.session_state: st.session_state.file_view = None

# --- SIDEBAR (PUNTO 1: TASTI MANCANTI) ---
with st.sidebar:
    st.markdown("### 🚀 RE-WIRE AI")
    st.markdown("**Operatore:** GIANNI")
    st.divider()
    
    # 1. TASTO CARICA FILE
    st.markdown("#### 📁 Caricamento Asset")
    uploaded_file = st.file_uploader("Scegli un file...", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        if "fname" not in st.session_state or st.session_state.fname != uploaded_file.name:
            st.session_state.fname = uploaded_file.name
            if uploaded_file.type in ["image/jpeg", "image/png"]:
                st.session_state.file_view = {"type": "img", "content": uploaded_file.read()}
                st.session_state.doc_text = f"Immagine: {uploaded_file.name}"
            else:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                txt = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.file_view = {"type": "txt", "content": txt}
                st.session_state.doc_text = txt
            st.rerun()

    st.divider()

    # 2. TASTO SALVA LAVORO
    if st.session_state.messages:
        chat_full = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="📥 SALVA LAVORO",
            data=chat_full,
            file_name=f"report_{st.session_state.get('fname', 'chat')}.txt",
            use_container_width=True
        )

    # 3. TASTO SVUOTA CHAT
    if st.button("🗑️ SVUOTA CHAT", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_view = None
        st.session_state.fname = None
        st.rerun()
    
    st.divider()
    if st.button("🔴 ESCI"):
        st.session_state.auth = False
        st.rerun()

# --- AREA CENTRALE ---
st.markdown(f"## ⚙️ Factory Dashboard - Sessione di Gianni")

# Visualizzazione Documento al centro (PUNTO 2)
if st.session_state.file_view:
    st.markdown('<div class="file-preview-card">', unsafe_allow_html=True)
    if st.session_state.file_view["type"] == "img":
        st.image(st.session_state.file_view["content"], caption=st.session_state.fname, use_container_width=True)
    else:
        st.info(f"Contenuto PDF: {st.session_state.fname}")
        st.text_area("", st.session_state.file_view["content"], height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input prompt
if prompt := st.chat_input("Digita un comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            r = requests.post(API_URL, 
                json={"model": MODEL_ID, "messages": [{"role": "system", "content": f"Analista Factory. Context: {st.session_state.doc_text}"}, {"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except: st.error("Errore AI.")
    st.rerun()
