import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# --------------------------------------------------
# 1. CONFIGURAZIONE PAGINA E STILE
# --------------------------------------------------
st.set_page_config(
    page_title="RE-WIRE Business",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione variabili di sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --------------------------------------------------
# 2. SISTEMA LOGIN (Persistente)
# --------------------------------------------------
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

def login_system():
    st.markdown("<h1 style='text-align:center;color:#007BFF;'>RE-WIRE PLATFORM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # L'uso di chiavi univoche permette al browser di salvare le credenziali
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")

        if st.button("ACCEDI", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali errate. Riprova.")

if not st.session_state.logged_in:
    login_system()
    st.stop()

# --------------------------------------------------
# 3. BARRA LATERALE (Pulsanti di controllo fissi)
# --------------------------------------------------
with st.sidebar:
    st.title("⚙️ Gestione")
    st.write(f"Utente: **{st.session_state.user_role}**")
    st.divider()
    
    # Pulsanti sempre visibili per l'utente
    if st.button("🗑️ CANCELLA SESSIONE", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()
        
    if st.button("🚪 ESCI (LOGOUT)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

# --------------------------------------------------
# 4. AREA DI GENERAZIONE PRINCIPALE
# --------------------------------------------------
st.header("🚀 Business Hub")
c_prompt = st.text_input("Descrivi la tua idea (es: Centro commerciale moderno, Logo tech, Strategia Market)")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🖼️ GENERA IMMAGINE HD", use_container_width=True):
        if c_prompt:
            with st.spinner("L'AI sta disegnando..."):
                seed = random.randint(1, 1000000)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(c_prompt)}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                try:
                    r = requests.get(url, timeout=25)
                    # Verifica se è un'immagine valida o un errore HTML (Rate Limit)
                    img_check = Image.open(io.BytesIO(r.content))
                    st.session_state.current_img_data = r.content
                except:
                    st.error("⚠️ Server immagini saturo (Rate Limit). Riprova tra 30 secondi.")
        else:
            st.warning("Inserisci una descrizione!")

with col_btn2:
    if st.button("📝 CREA TEMPLATE", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura template..."):
                try:
                    # Assicurati di avere la chiave GROQ_API_KEY nei Secrets di Streamlit
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea un template business per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore API Groq. Verifica la tua chiave API.")

# --------------------------------------------------
# 5. VISUALIZZAZIONE RISULTATI E SALVATAGGIO
# --------------------------------------------------
st.divider()

if st.session_state.current_img_data:
    st.subheader("🖼️ Anteprima Progetto")
    st.image(st.session_state.current_img_data, use_container_width=True)
    st.download_button(
        label="💾 SCARICA IMMAGINE",
        data=st.session_state.current_img_data,
        file_name="progetto_rewire.png",
        mime="image/png",
        use_container_width=True
    )

if st.session_state.current_template:
    st.subheader("📝 Template Strategico")
    st.info(st.session_state.current_template)
    st.download_button(
        label="💾 SCARICA TESTO",
        data=st.session_state.current_template,
        file_name="strategia_rewire.txt",
        use_container_width=True
    )
