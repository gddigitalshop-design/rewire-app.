import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# Design elegante
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ACCESSO UTENTI ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.messages = []

def login_page():
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E;">Business Intelligence & Strategic Partner</p>', unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Accedi", use_container_width=True):
        if u in USERS and USERS[u] == p:
            st.session_state.logged_in = True
            st.session_state.user_role = u
            st.rerun()
        else:
            st.error("Credenziali errate")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. FUNZIONE REPORT (MEMORIA) ---
def genera_report():
    testo = "REPORT DI CONSULENZA RE-WIRE\n\n"
    for m in st.session_state.messages:
        if m["role"] != "system":
            ruolo = "CLIENTE" if m["role"] == "user" else "RE-WIRE"
            testo += f"{ruolo}: {m['content']}\n\n"
    return testo

# --- 4. SIDEBAR (CARICAMENTO PDF) ---
with st.sidebar:
    st.markdown(f"Utente: **{st.session_state.user_role}**")
    
    # Bottone Download
    if len(st.session_state.messages) > 0:
        st.download_button(
            label="💾 Scarica Lavoro Svolto",
            data=genera_report(),
            file_name=f"consulenza_{st.session_state.user_role}.txt",
            mime="text/plain",
            use_container_width=True
        )

    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()
    st.markdown("### 📂 Analisi Documenti")
    file = st.file_uploader("Carica un PDF aziendale", type="pdf")
    
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        
        # Se il file è nuovo, lo mostra al centro della chat
        if "ultimo_file" not in st.session_state or st.session_state.ultimo_file != file.name:
            anteprima = testo_pdf[:1500]
            messaggio_auto = f"### ✅ Documento Analizzato: {file.name}\n\nHo letto il file. Ecco un estratto del contenuto:\n\n---\n{anteprima}...\n\n---\n**Cosa vuoi analizzare di questo documento?**"
            
            st.session_state.messages.append({"role": "assistant", "content": messaggio_auto})
            st.session_state.messages.append({"role": "system", "content": f"PDF CONTENT: {testo_pdf[:4000]}"})
            st.session_state.ultimo_file = file.name
            st.rerun()

# --- 5. CHAT CENTRALE ---
st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#007BFF;">RE-WIRE Business Brain</p>', unsafe_allow_html=True)

# Se non c'è ancora nulla, mostra istruzioni
if not [m for m in st.session_state.messages if m["role"] != "system"]:
    st.info("Benvenuto! Carica un PDF dalla barra laterale o scrivimi una domanda per iniziare.")

# Mostra i messaggi
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# Input Chat
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if prompt := st.chat_input("Chiedimi un'analisi strategica..."):
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
