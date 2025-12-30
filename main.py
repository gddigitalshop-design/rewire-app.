
import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #0056b3; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 10px; }
    .main-title { font-size: 3.5rem; font-weight: 800; color: #007BFF; text-align: center; margin-bottom: 0; }
    .subtitle { text-align: center; color: #8B949E; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO ---
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
    st.markdown('<p class="subtitle">L\'Intelligenza Artificiale per il tuo Business</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Accedi al Sistema"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali non valide")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. FUNZIONI TECNICHE ---
def genera_immagine(prompt_immagine):
    try:
        api_key = "sk_ENpARXemZP1q6SuLX6Xc7fZW0BHOID6P_"
        seed = random.randint(0, 9999999)
        prompt_pulito = urllib.parse.quote(prompt_immagine)
        # URL con SEED unico e AUTH per sbloccare i limiti
        url = f"https://image.pollinations.ai/prompt/{prompt_pulito}?width=1024&height=1024&nologo=true&seed={seed}&model=flux&auth={api_key}"
        return url
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("RE-WIRE Panel")
    st.write(f"Utente: **{st.session_state.user_role.upper()}**")
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    if st.button("🗑️ Svuota Tutto"):
        st.session_state.messages = []
        st.session_state.current_img = None
        st.session_state.current_template = None
        st.rerun()

    st.divider()
    file = st.file_uploader("Carica PDF", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"PDF: {testo[:3000]}"})
        st.success("PDF Analizzato!")

# --- 5. AREA PRINCIPALE ---
st.markdown(f"### Benvenuto, {st.session_state.user_role.capitalize()}")

st.header("✨ Generatore Creativo")
c_prompt = st.text_input("Descrivi cosa vuoi creare (es. tegole sarde, logo, piano marketing)...")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine"):
        if c_prompt:
            with st.spinner("Creazione immagine in corso..."):
                st.session_state.current_img = genera_immagine(c_prompt)
        else:
            st.warning("Inserisci una descrizione!")

with col2:
    if st.button("📝 Crea Template"):
        if c_prompt:
            with st.spinner("Generazione template..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Sei un esperto aziendale. Crea template chiari."},
                              {"role": "user", "content": f"Crea un template per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
        else:
            st.warning("Inserisci una descrizione!")

# --- AREA VISUALIZZAZIONE RISULTATI ---
if st.session_state.current_img:
    st.image(st.session_state.current_img, caption=f"Risultato: {c_prompt}")
    if st.button("❌ Chiudi Immagine"):
        st.session_state.current_img = None
        st.rerun()

if st.session_state.current_template:
    st.info("Template Generato:")
    st.markdown(st.session_state.current_template)
    if st.button("❌ Chiudi Template"):
        st.session_state.current_template = None
        st.rerun()

st.divider()

# --- 6. CHAT STORICA ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if p := st.chat_input("Chiedi un'analisi o una strategia..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
        response = compl.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
