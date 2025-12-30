import streamlit as st
from groq import Groq
import PyPDF2

# 1. Configurazione iniziale (DEVE essere la prima istruzione Streamlit)
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# 2. Inizializzazione Session State (Gestione memoria e accesso)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Database Utenti
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

# 4. LOGICA LINK MAGICO (Legge i dati dall'URL)
# Questo permette di entrare direttamente con il link speciale
query_params = st.query_params
url_user = query_params.get("user")
url_pass = query_params.get("pass")

if not st.session_state.logged_in:
    if url_user in USERS and USERS[url_user] == url_pass:
        st.session_state.logged_in = True
        st.session_state.user_role = url_user

# 5. SCHERMATA DI LOGIN (Se non loggato e link magico assente)
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

# --- DA QUI IN POI L'APP È ATTIVA ---

# 6. FUNZIONE REPORT
def genera_report():
    testo = "REPORT DI CONSULENZA RE-WIRE\n\n"
    for m in st.session_state.messages:
        if m["role"] != "system":
            ruolo = "CLIENTE" if m["role"] == "user" else "RE-WIRE"
            testo += f"{ruolo}: {m['content']}\n\n"
    return testo

# 7. SIDEBAR
with st.sidebar:
    st.markdown(f"Utente: **{st.session_state.user_role}**")
    if len(st.session_state.messages) > 0:
        st.download_button("💾 Scarica Lavoro", genera_report(), f"report_{st.session_state.user_role}.txt", use_container_width=True)
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()
    st.markdown("### 📂 Analisi PDF")
    file = st.file_uploader("Carica un PDF", type="pdf")
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        if "ultimo_file" not in st.session_state or st.session_state.ultimo_file != file.name:
            st.session_state.messages.append({"role": "assistant", "content": f"✅ **File analizzato:** {file.name}\n\n{testo_pdf[:1000]}..."})
            st.session_state.messages.append({"role": "system", "content": f"CONTESTO PDF: {testo_pdf[:4000]}"})
            st.session_state.ultimo_file = file.name
            st.rerun()

# 8. CHAT PRINCIPALE
st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#007BFF;">RE-WIRE Business Brain</p>', unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Chiedimi un'analisi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("Errore: Chiave API mancante nei Secrets!")
    else:
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            compl = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
            resp = compl.choices[0].message.content
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
