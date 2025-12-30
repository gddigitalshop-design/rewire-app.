import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse

# --- 1. CONFIGURAZIONE E STILE ---
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

# --- 2. GESTIONE ACCESSO (LOGIN OBBLIGATORIO) ---
# Fondamentale per vendere o affittare l'app
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
    st.markdown('<p class="subtitle">Accesso Riservato ai Partner</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sblocca Sistema"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali Errate. Accesso Negato.")

# Se non è loggato, ferma tutto qui e mostra solo il login
if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. MOTORE GENERAZIONE IMMAGINI (RISOLTO) ---
def genera_immagine(prompt_utente):
    # Tua chiave API per sbloccare i limiti
    api_key = "sk_ENpARXemZP1q6SuLX6Xc7fZW0BHOID6P_"
    
    # Rendiamo il prompt professionale per forzare l'alta qualità
    prompt_hd = f"{prompt_utente}, highly detailed, 8k, photorealistic, cinematic lighting"
    prompt_encoded = urllib.parse.quote(prompt_hd)
    
    # SEED casuale enorme per forzare il server a NON usare la vecchia immagine
    seed = random.randint(1, 999999999)
    
    # Costruzione URL con parametri di sblocco e qualità Flux
    url = (f"https://image.pollinations.ai/prompt/{prompt_encoded}"
           f"?width=1024&height=1024&seed={seed}&model=flux"
           f"&nologo=true&enhance=true&auth={api_key}")
    return url

# --- 4. SIDEBAR (PANNELLO DI CONTROLLO) ---
with st.sidebar:
    st.title("RE-WIRE Panel")
    st.write(f"Connesso come: **{st.session_state.user_role.upper()}**")
    
    if st.button("Esci dal Sistema"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    if st.button("🗑️ Svuota Sessione"):
        st.session_state.messages = []
        st.session_state.current_img = None
        st.session_state.current_template = None
        st.rerun()

    st.divider()
    file = st.file_uploader("Analisi Documenti PDF", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"PDF: {testo[:3000]}"})
        st.success("Documento pronto per l'analisi!")

# --- 5. AREA DI LAVORO PRINCIPALE ---
st.header("✨ Generatore Creativo Business")
c_prompt = st.text_input("Cosa desideri creare? (Es: Design prodotto, Template fattura, Logo)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Visual HD"):
        if c_prompt:
            with st.spinner("L'AI sta disegnando..."):
                st.session_state.current_img = genera_immagine(c_prompt)
        else:
            st.warning("Descrivi l'immagine!")

with col2:
    if st.button("📝 Genera Strategia/Template"):
        if c_prompt:
            with st.spinner("Elaborazione in corso..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sei un consulente business. Crea template Markdown."},
                              {"role": "user", "content": f"Crea per me: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
        else:
            st.warning("Descrivi cosa ti serve!")

# --- VISUALIZZAZIONE RISULTATI (FISSA E PULITA) ---
if st.session_state.current_img:
    st.image(st.session_state.current_img, caption=f"Anteprima: {c_prompt}", use_container_width=True)
    if st.button("🗑️ Rimuovi Immagine"):
        st.session_state.current_img = None
        st.rerun()

if st.session_state.current_template:
    st.info("Documento Generato:")
    st.markdown(st.session_state.current_template)
    if st.button("🗑️ Rimuovi Testo"):
        st.session_state.current_template = None
        st.rerun()

st.divider()

# --- 6. BUSINESS CHAT STORICA ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if p := st.chat_input("Fai una domanda alla tua AI..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
        response = compl.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
