import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# ==================================================
# CONFIGURAZIONE PAGINA
# ==================================================
st.set_page_config(
    page_title="RE-WIRE Business",
    layout="wide"
)

# ==================================================
# SESSION STATE
# ==================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = ""

if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# ==================================================
# LOGIN
# ==================================================
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

def login_system():
    st.markdown(
        "<h1 style='text-align:center;color:#007BFF;'>RE-WIRE PLATFORM</h1>",
        unsafe_allow_html=True
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("ACCEDI", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = username
                st.rerun()
            else:
                st.error("Credenziali non valide")

# ==================================================
# BLOCCO ACCESSO
# ==================================================
if not st.session_state.logged_in:
    login_system()
    st.stop()

# ==================================================
# SIDEBAR
# ==================================================
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

# ==================================================
# AREA PRINCIPALE
# ==================================================
st.header("🚀 Business Hub")

prompt = st.text_input(
    "Descrivi la tua idea",
    placeholder="Esempio: brand tech, logo moderno, strategia marketing"
)

col_img, col_tpl = st.columns(2)

# ==================================================
# GENERAZIONE IMMAGINE
# ==================================================
with col_img:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if prompt.strip() == "":
            st.warning("Inserisci una descrizione")
        else:
            with st.spinner("Generazione immagine in corso..."):
                try:
                    seed = random.randint(1, 999999)

                    url = (
                        "https://pollinations.ai/p/"
                        + urllib.parse.quote(prompt)
                        + f"?width=1024&height=1024"
                        + f"&seed={seed}&model=flux&nologo=true"
                    )

                    response = requests.get(url, timeout=25)
                    Image.open(io.BytesIO(response.content))  # verifica immagine
                    st.session_state.current_img_data = response.content

                except Exception as e:
                    st.error("Errore durante la generazione dell'immagine")
                    st.write(e)

# ==================================================
# GENERAZIONE TEMPLATE BUSINESS (GROQ)
# ==================================================
with col_tpl:
    if st.button("📝 Crea Template Business", use_container_width=True):
        if prompt.strip() == "":
            st.warning("Inserisci una descrizione")
        else:
            with st.spinner("Creazione template strategico..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {
                                "role": "user",
                                "content": f"""
                                Crea un template business professionale per:
                                {prompt}

                                Includi:
                                - Vision
                                - Target
                                - Proposta di valore
                                - Canali di marketing
                                - Monetizzazione
                                - Prossimi step operativi
                                """
                            }
                        ],
                        temperature=0.7,
                        max_tokens=900
                    )

                    st.session_state.current_template = (
                        completion.choices[0].message.content
                    )

                except Exception as e:
                    st.error("Errore durante la generazione del template")
                    st.write(e)

# ==================================================
# OUTPUT RISULTATI
# ==================================================
st.divider()

if st.session_state.current_img_data:
    st.subheader("🖼️ Immagine Generata")
    st.image(st.session_state.current_img_data, use_container_width=True)

if st.session_state.current_template:
    st.subheader("📄 Template Business")
    st.markdown(st.session_state.current_template)
