import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. LOGIN (Browser autofill enabled) ---
USERS = {"admin": "tuapassword123", "cliente1": "rewire2025"}

def login_system():
    st.markdown("<h1 style='text-align:center;color:#007BFF;'>RE-WIRE PLATFORM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("ACCEDI", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali errate.")

if not st.session_state.logged_in:
    login_system()
    st.stop()

# --- 3. SIDEBAR FISSA ---
with st.sidebar:
    st.title("⚙️ Pannello")
    st.write(f"Utente: **{st.session_state.get('user_role')}**")
    st.divider()
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 4. CORE GENERAZIONE ---
st.header("🚀 Business Hub")
c_prompt = st.text_input("Cosa vuoi creare oggi?")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ GENERA IMMAGINE HD", use_container_width=True):
        if c_prompt:
            with st.spinner("L'AI sta disegnando..."):
                seed = random.randint(1, 1000000)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(c_prompt)}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                try:
                    r = requests.get(url, timeout=20)
                    if r.status_code == 200:
                        # VALIDAZIONE: Cerchiamo di aprire l'immagine prima di salvarla
                        img_temp = Image.open(io.BytesIO(r.content))
                        img_temp.verify() # Se è HTML/Errore, qui scatta l'eccezione
                        st.session_state.current_img_data = r.content
                        st.success("Immagine generata con successo!")
                    else:
                        st.error("Il server AI non risponde correttamente.")
                except Exception:
                    st.error("⚠️ Errore: Il server è in Rate Limit (troppe richieste). Riprova tra 30 secondi.")
        else:
            st.warning("Inserisci una descrizione!")

with col2:
    if st.button("📝 CREA TEMPLATE", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea un template per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore Groq API.")

# --- 5. DISPLAY RISULTATI ---
st.divider()

# Mostra l'immagine solo se i dati sono validi
if st.session_state.current_img_data:
    try:
        st.image(st.session_state.current_img_data, use_container_width=True)
        st.download_button("💾 SCARICA IMMAGINE", st.session_state.current_img_data, "creazione.png", "image/png")
    except Exception:
        st.session_state.current_img_data = None # Pulisce lo stato se i dati sono corrotti
        st.error("Immagine corrotta ricevuta dal server. Riprova la generazione.")

if st.session_state.current_template:
    st.info("Template Generato:")
    st.markdown(st.session_state.current_template)
    st.download_button("💾 SCARICA TESTO", st.session_state.current_template, "template.txt")
