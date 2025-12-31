import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# -------------------------------------------------------
#                 CONFIGURAZIONE
# -------------------------------------------------------
API_KEY = "INSERISCI_LA_TUA_API_KEY"
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.2-11b-vision-preview"

st.set_page_config(page_title="RE-WIRE AI", layout="wide")


# -------------------------------------------------------
#            FUNZIONE PREPARAZIONE IMMAGINE
# -------------------------------------------------------
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((900, 900))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# -------------------------------------------------------
#                  GESTIONE SESSIONE
# -------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "img" not in st.session_state:
    st.session_state.img = None

if "project_name" not in st.session_state:
    st.session_state.project_name = None


# -------------------------------------------------------
#                    INTERFACCIA SUPERIORE
# -------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#6A5ACD;'>⚡ RE-WIRE AI</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; font-size:18px; color:#555;'>L’assistente che ti aiuta, ti guida e ti risolve i problemi.</p>",
    unsafe_allow_html=True,
)

st.write("---")


# -------------------------------------------------------
#                   SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.header("📁 Progetto")

    project = st.text_input("Nome progetto", value=st.session_state.project_name or "")

    if st.button("💾 Salva progetto"):
        if project.strip() != "":
            st.session_state.project_name = project
            with open(f"{project}.json", "w", encoding="utf-8") as f:
                json.dump({
                    "chat": st.session_state.chat,
                    "img": st.session_state.img
                }, f, ensure_ascii=False)
            st.success("Progetto salvato!")

    if st.button("📂 Carica progetto"):
        if project.strip() != "" and os.path.exists(f"{project}.json"):
            with open(f"{project}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.chat = data.get("chat", [])
                st.session_state.img = data.get("img", None)
            st.success("Progetto caricato!")
            st.experimental_rerun()
        else:
            st.error("Progetto non trovato.")

    st.write("---")

    st.header("🖼 Immagine")
    file = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Immagine caricata", use_column_width=True)

    st.write("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.chat =_
