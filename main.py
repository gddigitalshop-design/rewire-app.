import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# CSS Personalizzato per un look Premium
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; height: 3em; background-color: #007BFF; color: white; border: none; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE UTENTI (Qui aggiungerai i tuoi clienti) ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

# --- 3. GESTIONE ACCESSO ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.messages = []

# Controllo link magico (per la comodità del cliente)
q = st.query_params
if not st.session_state.logged_in and q.get("user") in USERS and USERS[q.get("user")] == q.get("pass"):
    st.session_state.logged_in = True
    st.session_state.user_role = q.get("user")

def login_page():
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#007BFF; text-align:center; margin-bottom:0;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E; margin-bottom:2rem;">Business Intelligence & Strategic Partner</p>', unsafe_allow_html=True)
    
    with st.container():
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Entra nel Brain", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali non valide")

if not st.session_state.logged_in:
    login_page()
    st.stop()# --- TITOLO SEMPRE VISIBILE IN ALTO ---
st.markdown('<p style="font-size:2rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE Business Brain</p>', unsafe_allow_html=True)
st.divider() # Aggiunge una linea sottile di separazione

# --- 4. LOGICA DOWNLOAD REPORT (La "Memoria" per il cliente) ---
def genera_report():
    testo = f"REPORT DI CONSULENZA RE-WIRE\nUtente: {st.session_state.user_role}\n------------------------------\n\n"
    for m in st.session_state.messages:
        ruolo = "IO" if m["role"] == "user" else "RE-WIRE"
        testo += f"{ruolo}: {m['content']}\n\n"
    return testo

# --- 5. INTERFACCIA PRINCIPALE ---
with st.sidebar:
    st.markdown(f"### Benvenuto, **{st.session_state.user_role}**")
    
    # TASTO DOWNLOAD (Appare solo se c'è una chat)
    if len(st.session_state.messages) > 0:
        st.download_button(
            label="📄 Scarica Report Consulenza",
            data=genera_report(),
            file_name=f"consulenza_rewire_{st.session_state.user_role}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    if st.button("Chiudi Sessione (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.query_params.clear()
        st.rerun()

    st.divider()
    st.markdown("### 📂 Analisi Documenti")
    file = st.file_uploader("Carica bilanci o PDF aziendali", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"DOCUMENTO CARICATO: {testo_pdf[:4000]}"})
        st.success("Analisi completata!")

# --- 6. CHAT CORE ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Di cosa vogliamo discutere oggi?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        compl = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        resp = compl.choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})

