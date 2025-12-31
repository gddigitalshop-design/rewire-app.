import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# ============================================================
#                   CONFIGURAZIONE BASE
# ============================================================

API_KEY = st.secrets.get("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ Devi inserire la GROQ_API_KEY nei secrets.")
    st.stop()

VISION_MODEL = "llama-3.2-90b-vision-instant"
CHAT_MODEL = "llama-3.2-11b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(
    page_title="HELP KID AI",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# ============================================================
#                   STILE PERSONALIZZATO
# ============================================================

st.markdown("""
    <style>
        body { background-color: #F7F7FC; }
        div.block-container { padding-top: 2rem; }
        .logo-title { text-align:center; font-size:40px; color:#4B6FFF; font-weight:900; margin-top:20px; }
        .subtitle { text-align:center; color:#6A6A8A; font-size:18px; margin-bottom:40px; }
        .chat-box { background:#FFFFFF; padding:20px; border-radius:20px; }
        .save-btn { background:#4B6FFF; color:white; padding:8px 18px; border-radius:10px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
#                   FUNZIONI DI UTILITÀ
# ============================================================

def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((768, 768))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def ai_request(messages, model=CHAT_MODEL):
    payload = {"model": model, "messages": messages, "temperature": 0.4}
    
    r = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload
    )
    if r.status_code != 200:
        return f"❌ Errore: {r.status_code}"
    return r.json()["choices"][0]["message"]["content"]

def save_project(name, data):
    with open(f"project_{name}.json", "w") as f:
        json.dump(data, f)

def load_project(name):
    try:
        with open(f"project_{name}.json", "r") as f:
            return json.load(f)
    except:
        return None

# ============================================================
#                   INIZIALIZZAZIONE SESSIONE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "image_b64" not in st.session_state:
    st.session_state.image_b64 = None

# ============================================================
#                   LAYOUT PRINCIPALE
# ============================================================

st.markdown("<div class='logo-title'>🤖 HELP KID AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Un assistente che risolve problemi, descrive immagini e aiuta la tua famiglia.</div>", unsafe_allow_html=True)

colL, colR = st.columns([1, 2])

# ============================================================
#                   SIDEBAR: PROGETTI
# ============================================================

with st.sidebar:
    st.header("📁 I tuoi progetti")

    project_name = st.text_input("Nome progetto", placeholder="es. famiglia_2025")

    if st.button("💾 Salva progetto"):
        if not project_name:
            st.error("Inserisci un nome progetto.")
        else:
            save_project(project_name, {
                "history": st.session_state.history,
                "image": st.session_state.image_b64
            })
            st.success("Progetto salvato!")

    if st.button("📂 Carica progetto"):
        if not project_name:
            st.error("Inserisci un nome progetto.")
        else:
            loaded = load_project(project_name)
            if loaded:
                st.session_state.history = loaded["history"]
                st.session_state.image_b64 = loaded["image"]
                st.success("Progetto caricato!")
                st.rerun()
            else:
                st.error("Progetto non trovato.")

# ============================================================
#                   COLONNA SINISTRA
# ============================================================

with colL:

    st.subheader("📷 Analisi Immagine per Bimbi Non Vedenti")

    img_file = st.file_uploader("Carica immagine", type=["png", "jpg", "jpeg"])

    if img_file:
        st.session_state.image_b64 = prepare_image(img_file)
        st.image(img_file, caption="Immagine caricata", use_column_width=True)

        # Analisi immagine
        st.write("🧠 Analisi in corso...")

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Descrivi questa immagine per un bambino non vedente, usando parole semplici."},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{st.session_state.image_b64}"
                }
            ]
        }]

        descrizione = ai_request(messages, model=VISION_MODEL)

        st.write("### 🗣 Risposta accessibile")
        st.write(descrizione)

        st.session_state.history.append({"role": "assistant", "content": descrizione})

# ============================================================
#                   CHAT FLUIDA A DESTRA
# ============================================================

with colR:

    st.subheader("💬 Chat intelligente")

    chat_box = st.container()

    with chat_box:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    prompt = st.chat_input("Scrivi qui...")

    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        response = ai_request([
            {"role": "system", "content": "Sei un assistente che risolve problemi quotidiani. Rispondi in modo pratico, empatico e utile."},
            *st.session_state.history
        ])

        with st.chat_message("assistant"):
            st.write(response)

        st.session_state.history.append({"role": "assistant", "content": response})
