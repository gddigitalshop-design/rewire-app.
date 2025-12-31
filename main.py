import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# 1. CONFIGURAZIONE UI E STILE FORZATO (TESTO NERO)
# ---------------------------------------------------------
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Forza il colore del testo globale */
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    
    /* Stile per i messaggi della chat */
    [data-testid="stChatMessage"] {
        background-color: #f0f2f6 !important; /* Grigio chiaro per i messaggi */
        border: 1px solid #ddd !important;
        color: #1a1a1a !important; /* Testo nero */
        border-radius: 15px;
    }

    /* Distinzione colore testo per l'assistente */
    [data-testid="stChatMessageContent"] p {
        color: #1a1a1a !important;
        font-size: 16px;
    }

    /* Sidebar scura per contrasto professionale */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Bottone login e azioni */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #4F46E5;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INIZIALIZZAZIONE E SICUREZZA
# ---------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Gestione sicura della chiave API
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API non trovata nei Secrets di Streamlit.")
    st.stop()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------
# 3. PAGINA DI LOGIN
# ---------------------------------------------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #1a1a1a;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        st.info("Sistema protetto. Inserisci la licenza per continuare.")
        pwd = st.text_input("Password Licenza:", type="password")
        if st.button("SBLOCCA SOFTWARE"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Password errata.")
    st.stop()

# ---------------------------------------------------------
# 4. SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚡ Rewire Control")
    st.success("Licenza: ATTIVA (2026)")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📁 Carica File (Immagini/Testo)", type=["png", "jpg", "jpeg", "txt"])
    
    template = st.selectbox("🎯 Template Rapidi:", [
        "Chat Libera", 
        "Analisi Tecnica Immagine", 
        "Riassunto Contenuto"
    ])
    
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# ---------------------------------------------------------
# 5. FUNZIONE CHIAMATA API GROQ
# ---------------------------------------------------------
def get_ai_response(user_input, image_b64=None):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Sceglie il modello in base alla presenza di un'immagine
    model = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    
    # Prepara il contenuto del messaggio
    if image_b64:
        user_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    else:
        user_content = user_input

    # Costruisce la cronologia messaggi
    payload_messages = [{"role": "system", "content": "
