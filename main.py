import streamlit as st
import requests
import base64
from PIL import Image
import io

# ============================================
#               CONFIGURAZIONE
# ============================================

API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not API_KEY:
    st.error("❌ ERRORE: Inserisci la chiave API in st.secrets!")
    st.stop()

# 🔥 Modelli Vision validi (2025)
MODELS_TO_TRY = [
    "llama-3.2-90b-vision-instant",
    "llama-3.2-11b-vision-instant"
]

URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")


# ============================================
#                   LOGIN
# ============================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚡ RE-WIRE ACCESS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Accesso negato")
    st.stop()


# ============================================
#         FUNZIONE PREPARAZIONE IMMAGINE
# ============================================

def prepare_image(uploaded_file):
    try:
        img = Image.open(uploaded_file).convert("RGB")
        img.thumbnail((768, 768))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        st.error(f"Errore nel processare l'immagine: {e}")
        return None


# ============================================
#         MEMORIA DELLA SESSIONE
# ============================================

if "chat" not in st.session_state:
    st.session_state.chat = []

if "img" not in st.session_state:
    st.session_state.img = None


# ============================================
#                   SIDEBAR
# ============================================

with st.sidebar:
    st.title("⚡ DASHBOARD")

    file = st.file_uploader("Carica Immagine", type=["jpg", "jpeg", "png"])
    
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Visione Attiva", use_column_width=True)

    if st.button("RESET"):
        st.session_state.chat.clear()
        st.session_state.img = None
        st.rerun()


# ============================================
#                   CHAT UI
# ============================================

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


# ============================================
#          ELABORAZIONE DEL PROMPT
# ============================================

if prompt := st.chat_input("Chiedi qualcosa..."):

    # Mostra il messaggio utente
    st.session_state.chat.append({"role": "user",_
