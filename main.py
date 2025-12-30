import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse
import requests

# --- 1. CONFIGURAZIONE E PERSISTENZA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

# Inizializzazione variabili di sessione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# Stile CSS
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 12px; font-weight: bold; }
    .main-title { font-size: 3rem; font-weight: 800; color: #007BFF; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE UTENTI ---
USERS = {"admin": "tuapassword123", "cliente1": "rewire2025"}

# --- 3. GESTIONE LOGIN (CON TRUCCO PER NON DIGITARE SEMPRE) ---
def login_page():
    st.markdown('<p class="main-title">RE-WIRE LOGIN</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Usando 'key' fisse, il browser di solito salva i dati per l'autofill
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("SBLOCCA SISTEMA"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali errate")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 4. FUNZIONE GENERAZIONE IMMAGINI (ANTI-BLOCCO) ---
def genera_immagine_sicura(prompt_utente):
    # Generiamo un seed casuale per forzare il server a ignorare i vecchi errori
    seed = random.randint(1, 1000000)
    prompt_pro = f"{prompt_utente}, cinematic style, realistic, 8k, highly detailed"
    prompt_encoded = urllib.parse.quote(prompt_pro)
    
    # URL di backup (usiamo l'endpoint 'p' che spesso è più libero)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    try:
        # Proviamo a scaricare l'immagine direttamente per evitare lo standby
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.content
    except:
        return None
    return None

# --- 5. INTERFACCIA PRINCIPALE ---
with st.sidebar:
    st.title("RE-WIRE PANEL")
    st.write(f"Utente: **{st.session_state.user_role.upper()}**")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    if st.button("🗑️ SVUOTA CHAT"):
        st.session_state.messages = []
        st.rerun()

st.header("🚀 Business Hub")
c_prompt = st.text_input("Cosa vuoi creare oggi?")

# Layout Bottoni
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🖼️ GENERA IMMAGINE HD"):
        if c_prompt:
            with st.spinner("L'AI sta disegnando..."):
                img = genera_immagine_sicura(c_prompt)
                if img:
                    st.session_state.current_img_data = img
                else:
                    st.error("Errore server (Rate Limit). Riprova tra 10 secondi.")
        else:
            st.warning("Scrivi qualcosa nel campo sopra!")

with col_btn2:
    if st.button("📝 CREA TEMPLATE"):
        if c_prompt:
            with st.spinner("Scrittura template..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sei un esperto di business. Crea template professionali."},
                              {"role": "user", "content": f"Crea un template per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
        else:
            st.warning("Scrivi l'argomento del template!")

# --- AREA VISUALIZZAZIONE RISULTATI ---
if st.session_state.current_img_data:
    st.image(st.session_state.current_img_data, use_container_width=True)
    st.download_button("💾 SCARICA IMMAGINE", st.session_state.current_img_data, "creazione.png", "image/png")
    if st.button("❌ CHIUDI IMMAGINE"):
        st.session_state.current_img_data = None
        st.rerun()

if st.session_state.current_template:
    st.info("Template Generato:")
    st.markdown(st.session_state.current_template)
    if st.button("❌ CHIUDI TEMPLATE"):
        st.session_state.current_template = None
        st.rerun()

st.divider()

# --- 6. CHAT DI SUPPORTO ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if p := st.chat_input("Chiedi aiuto alla tua AI..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
        response = compl.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
