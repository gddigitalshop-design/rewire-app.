import streamlit as st
import requests
import base64
import PyPDF2
import io

# --- 1. SETUP UI: DESIGN PREMIUM & VIVO ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
    }

    /* Area di caricamento stile "Isola di Rame" */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #6366f1 !important;
        background: rgba(99, 102, 241, 0.05) !important;
        border-radius: 20px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #818cf8 !important;
        background: rgba(99, 102, 241, 0.1) !important;
    }

    .stImage > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 15px;
        border: 2px solid #6366f1;
    }

    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 1px solid #6366f1 !important;
    }
    
    h1, h2, h3 { color: #818cf8 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO & SESSIONE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API Groq non trovata nei Secrets.")
    st.stop()

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1>⚡ REWIRE PRO</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Licenza Group 4.0:", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026": #
                st.session_state.auth = True
                st.rerun()
            else: st.error("Licenza non valida.")
    st.stop()

# --- 3. FUNZIONI DI SERVIZIO ---
def get_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except: return ""

def prepare_download_text(messages):
    report = "--- REWIRE AI - REPORT SESSIONE ---\n\n"
    for m in messages:
        role = "UTENTE" if m["role"] == "user" else "REWIRE AI"
        report += f"{role}:\n{m['content']}\n\n"
    return report

# --- 4. SIDEBAR (LOGICA DINAMICA) ---
with st.sidebar:
    st.title("📂 Risorse")
    st.info("Rewire: Gestione Documenti")
    
    # Se ci sono messaggi, l'uploader si sposta qui per lasciare spazio alla chat
    file = None
    if st.session_state.messages:
        file = st.file_uploader("Carica File aggiuntivi", type=["pdf", "png", "jpg", "jpeg"], key="sidebar_up")
    
    st.markdown("---")
    st.subheader("💾 Gestione Lavoro")
    if st.session_state.messages:
        report_data = prepare_download_
