import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# --- 2. DATABASE UTENTI ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

# --- 3. LOGICA DI ACCESSO AUTOMATICO (URL PARAMS) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# Controlla se ci sono credenziali nel link (URL)
query_params = st.query_params
url_user = query_params.get("user")
url_pass = query_params.get("pass")

if not st.session_state.logged_in:
    if url_user in USERS and USERS[url_user] == url_pass:
        st.session_state.logged_in = True
        st.session_state.user_role = url_user
        st.session_state.messages = [{"role": "system", "content": "Accesso rapido eseguito."}]

def login_screen():
    st.markdown('<p style="font-size:2.5rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE</p>', unsafe_allow_html=True)
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Accedi al Brain", use_container_width=True):
        if user in USERS and USERS[user] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = user
            st.session_state.messages = [{"role": "system", "content": "Sei RE-WIRE, partner di pensiero."}]
            st.rerun()
        else:
            st.error("Credenziali errate.")

# --- 4. CONTROLLO ACCESSO ---
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- 5. LOGOUT E UI ---
with st.sidebar:
    st.write(f"Connesso come: **{st.session_state.user_role}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        # Pulisce i parametri dall'URL al logout
        st.query_params.clear()
        st.rerun()
    st.divider()
    uploaded_file = st.file_uploader("Carica PDF", type="pdf")
    if uploaded_file:
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([page.extract_text() for page in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"PDF: {pdf_text[:4000]}"})
        st.success("Documento pronto!")

# --- 6. CORE CHAT (GROQ) ---
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
client = Groq(api_key=api_key)

# Visualizzazione messaggi
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Chiedimi quello che vuoi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
