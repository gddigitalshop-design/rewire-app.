import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# --- 2. DATABASE UTENTI (Configurazione per affitto) ---
# Qui puoi aggiungere i tuoi clienti. Ognuno avrà la sua password.
USERS = {
    "admin": "tuapassword123",      # La tua password personale
    "cliente1": "rewire2025",       # Password per il primo cliente
    "ospite": "businessbrain"       # Una per i test
}

# --- 3. LOGICA DI ACCESSO E PRIVACY ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

def login_screen():
    st.markdown("""
        <style>
        .stApp { background-color: #0B0E11; color: #E9ECEF; }
        .login-box { padding: 30px; border-radius: 15px; border: 1px solid #30363D; background-color: #161B22; }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('<p style="font-size:2.5rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E;">Inserisci le tue credenziali per accedere al tuo socio digitale.</p>', unsafe_allow_html=True)
    
    with st.container():
        user = st.text_input("Username", placeholder="Inserisci username")
        password = st.text_input("Password", type="password", placeholder="Inserisci password")
        
        if st.button("Accedi al Brain", use_container_width=True):
            if user in USERS and USERS[user] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = user
                # Inizializza la memoria SOLO per questa sessione specifica
                st.session_state.messages = [{"role": "system", "content": "Sei RE-WIRE, un partner di pensiero empatico e professionale. Dai del TU e aiuta l'utente nel suo business."}]
                st.rerun()
            else:
                st.error("Credenziali errate o accesso non autorizzato.")

# --- 4. CONTROLLO ACCESSO ---
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- 5. DESIGN DARK MODERNO (Solo dopo il login) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stChatMessage { background-color: #161B22; border-radius: 20px; padding: 15px; margin-bottom: 15px; border: 1px solid #30363D; }
    [data-testid="stChatMessageUser"] { background-color: #1F2937; border: 1px solid #007BFF; }
    .main-title { font-size: 2rem; font-weight: 800; background: -webkit-linear-gradient(#007BFF, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. CONVERSIONE API E CORE ---
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
client = Groq(api_key=api_key)

# --- 7. INTERFACCIA APP ---
st.markdown(f'<p class="main-title">RE-WIRE Brain | {st.session_state.user_role.upper()}</p>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_role.capitalize()}")
    st.caption("Ogni conversazione è privata e sicura.")
    
    st.divider()
    st.markdown("### 📄 Carica PDF")
    uploaded_file = st.file_uploader("Analizza un documento", type="pdf")
    
    if uploaded_file:
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "".join([page.extract_text() for page in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"DOCUMENTO CARICATO: {pdf_text[:5000]}"})
        st.success("PDF Analizzato!")

    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# VISUALIZZAZIONE CHAT
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# INPUT CHAT
if prompt := st.chat_input("Di cosa parliamo oggi?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
            temperature=0.8
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
