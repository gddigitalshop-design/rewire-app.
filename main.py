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

# --- STILE CSS PERSONALIZZATO (IL "MOTORE" GRAFICO) ---
st.markdown("""
    <style>
    /* Sfondo e Font Generale */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Titoli Neon */
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background: -webkit-linear-gradient(#00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Sidebar futuristica */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.45);
        border-right: 1px solid rgba(0, 242, 254, 0.3);
        backdrop-filter: blur(15px);
    }

    /* Box Messaggi Chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
        margin-bottom: 12px;
        padding: 15px !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }

    /* Campi di Input */
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: #00f2fe !important;
        border: 1px solid #4facfe !important;
        border-radius: 10px;
    }

    /* Bottoni ad alto contrasto */
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: #0f0c29 !important;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0px 5px 15px rgba(0, 242, 254, 0.4);
        color: #ffffff !important;
    }
    
    /* Linea di separazione */
    hr {
        border-top: 2px solid rgba(79, 172, 254, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DI LOGIN ---
if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #4facfe;'>Premium Intelligence Access</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            pwd = st.text_input("Inserisci la Chiave d'Accesso:", type="password")
            if st.button("SBLOCCA SISTEMA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Accesso negato. Chiave errata.")
    st.stop()

# --- INIZIALIZZAZIONE DATI ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file_data" not in st.session_state: st.session_state.current_file_data = None

# --- SIDEBAR (PANNELLO DI CONTROLLO) ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe;'>DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Carica Documento o Foto", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        if "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
            st.session_state.messages = []
            st.session_state.last_file_name = uploaded_file.name
            
            if uploaded_file.type in ["image/jpeg", "image/png"]:
                img_bytes = uploaded_file.read()
                st.session_state.current_file_data = {"type": "image", "data": img_bytes, "name": uploaded_file.name}
                st.session_state.doc_text = f"Analisi immagine: {uploaded_file.name}"
            elif uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.doc_text = text
                st.session_state.current_file_data = {"type": "pdf", "data": text, "name": uploaded_file.name}
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # PULSANTE RESET SELETTIVO (Non cancella il login)
    if st.button("🗑️ SVUOTA WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file_data = None
        if "last_file_name" in st.session_state: 
            del st.session_state.last_file_name
        st.rerun()

# --- AREA CENTRALE: VISUALIZZAZIONE ---
st.markdown("<h2 style='text-align: center;'>📄 AREA DOCUMENTI</h2>", unsafe_allow_html=True)

with st.container():
    if st.session_state.current_file_data:
        f = st.session_state.current_file_data
        col_c1, col_c2, col_
