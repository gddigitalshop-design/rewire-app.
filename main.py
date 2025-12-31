
import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        background: -webkit-linear-gradient(#00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.45);
        border-right: 1px solid rgba(0, 242, 254, 0.3);
        backdrop-filter: blur(15px);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: #0f0c29 !important;
        border-radius: 20px;
        font-weight: bold;
        width: 100%;
    }
    hr { border-top: 2px solid rgba(79, 172, 254, 0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DI LOGIN ---
if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<br><br><h1 style='text-align: center;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            pwd = st.text_input("Chiave d'Accesso:", type="password")
            if st.button("SBLOCCA SISTEMA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Chiave errata.")
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file_data" not in st.session_state: st.session_state.current_file_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## DASHBOARD")
    uploaded_file = st.file_uploader("📂 Carica file", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        if "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
            st.session_state.messages = []
            st.session_state.last_file_name = uploaded_file.name
            if uploaded_file.type in ["image/jpeg", "image/png"]:
                st.session_state.current_file_data = {"type": "image", "data": uploaded_file.read(), "name": uploaded_file.name}
                st.session_state.doc_text = "Analisi immagine caricata."
            else:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.current_file_data = {"type": "pdf", "data": st.session_state.doc_text, "name": uploaded_file.name}
            st.rerun()

    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file_data = None
        st.rerun()

# --- AREA CENTRALE ---
st.markdown("<h2 style='text-align: center;'>📄 AREA DOCUMENTI</h2>", unsafe_allow_html=True)

if st.session_state.current_file_data:
    f = st.session_state.current_file_data
    # RIGA CORRETTA QUI SOTTO:
    col_c1, col_c2, col_c3 = st.columns([0.2, 4, 0.2])
    with col_c2:
        if f["type"] == "image":
            st.image(f["data"], use_container_width=True)
        else:
            with st.expander("🔍 Testo PDF Estratto"):
                st.write(f["data"])
else:
    st.markdown("<p style='text-align: center; opacity: 0.5;'>Carica un file per iniziare.</p>", unsafe_allow_html=True)

st.divider()

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi a RE-WIRE AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Sei RE-WIRE AI. Contesto: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
        except:
            ans = "Errore AI."
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
