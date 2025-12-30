import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = ""

if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --------------------------------------------------
# LOGIN
# --------------------------------------------------
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

def login_system():
    st.markdown(
        "<h1 style='text-align:center;color:#007BFF;'>RE-WIRE PLATFORM</h1>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("ACCEDI", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = username
                st.rerun()
            else:
                st.error("Credenziali non valide")

# --------------------------------------------------
# BLOCCO ACCESSO
# --------------------------------------------------
if not st.session_state.logged_in:
    login_system()
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.title("⚙️ Pannello di Controllo")
    st.write(f"Utente: **{st.session_state.user_role}**")
    st.divider()

    if st.button("🗑️ Cancella Sessione", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = ""
        st.rerun()

# --------------------------------------------------
# AREA PRINCIPALE
# --------------------------------------------------
st.header("🚀 Business Hub")

prompt = st.text_input(
    "Descrivi la tua idea",
    placeholder="Esempio: brand tech, logo moderno, strategia marketing"
)

col1, col2 = st.columns(2)

# --------------------------------------------------
# GENERA IMMAGINE
# --------------------------------------------------
with col1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if prompt == "":
            st.warning("Inserisci una descrizione")
        else:
            with st.spinner("Generazione immagine..."):
                try:
                    seed = random.randint(1, 999999)
                    url = (
                        "https://pollinations.ai/p/"
                        + urllib.parse.quote(prompt)
                        + f"?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
                    )

                    r = requests.get(url, timeout=25)
                    Image.open(io.BytesIO(r.content))
                    st.session_state.current_img_data = r.content

                except Exception:
                    st.e
