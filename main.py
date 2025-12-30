import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse
import requests

# --- 1. ESTETICA E CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #0056b3; }
    .main-title { font-size: 3.5rem; font-weight: 800; color: #007BFF; text-align: center; margin-bottom: 0; }
    .subtitle { text-align: center; color: #8B949E; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN OBBLIGATORIO ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025",
    "test": "test2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.messages = []
    st.session_state.current_img = None
    st.session_state.current_template = None

def login_page():
    st.markdown('<p class="main-title">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Accedi per sbloccare le funzionalità AI</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Accedi al Sistema"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali non valide. Riprova.")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. MOTORE DI GENERAZIONE PROFESSIONALE ---
def genera_immagine(prompt_utente):
    # API KEY e parametri per bypassare i blocchi
    api_key = "sk_ENpARXemZP1q6SuLX6Xc7fZW0BHOID6P_"
    seed = random.randint(1, 1000000)
    
    # Rafforziamo il prompt per il massimo realismo
    prompt_hd = f"{prompt_utente}, cinematic photo, high resolution, 8k, professional lighting"
    prompt_encoded = urllib.parse.quote(prompt_hd)
    
    # Costruiamo l'URL usando il modello 'flux' che è il più potente
    url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&seed={seed}&model=flux&nologo=true&enhance=true"
    
    # Proviamo a validare l'immagine prima di passarla a Streamlit
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        # Aggiungiamo un parametro casuale per rompere la cache del server
        url_final = f"{url}&cache_bust={random.randint(1,999)}"
        return url_final
    except Exception:
        return url

# --- 4. BARRA LATERALE ---
with st.sidebar:
    st.title("RE-WIRE Panel")
    st.write(f"Utente attivo: **{st.session_state.user_role.upper()}**")
    
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    if st.button("🗑️ Svuota Sessione"):
        st.session_state.messages = []
        st.session_state.current_img = None
        st.session_state.current_template = None
        st.rerun()

    st.divider()
    file = st.file_uploader("Analizza PDF Aziendali", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"PDF: {testo[:3000]}"})
        st.success("Analisi PDF completata!")

# --- 5. INTERFACCIA PRINCIPALE ---
st.header("✨ Generatore Creativo Business")
c_prompt = st.text_input("Descrivi la tua idea (es: logo moderno, design prodotto, ecc.)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine HD"):
        if c_prompt:
            with st.spinner("L'AI sta creando l'immagine..."):
                # Reset preventivo per forzare il refresh del widget immagine
                st.session_state.current_img = None
                st.session_state.current_img = genera_immagine(c_prompt)
        else:
            st.warning("Scrivi prima cosa vuoi generare!")

with col2:
    if st.button("📝 Crea Template/Strategia"):
        if c_prompt:
            with st.spinner("Generazione testo..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sei un esperto aziendale. Crea template chiari."},
                              {"role": "user", "content": f"Crea un template per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
        else:
            st.warning("Descrivi il template necessario!")

# --- AREA DI VISUALIZZAZIONE ---
if st.session_state.current_img:
    st.markdown("---")
    # Mostriamo l'immagine forzando il caricamento
    st.image(st.session_state.current_img, caption=f"Risultato per: {c_prompt}", use_container_width=True)
    if st.button("🗑️ Rimuovi Immagine"):
        st.session_state.current_img = None
        st.rerun()

if st.session_state.current_template:
    st.info("Template Generato:")
    st.markdown(st.session_state.current_template)
    if st.button("🗑️ Rimuovi Template"):
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
        compl = client.chat.completions.create(
            messages=st.session_state.messages, 
            model="llama-3.3-70b-versatile"
        )
        response = compl.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
