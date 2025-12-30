import streamlit as st
from groq import Groq
import PyPDF2
from extra_streamlit_components import CookieManager

# --- 1. INIZIALIZZAZIONE COOKIE ---
# Il CookieManager deve essere chiamato all'inizio
cookie_manager = CookieManager()

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# --- 3. DATABASE UTENTI ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

# --- 4. GESTIONE LOGICA ACCESSO ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# Recupera il cookie se esiste
saved_user = cookie_manager.get(cookie="rewire_user_session")

if saved_user in USERS and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_role = saved_user
    st.session_state.messages = [{"role": "system", "content": "Bentornato in RE-WIRE."}]

def login_screen():
    st.markdown('<p style="font-size:2.5rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE</p>', unsafe_allow_html=True)
    
    with st.container():
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Rimani connesso (30 giorni)")
        
        if st.button("Accedi al Brain", use_container_width=True):
            if user in USERS and USERS[user] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = user
                st.session_state.messages = [{"role": "system", "content": "Sei RE-WIRE, partner di pensiero."}]
                
                if remember_me:
                    # Salva il cookie per 30 giorni
                    cookie_manager.set("rewire_user_session", user, key="set_cookie")
                
                st.rerun()
            else:
                st.error("Credenziali errate.")

# --- 5. CONTROLLO ACCESSO ---
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- 6. DESIGN E INTERFACCIA (Dopo il Login) ---
st.markdown(f'<p style="font-size:1.5rem; font-weight:800; color:#007BFF;">RE-WIRE Brain | {st.session_state.user_role.upper()}</p>', unsafe_allow_html=True)

# CSS per il look scuro
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stChatMessage { background-color: #161B22; border-radius: 20px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# --- 7. CONNESSIONE GROQ ---
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
client = Groq(api_key=api_key)

# SIDEBAR
with st.sidebar:
    st.write(f"Utente: **{st.session_state.user_role}**")
    if st.button("Logout ed Esci"):
        cookie_manager.delete("rewire_user_session")
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("Carica PDF", type="pdf")
    if uploaded_file:
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([page.extract_text() for page in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"PDF: {pdf_text[:4000]}"})
        st.success("Documento pronto!")

# VISUALIZZAZIONE E INPUT CHAT
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
