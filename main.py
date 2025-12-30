import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="centered")

# CSS Professionale
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- UTENTI (Aggiungine altri qui per affittare l'app) ---
USERS = {
    "admin": "tuapassword123",
    "cliente_test": "rewire2025"
}

# --- STATO SESSIONE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.messages = []

# --- LOGIN ---
def login():
    st.title("🚀 RE-WIRE LOGIN")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if u in USERS and USERS[u] == p:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenziali errate")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- FUNZIONI CORE ---
def genera_immagine(prompt):
    seed = random.randint(0, 999999)
    prompt_enc = urllib.parse.quote(prompt)
    # Usiamo il modello Flux per massima precisione (foglie di fico vs uva)
    url = f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
    return url

# --- SIDEBAR ---
with st.sidebar:
    st.title("RE-WIRE Panel")
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    file = st.file_uploader("Analizza Documento (PDF)", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"Dati PDF: {testo[:3000]}"})
        st.success("PDF Analizzato!")

# --- INTERFACCIA PRINCIPALE ---
st.header("✨ Generatore Creativo")
c_prompt = st.text_input("Cosa vuoi creare? (Immagine o Template)")

col1, col2 = st.columns(2)
with col1:
    if st.button("🖼️ Genera Immagine"):
        img_url = genera_immagine(c_prompt)
        st.image(img_url, caption=c_prompt)
        st.session_state.messages.append({"role": "assistant", "content": f"Immagine creata: {img_url}"})

with col2:
    if st.button("📝 Crea Template"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Crea un template professionale per: {c_prompt}"}],
            model="llama-3.3-70b-versatile"
        )
        st.markdown(res.choices[0].message.content)

st.divider()

# --- CHAT ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Chiedi analisi..."):
    st.session_state.messages.append({"role": "user", "content": p})
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    res = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
    st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
    st.rerun()
