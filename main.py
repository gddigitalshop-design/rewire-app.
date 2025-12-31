import streamlit as st
import requests
import base64
from PIL import Image
import io
import pyttsx3
import uuid

# ---------------------
# CONFIGURAZIONE APP
# ---------------------
st.set_page_config(
    page_title="REWIRE AI",
    page_icon="⚡",
    layout="wide"
)

GROQ_API_KEY = "INSERISCI_LA_TUA_CHIAVE"  # <<< METTI QUI LA TUA NUOVA CHIAVE
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# ---------------------
# STILE CSS
# ---------------------
st.markdown("""
<style>
body { background-color: #f2f4ff; }
.chat-bubble {
    background: white;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 10px;
    font-size: 18px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.15);
}
button {
    background-color: #6c63ff;
    color: white;
    font-size: 16px;
    padding: 10px;
    border-radius: 10px;
}
#MainMenu, header, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------
# INIZIALIZZAZIONE STATI
# ---------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "saved_chat" not in st.session_state:
    st.session_state.saved_chat = None
if "image_b64" not in st.session_state:
    st.session_state.image_b64 = None
if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = pyttsx3.init()

# ---------------------
# LOGIN
# ---------------------
if not st.session_state.auth:
    st.title("🔐 ACCESSO REWIRE AI")
    pwd = st.text_input("Password:", type="password")
    if st.button("ACCEDI"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.experimental_rerun()
        else:
            st.error("Password errata.")
    st.stop()

# ---------------------
# FUNZIONI
# ---------------------
def prepare_image(file):
    img = Image.open(file).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def groq_answer(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    content = [{"type": "text", "text": prompt}]
    if st.session_state.image_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{st.session_state.image_b64}"
            }
