import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# --- 1. CONFIGURAZIONE E PERSISTENZA ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

# Inizializzazione variabili di sessione (per non perdere i dati)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. GESTIONE ACCESSO (Semplificata per il browser) ---
USERS = {"admin": "tuapassword123", "cliente1": "rewire2025"}

def login():
    st.markdown("<h1 style='text-align: center;'>RE-WIRE LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Usando queste key, il browser (Chrome/Safari) ti chiederà di salvare la pass
        u = st.text_input("Username", key="auth_u")
        p = st.text_input("Password", type="password", key="auth_p")
        if st.button("SBLOCCA SISTEMA"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Credenziali errate")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- 3. BARRA LATERALE (Pulsanti fissi) ---
with st.sidebar:
    st.title("⚙️ Gestione Sistema")
    st.write(f"Utente attivo: **admin**")
    
    # PULSANTI DI CANCELLAZIONE SEMPRE VISIBILI
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()
        
    if st.button("🚪 ESCI (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 4. AREA CREAZIONE ---
st.header("🚀 Business Hub")
c_prompt = st.text_input("Cosa vuoi creare? (es: Centro commerciale, Logo, Strategia)")

col_a, col_b = st.columns(2)

with col_a:
    if st.button("🖼️ GENERA IMMAGINE HD", use_container_width=True):
        if c_prompt:
            with st.spinner("Generazione..."):
                seed = random.randint(1, 1000000)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(c_prompt)}?seed={seed}&nologo=true&model=flux"
                try:
                    r = requests.get(url, timeout=20)
                    # Verifica se è un'immagine reale o l'errore del server
                    test_img = Image.open(io.BytesIO(r.content))
                    st.session_state.current_img_data = r.content
                except:
                    st.error("⚠️ Server AI sovraccarico. Attendi 30 secondi.")
        else:
            st.warning("Inserisci un'idea!")

with col_b:
    if st.button("📝 CREA TEMPLATE", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea un template professionale per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore connessione Groq.")

# --- 5. VISUALIZZAZIONE E SALVATAGGIO ---
st.divider()

if st.session_state.current_img_data:
    st.subheader("🖼️ Risultato Visuale")
    st.image(st.session_state.current_img_data, use_container_width=True)
    # TASTO SALVATAGGIO SEMPRE SOTTO L'IMMAGINE
    st.download_button(
        label="💾 SALVA IMMAGINE SU PC",
        data=st.session_state.current_img_data,
        file_name="progetto_rewire.png",
        mime="image/png",
        use_container_width=True
    )

if st.session_state.current_template:
    st.subheader("📝 Template Strategico")
    st.info(st.session_state.current_template)
    st.download_button(
        label="💾 SALVA TESTO",
        data=st.session_state.current_template,
        file_name="template_rewire.txt",
        use_container_width=True
    )
