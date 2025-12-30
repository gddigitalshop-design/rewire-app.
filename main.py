import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse
import requests

# --- 1. CONFIGURAZIONE E PERSISTENZA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

# Inizializziamo lo stato se non esiste
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None

# Stile CSS
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; font-weight: bold; }
    .main-title { font-size: 3.5rem; font-weight: 800; color: #007BFF; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE UTENTI ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

# --- 3. LOGICA DI ACCESSO MIGLIORATA ---
def login_page():
    st.markdown('<p class="main-title">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Area Riservata Business</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Usiamo i widget con 'key' per permettere al browser di ricordarli (Autofill)
        u = st.text_input("Username", key="user_input")
        p = st.text_input("Password", type="password", key="pass_input")
        
        if st.button("Accedi"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.success("Accesso eseguito!")
                st.rerun()
            else:
                st.error("Credenziali errate")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 4. MOTORE IMMAGINI (DOWNLOAD DIRETTO PER EVITARE STAND-BY) ---
def genera_immagine_sicura(prompt_utente):
    api_key = "sk_ENpARXemZP1q6SuLX6Xc7fZW0BHOID6P_"
    seed = random.randint(1, 999999)
    prompt_hd = f"{prompt_utente}, cinematic photo, high resolution, 8k, photorealistic"
    prompt_encoded = urllib.parse.quote(prompt_hd)
    
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    try:
        # Timeout a 20 secondi per dare tempo al server di elaborare
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# --- 5. INTERFACCIA PRINCIPALE ---
with st.sidebar:
    st.title("RE-WIRE Panel")
    st.write(f"Connesso: **{st.session_state.user_role.upper()}**")
    
    # Il tasto Esci resetta tutto
    if st.button("Esci / Cambia Utente"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

st.header("✨ Generatore Creativo HD")
c_prompt = st.text_input("Descrivi cosa vuoi creare (es. un topo, un ufficio moderno, tegole)...")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine"):
        if c_prompt:
            with st.spinner("L'AI sta disegnando (attendi circa 10s)..."):
                img_data = genera_immagine_sicura(c_prompt)
                if img_data:
                    st.session_state.current_img_data = img_data
                else:
                    st.error("Il server è sovraccarico. Riprova tra 5 secondi.")
        else:
            st.warning("Inserisci una descrizione!")

# --- AREA VISUALIZZAZIONE ---
if st.session_state.current_img_data:
    st.image(st.session_state.current_img_data, use_container_width=True)
    st.download_button("💾 Scarica Progetto", st.session_state.current_img_data, "file.png", "image/png")
    if st.button("❌ Chiudi"):
        st.session_state.current_img_data = None
        st.rerun()

st.divider()

# --- 6. CHAT AI (GROQ) ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if p := st.chat_input("Chiedi aiuto per la tua strategia..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            compl = client.chat.completions.create(
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                model="llama-3.3-70b-versatile"
            )
            response = compl.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Errore Groq: {e}")
