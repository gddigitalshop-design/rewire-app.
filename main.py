import streamlit as st
import requests
import base64
import json
from PIL import Image
import io

# ---------------------
# CONFIGURAZIONE
# ---------------------
st.set_page_config(
    page_title="REWIRE AI",
    page_icon="⚡",
    layout="wide"
)

GROQ_API_KEY = "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"

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"   # ✔ stabile + vision support

# ---------------------
# STILE
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
#MainMenu, header, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ---------------------
# LOGIN
# ---------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

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
# STATI
# ---------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "saved_chat" not in st.session_state:
    st.session_state.saved_chat = None

if "image_b64" not in st.session_state:
    st.session_state.image_b64 = None


# ---------------------
# VISION
# ---------------------
def prepare_image(file):
    img = Image.open(file).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------
# SIDEBAR
# ---------------------
with st.sidebar:
    st.title("⚡ FUNZIONI")

    file = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.image_b64 = prepare_image(file)
        st.image(file, caption="Immagine caricata")

    if st.button("💾 Salva chat"):
        st.session_state.saved_chat = st.session_state.chat
        st.success("Chat salvata!")

    if st.button("📂 Riapri chat"):
        if st.session_state.saved_chat:
            st.session_state.chat = st.session_state.saved_chat
            st.experimental_rerun()
        else:
            st.warning("Nessuna chat salvata.")

    if st.button("🔄 Reset"):
        st.session_state.chat = []
        st.session_state.image_b64 = None
        st.experimental_rerun()


# ---------------------
# FUNZIONE AI
# ---------------------
def groq_answer(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    content = [{"type": "text", "text": prompt}]

    if st.session_state.image_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{st.session_state.image_b64}"
            }
        })

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sei REWIRE AI. Aiuti famiglie, bambini non vedenti, utenti con problemi quotidiani. "
                    "Rispondi con calma, preci


